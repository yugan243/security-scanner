import logging
from pydantic import BaseModel, Field
from src.core.state import AgentState
from src.core.llm import get_llm
from src.core.models import FindingStatus, Severity
from src.config import settings

logger = logging.getLogger(settings.APP_NAME)

# --- 1. Define strict output schema ---
class VerificationResult(BaseModel):
    is_true_positive: bool = Field(..., description="True if real risk, False if safe.")
    confidence: float = Field(..., description="0.0 to 1.0 confidence score.")
    reasoning: str = Field(..., description="Why is it safe or unsafe?")
    fix_suggestion: str = Field(..., description="Code or logic to fix it.")

def verify_findings_node(state: AgentState) -> dict:
    """
    Node 2: Verifier Agent.
    
    1. Reviews raw findings from the Scanner.
    2. Uses Structured Outputs (JSON) to force the LLM to give a confidence score (0.0-1.0).
    3. Filters out False Positives and suggests fixes for real bugs.
    """
    
    findings = state.get("findings", [])
    verified_list = []
    
    if not findings:
        return {"verified_findings": []}

    llm = get_llm()
    # Force JSON Output
    structured_llm = llm.with_structured_output(VerificationResult)

    logger.info(f"🧠 [Verifier] Reviewing {len(findings)} findings...")

    for finding in findings:
        if finding.severity not in [Severity.CRITICAL, Severity.HIGH]:
            finding.status = FindingStatus.UNVERIFIED
            verified_list.append(finding)
            continue

        try:
            result = structured_llm.invoke(f"""
                Analyze this finding.
                Vuln: {finding.vuln_type}
                File: {finding.file_path}:{finding.line_number}
                Code:
                {finding.code_snippet}
            """)

            # Update Fields
            finding.confidence_score = result.confidence  # <--- CAPTURE SCORE
            finding.description += f" [Reason: {result.reasoning}]"

            if result.is_true_positive:
                finding.status = FindingStatus.TRUE_POSITIVE
                finding.remediation = result.fix_suggestion
            else:
                finding.status = FindingStatus.FALSE_POSITIVE
        
        except Exception as e:
            logger.error(f"❌ [Verifier] Failed: {e}")
            finding.status = FindingStatus.NEEDS_REVIEW
        
        verified_list.append(finding)

    return {"verified_findings": verified_list}