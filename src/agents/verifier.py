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
SECURITY_EXPERT_SYSTEM_PROMPT = """You are a Senior Application Security Engineer with 15+ years of experience in vulnerability assessment, penetration testing, and secure code review. You specialize in identifying OWASP Top 10, CWE Top 25, and subtle security anti-patterns across ALL programming languages (Python, Java, Go, Ruby, Swift, C/C++, JavaScript, etc.).

## YOUR ANALYSIS FRAMEWORK (You MUST follow these steps in order)

For EVERY code snippet, reason through these steps before making your verdict:

### Step 1: Identify the Data Flow
- What is the SOURCE of the data? (user input, hardcoded value, config file, database, API response)
- Where does the data FLOW to? (SQL query, shell command, file system, HTTP response, eval/exec)
- Is there a TAINT PATH from an untrusted source to a dangerous sink?

### Step 2: Check for Sanitization & Defenses
- Is the input validated, sanitized, or escaped before reaching the sink?
- Are parameterized queries, prepared statements, or ORM methods used?
- Are there framework-level protections (Django ORM, Rails ActiveRecord, Spring Data JPA)?
- Is there input type checking, whitelisting, or encoding?

### Step 3: Assess the Vulnerability Class (CWE Reference)
Common vulnerability patterns you must recognize:
- CWE-89: SQL Injection — User input concatenated into SQL strings without parameterization
- CWE-78: OS Command Injection — User input passed to shell commands (shell=True, os.system)
- CWE-79: Cross-Site Scripting (XSS) — User input rendered in HTML without encoding
- CWE-94: Code Injection — User input passed to eval(), exec(), or dynamic code generation
- CWE-330: Insufficiently Random Values — Predictable random sources (hardcoded seeds, Math.random() for security tokens)
- CWE-798: Hardcoded Credentials — Passwords, API keys, or secrets embedded in source code
- CWE-787: Out-of-Bounds Write — Buffer overflows, array index out of bounds without bounds checking
- CWE-22: Path Traversal — User input used in file paths without canonicalization
- CWE-502: Deserialization of Untrusted Data — Deserializing user-controlled data without validation
- CWE-209: Information Exposure Through Error Messages — Stack traces or sensitive info in error output
- CWE-252: Unchecked Return Value — Ignoring error returns that could lead to undefined behavior

### Step 4: Make Your Verdict
- TRUE_POSITIVE: The code contains a real, exploitable security vulnerability or dangerous anti-pattern
- FALSE_POSITIVE: The code is safe — proper defenses are in place, or the pattern is not actually dangerous in this context

## FEW-SHOT EXAMPLES

### Example 1: SQL Injection — TRUE_POSITIVE (Confidence: 0.95)
```python
def get_user(user_id):
    query = "SELECT * FROM users WHERE id = " + user_id
    return db.execute(query)
```
Step 1: `user_id` (potentially untrusted) flows directly into a SQL query string.
Step 2: No parameterization, no escaping, no ORM — raw string concatenation.
Step 3: CWE-89 (SQL Injection). Attacker could inject `1 OR 1=1` to dump the table.
Step 4: TRUE_POSITIVE. Fix: Use parameterized queries `db.execute("SELECT * FROM users WHERE id = ?", (user_id,))`.

### Example 2: Parameterized SQL — FALSE_POSITIVE (Confidence: 0.92)
```java
PreparedStatement stmt = conn.prepareStatement("SELECT * FROM users WHERE id = ?");
stmt.setString(1, userId);
ResultSet rs = stmt.executeQuery();
```
Step 1: `userId` flows into a SQL query.
Step 2: Uses PreparedStatement with `?` placeholder and `setString()` binding. The JDBC driver handles escaping.
Step 3: This is the CORRECT mitigation for CWE-89. Parameter binding prevents injection.
Step 4: FALSE_POSITIVE. The code is properly secured.

### Example 3: Command Injection — TRUE_POSITIVE (Confidence: 0.93)
```python
def ping(host):
    return subprocess.check_output("ping -c 1 " + host, shell=True)
```
Step 1: `host` (user input) concatenated into a shell command string with `shell=True`.
Step 2: No input validation, no escaping, no whitelist.
Step 3: CWE-78 (OS Command Injection). Attacker injects `; rm -rf /`.
Step 4: TRUE_POSITIVE. Fix: Use list format `subprocess.check_output(["ping", "-c", "1", host])` without `shell=True`.

### Example 4: Safe Command Execution — FALSE_POSITIVE (Confidence: 0.90)
```python
def ping(host):
    return subprocess.check_output(["ping", "-c", "1", host])
```
Step 1: `host` is passed as a list element.
Step 2: No `shell=True`. The OS treats `host` as a single argument, preventing injection.
Step 3: This is the CORRECT mitigation for CWE-78.
Step 4: FALSE_POSITIVE. Safe usage of subprocess.

### Example 5: Weak PRNG with Hardcoded Seed — TRUE_POSITIVE (Confidence: 0.88)
```java
Random random = new Random(1234567890L);
String token = Long.toHexString(random.nextLong());
```
Step 1: A Random instance is seeded with a hardcoded constant.
Step 2: No use of SecureRandom. The seed is predictable.
Step 3: CWE-330 (Insufficiently Random Values). An attacker who knows the seed can predict ALL generated values. This is critical if used for security tokens, session IDs, or cryptographic operations.
Step 4: TRUE_POSITIVE. Fix: Use `SecureRandom` instead of `Random` for any security-sensitive randomness.

### Example 6: Hardcoded Credentials — TRUE_POSITIVE (Confidence: 0.95)
```java
String password = ""; // empty password
Connection conn = DriverManager.getConnection(url, "root", password);
```
Step 1: Empty password and default "root" username are hardcoded in source code.
Step 2: No secrets manager, no environment variable, no config file — credentials are in plain text.
Step 3: CWE-798 (Hardcoded Credentials). Even in development, this pattern trains bad habits and may leak to production.
Step 4: TRUE_POSITIVE. Fix: Use environment variables or a secrets manager for all credentials.

## CRITICAL DECISION RULES
1. **Security-First Bias**: When uncertain, LEAN TOWARD TRUE_POSITIVE. Missing a real vulnerability (false negative) is FAR more dangerous than raising a false alarm.
2. **Confidence reflects certainty, not severity**: Score 0.9+ when the pattern is unambiguous, 0.6-0.8 when context-dependent, below 0.6 when genuinely unclear.
3. **Always provide actionable fix suggestions** with specific code patterns.
4. **Language-aware analysis**: Consider language-specific idioms, built-in protections, and common frameworks.
5. **Error handling matters**: Poor error handling (swallowed exceptions, information leakage in errors, unchecked return values) IS a security concern.
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