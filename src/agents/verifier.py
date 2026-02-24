import logging
from typing import Literal, Optional
from pydantic import BaseModel, Field
from src.core.state import AgentState
from src.core.llm import get_llm
from src.core.models import FindingStatus, Severity
from src.config import settings
from src.tools.file_reader import read_code_segment
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

# --- 1. Define strict output schema ---
class VerificationResult(BaseModel):
    """
    The LLM can either make a decision OR ask to read more code.
    """
    
    action: Literal["DECIDE", "READ_MORE_CODE"] = Field(..., description="Choose DECIDE if you have enough info. Choose READ_MORE_CODE if you need to see surrounding lines to check for sanitization.")
    
    # Fields for when action == "DECIDE"
    is_true_positive: bool = Field(..., description="True if real risk, False if safe.")
    confidence: float = Field(..., description="0.0 to 1.0 confidence score.")
    reasoning: str = Field(..., description="Why is it safe or unsafe?")
    fix_suggestion: str = Field(..., description="Code or logic to fix it.")
    
    # Fields for when action == "READ_MORE_CODE"
    start_line: Optional[int] = Field(None, description="Line number to start reading from.")
    end_line: Optional[int] = Field(None, description="Line number to stop reading.")

def verify_findings_node(state: AgentState) -> dict:
    """
    Node 2: Verifier Agent.
    
    1. Reviews raw findings from the Scanner.
    2. Uses Structured Outputs (JSON) to force the LLM to give a confidence score (0.0-1.0).
    3. Filters out False Positives and suggests fixes for real bugs.
    """
    
    findings = state.get("findings", [])
    repo_path = state.get("repo_path", "unknown")
    verified_list = []
    
    if not findings:
        return {"verified_findings": []}

    llm = get_llm()
    # Force JSON Output
    structured_llm = llm.with_structured_output(VerificationResult)

    logger.info(f"[Verifier] Reviewing {len(findings)} findings...")

    for finding in findings:
        if finding.severity not in [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM]:
            finding.status = FindingStatus.UNVERIFIED
            verified_list.append(finding)
            continue

        try:
            # First Pass: Enhanced prompt with CoT framework + Few-Shot context
            finding_prompt = f"""Analyze the following static analysis finding using your security analysis framework.

**Reported Vulnerability Type:** {finding.vuln_type}
**File:** {finding.file_path}:{finding.line_number}
**Code Snippet:**
```
{finding.code_snippet}
```

Follow your 4-step analysis framework:
1. Identify the data source and data sink (the taint path)
2. Check for any sanitization, validation, or defensive coding
3. Map to the relevant CWE vulnerability class
4. Provide your verdict with confidence score, detailed reasoning, and a specific fix suggestion

If you need to see more surrounding code to check for sanitization or context, choose READ_MORE_CODE and specify the line range. Otherwise, choose DECIDE."""
            messages = [
                SystemMessage(content=SECURITY_EXPERT_SYSTEM_PROMPT),
                HumanMessage(content=finding_prompt)
            ]
            result = structured_llm.invoke(messages)
            
            # AGENT LOOP: Did the LLM decide to use its "Hand"?
            if result.action == "READ_MORE_CODE" and result.start_line:
                logger.info(f"[Verifier] LLM requested more context for {finding.file_path} (lines {result.start_line}-{result.end_line})")
                
                # Fetch the surrounding code
                extra_context = read_code_segment(
                    repo_root=repo_path, 
                    file_path=finding.file_path, 
                    start_line=result.start_line, 
                    end_line=result.end_line
                )
                
                # Second Pass: Feed the new context and force a decision
                logger.info(f"[Verifier] Re-evaluating with expanded context...")
                followup_prompt = f"""{finding_prompt}

--- ADDITIONAL CONTEXT (You requested this) ---
{extra_context}
---

You now have the expanded context. You MUST choose DECIDE and provide your final verdict following the 4-step framework."""
                messages = [
                    SystemMessage(content=SECURITY_EXPERT_SYSTEM_PROMPT),
                    HumanMessage(content=followup_prompt)
                ]
                result = structured_llm.invoke(messages)
                
            # Final Record Keeping
            if result.action == "DECIDE":
                finding.confidence_score = result.confidence if result.confidence else 0.0
                finding.description += f" [AI Reason: {result.reasoning}]"

                if result.is_true_positive:
                    finding.status = FindingStatus.TRUE_POSITIVE
                    finding.remediation = result.fix_suggestion
                else:
                    finding.status = FindingStatus.FALSE_POSITIVE
            else:
                 finding.status = FindingStatus.NEEDS_REVIEW
        except Exception as e:
            logger.error(f"[Verifier] Failed on {finding.id}: {e}")
            finding.status = FindingStatus.NEEDS_REVIEW
        
        verified_list.append(finding)

    return {"verified_findings": verified_list}