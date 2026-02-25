import logging
from datetime import datetime
from vigil.core.state import AgentState
from vigil.core.models import FindingStatus, Severity, ScanReport
from vigil.core.llm import get_llm
from vigil.config import settings
from collections import Counter

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
    
    # --- Generate AI Summary ---
    summary_text = "No critical issues found."
    if true_positives:
        try:
            llm = get_llm()
            
            # 1. Count how many times each vulnerability type appears
            vuln_counts = Counter([f.vuln_type for f in true_positives])
            
            # 2. Format the aggregated list (e.g., "- SQL Injection: 12 instance(s)")
            vuln_list = "\n".join([f"- {v_type}: {count} instance(s)" for v_type, count in vuln_counts.items()])
            
            logger.info(f"[Reporter] Sending aggregated metrics to LLM:\n{vuln_list}")
            
            # 3. Ask the LLM to summarize based on the metrics
            response = llm.invoke(f"""
                You are a Chief Information Security Officer (CISO).
                Write a 3-sentence executive security summary based on these vulnerability metrics:
                
                {vuln_list}
                
                Focus on the overarching business risk and attack surface, not individual files.
                Tone: Professional, direct, and actionable.
            """)
            summary_text = response.content.strip()
            
        except Exception as e:
            logger.error(f"[Reporter] AI Summary generation failed: {e}")
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
    
    logger.info(f"[Reporter] Summary: {summary_text}")
    return {"scan_summary": {"report_object": report}}