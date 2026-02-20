import logging
from typing import Literal, Optional
from pydantic import BaseModel, Field
from src.core.state import AgentState
from src.core.llm import get_llm
from src.core.models import FindingStatus, Severity
from src.config import settings
from src.tools.file_reader import read_code_segment

logger = logging.getLogger(settings.APP_NAME)

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
            # First Pass: Give it the tiny Semgrep snippet
            prompt = f"""
                Analyze this static analysis finding.
                Vulnerability: {finding.vuln_type}
                File: {finding.file_path}:{finding.line_number}
                Code Snippet:
                {finding.code_snippet}
            """
            result = structured_llm.invoke(prompt)
            
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
                prompt += f"\n\nYou requested more context. Here is the expanded file segment:\n{extra_context}\n\nNow, you MUST choose DECIDE."
                result = structured_llm.invoke(prompt)
                
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