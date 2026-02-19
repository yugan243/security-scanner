import logging
from datetime import datetime
from src.core.state import AgentState
from src.core.models import FindingStatus, Severity, ScanReport
from src.core.llm import get_llm
from src.config import settings

logger = logging.getLogger(settings.APP_NAME)

def report_generation_node(state: AgentState) -> dict:
    """
    Node 3: Reporting Agent.
    
    1. Aggregates final statistics (Critical/High counts).
    2. ASKS the LLM (acting as a CISO) to write an Executive Summary.
    3. Generates the final Report Object for the user.
    """
    
    verified = state.get("verified_findings", [])
    repo_path = state.get("repo_path", "unknown")
    
    true_positives = [f for f in verified if f.status == FindingStatus.TRUE_POSITIVE]
    criticals = [f for f in true_positives if f.severity == Severity.CRITICAL]
    highs = [f for f in true_positives if f.severity == Severity.HIGH]
    
    # --- NEW: Generate AI Summary ---
    summary_text = "No critical issues found."
    if true_positives:
        try:
            llm = get_llm()
            vuln_list = "\n".join([f"- {f.vuln_type} in {f.file_path}" for f in true_positives[:5]])
            
            response = llm.invoke(f"""
                Write a 3-sentence executive security summary for these findings:
                {vuln_list}
            """)
            summary_text = response.content
        except Exception:
            summary_text = "AI Summary generation failed."
    # --------------------------------

    report = ScanReport(
        repo_url=repo_path,
        scan_time=datetime.now().isoformat(),
        total_findings=len(verified),
        critical_count=len(criticals),
        high_count=len(highs),
        executive_summary=summary_text, # <--- Save it here
        findings=verified
    )
    
    logger.info(f"📊 [Reporter] Summary: {summary_text}")
    return {"scan_summary": {"report_object": report}}