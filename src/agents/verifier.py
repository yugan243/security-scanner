import logging
from typing import List
from pydantic import BaseModel, Field
from src.core.state import AgentState
from src.core.llm import get_llm
from src.core.models import FindingStatus, Severity
from src.config import settings
from langchain_core.messages import SystemMessage, HumanMessage

logger = logging.getLogger(settings.APP_NAME)

# ================================================================================
# STRATEGY 1: Enhanced System Prompt with Chain-of-Thought (CoT) Reasoning
# STRATEGY 2: Few-Shot Examples for calibrating the LLM's decision boundary
# ================================================================================
SECURITY_EXPERT_SYSTEM_PROMPT = """You are a Senior Application Security Engineer. Analyze code for OWASP Top 10, CWE Top 25, and security anti-patterns across all languages.

## ANALYSIS FRAMEWORK (Follow in order)
1. **Data Flow**: SOURCE (user input, hardcoded, config) → SINK (SQL, shell, eval, HTTP response). Is there a taint path?
2. **Defenses**: Any sanitization, parameterized queries, prepared statements, ORM, whitelisting, or encoding?
3. **CWE Class**: Map to the relevant CWE:
   - CWE-89: SQL Injection (input in SQL without parameterization)
   - CWE-78: Command Injection (input in shell commands)
   - CWE-79: XSS (input in HTML without encoding)
   - CWE-94: Code Injection (input in eval/exec)
   - CWE-330: Weak Randomness (hardcoded seeds, predictable PRNG)
   - CWE-798: Hardcoded Credentials (passwords/keys in source)
   - CWE-787: Out-of-Bounds Write (buffer overflow, unchecked indices)
   - CWE-22: Path Traversal | CWE-502: Insecure Deserialization
   - CWE-209: Error Info Leak | CWE-252: Unchecked Return Value
4. **Verdict**: TRUE_POSITIVE (real vulnerability) or FALSE_POSITIVE (safe code)

## EXAMPLES

### SQL Injection — TRUE_POSITIVE (0.95)
`query = "SELECT * FROM users WHERE id = " + user_id` → No parameterization, CWE-89. Fix: use `?` binding.

### Parameterized SQL — FALSE_POSITIVE (0.92)
`PreparedStatement stmt = conn.prepareStatement("SELECT * FROM users WHERE id = ?"); stmt.setString(1, userId);` → Parameter binding prevents injection. SAFE.

### Weak PRNG — TRUE_POSITIVE (0.88)
`Random random = new Random(1234567890L);` → Hardcoded seed, predictable output. CWE-330. Fix: use `SecureRandom`.

### Hardcoded Credentials — TRUE_POSITIVE (0.95)
`Connection conn = DriverManager.getConnection(url, "root", "");` → Empty password hardcoded, CWE-798. Fix: use env vars.

## RULES
1. **When uncertain, LEAN TOWARD TRUE_POSITIVE.** Missing a real vulnerability is worse than a false alarm.
2. Confidence: 0.9+ = unambiguous, 0.6-0.8 = context-dependent, <0.6 = unclear.
3. Always provide specific, actionable fix suggestions.
4. Poor error handling (swallowed exceptions, info leakage) IS a security concern.
"""

# ================================================================================
# BATCH VERIFICATION: Send multiple findings per LLM call to save tokens & time
# System prompt (~850 tokens) is sent ONCE per batch instead of once per finding
# ================================================================================
VERIFICATION_BATCH_SIZE = 10

# ================================================================================
# CONFIDENCE THRESHOLD: Override uncertain FALSE_POSITIVE verdicts
# If the LLM says "safe" but isn't confident enough, treat it as TRUE_POSITIVE
# This catches missed threats (False Negatives) at zero extra token cost
# ================================================================================
CONFIDENCE_THRESHOLD = 0.7  # FP verdicts below this confidence get overridden

# --- Structured Output Schemas ---
class FindingVerdict(BaseModel):
    """Verdict for a single finding within a batch."""
    finding_id: str = Field(..., description="The ID of the finding being evaluated")
    is_true_positive: bool = Field(..., description="True if real risk, False if safe.")
    confidence: float = Field(..., description="0.0 to 1.0 confidence score.")
    reasoning: str = Field(..., description="Brief explanation: why is it safe or unsafe?")
    fix_suggestion: str = Field(..., description="How to fix it, or 'N/A' if safe.")

class BatchVerificationResult(BaseModel):
    """Batch verification results for multiple findings."""
    verdicts: List[FindingVerdict] = Field(..., description="One verdict per finding, matching the IDs from the input.")

def verify_findings_node(state: AgentState) -> dict:
    """
    Node 2: Verifier Agent (Batch Mode).
    
    1. Groups raw findings into batches of VERIFICATION_BATCH_SIZE.
    2. Sends each batch as a SINGLE LLM call (amortizing the system prompt cost).
    3. Parses batch results back to individual findings.
    """
    
    findings = state.get("findings", [])
    repo_path = state.get("repo_path", "unknown")
    verified_list = []
    
    if not findings:
        return {"verified_findings": []}

    # Separate findings by severity — only verify CRITICAL/HIGH/MEDIUM
    to_verify = []
    for finding in findings:
        if finding.severity not in [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM]:
            finding.status = FindingStatus.UNVERIFIED
            verified_list.append(finding)
        else:
            to_verify.append(finding)
    
    if not to_verify:
        return {"verified_findings": verified_list}

    llm = get_llm()
    structured_llm = llm.with_structured_output(BatchVerificationResult)

    total_batches = (len(to_verify) + VERIFICATION_BATCH_SIZE - 1) // VERIFICATION_BATCH_SIZE
    logger.info(f"[Verifier] Reviewing {len(to_verify)} findings in {total_batches} batch(es) of {VERIFICATION_BATCH_SIZE}...")

    for batch_idx in range(0, len(to_verify), VERIFICATION_BATCH_SIZE):
        batch = to_verify[batch_idx:batch_idx + VERIFICATION_BATCH_SIZE]
        batch_num = (batch_idx // VERIFICATION_BATCH_SIZE) + 1
        
        # Format all findings in this batch into a single prompt
        findings_text = ""
        for idx, f in enumerate(batch, 1):
            findings_text += f"""
--- Finding {idx} (ID: {f.id}) ---
Type: {f.vuln_type}
File: {f.file_path}:{f.line_number}
Code:
```
{f.code_snippet}
```
"""
        
        batch_prompt = f"""Analyze the following {len(batch)} static analysis finding(s). For EACH finding, apply the 4-step analysis framework and provide a verdict.

{findings_text}
You MUST provide exactly {len(batch)} verdict(s), one for each finding ID listed above."""

        try:
            logger.info(f"[Verifier] Processing batch {batch_num}/{total_batches} ({len(batch)} findings)...")
            messages = [
                SystemMessage(content=SECURITY_EXPERT_SYSTEM_PROMPT),
                HumanMessage(content=batch_prompt)
            ]
            result = structured_llm.invoke(messages)
            
            # Map results back to findings by ID
            verdict_map = {v.finding_id: v for v in result.verdicts}
            
            for finding in batch:
                verdict = verdict_map.get(finding.id)
                if verdict:
                    finding.confidence_score = verdict.confidence if verdict.confidence else 0.0
                    finding.description += f" [AI Reason: {verdict.reasoning}]"
                    if verdict.is_true_positive:
                        finding.status = FindingStatus.TRUE_POSITIVE
                        finding.remediation = verdict.fix_suggestion
                    else:
                        # CONFIDENCE THRESHOLD: Override uncertain "safe" verdicts
                        # If the LLM says FALSE_POSITIVE but isn't confident, flag it as TRUE_POSITIVE
                        if finding.confidence_score < CONFIDENCE_THRESHOLD:
                            logger.warning(
                                f"[Verifier] Confidence override: {finding.id} marked FP with confidence "
                                f"{finding.confidence_score:.2f} < {CONFIDENCE_THRESHOLD} → overriding to TP"
                            )
                            finding.status = FindingStatus.TRUE_POSITIVE
                            finding.remediation = verdict.fix_suggestion or "Low-confidence dismissal overridden. Manual review recommended."
                        else:
                            finding.status = FindingStatus.FALSE_POSITIVE
                else:
                    # LLM didn't return a verdict for this finding
                    logger.warning(f"[Verifier] No verdict returned for {finding.id}")
                    finding.status = FindingStatus.NEEDS_REVIEW
                
                verified_list.append(finding)
                
        except Exception as e:
            logger.error(f"[Verifier] Batch {batch_num} failed: {e}")
            for finding in batch:
                finding.status = FindingStatus.NEEDS_REVIEW
                verified_list.append(finding)

    return {"verified_findings": verified_list}