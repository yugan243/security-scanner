import logging
from src.core.state import AgentState
from src.core.models import FindingStatus, Severity
from src.config import settings

logger = logging.getLogger(settings.APP_NAME)

def report_generation_node(state: AgentState) -> dict:
    """
    Node 3: Reporting.
    Aggregates stats and prepares the final summary.
    """
    verified = state.get("verified_findings", [])
    
    # calculate stats
    stats = {
        "total": len(verified),
        "critical": len([f for f in verified if f.severity == Severity.CRITICAL]),
        "high": len([f for f in verified if f.severity == Severity.HIGH]),
        "true_positives": len([f for f in verified if f.status == FindingStatus.TRUE_POSITIVE]),
        "false_positives": len([f for f in verified if f.status == FindingStatus.FALSE_POSITIVE])
    }
    
    logger.info(f"📊 [Reporter] Report generated. Critical: {stats['critical']}, High: {stats['high']}")
    
    return {"scan_summary": stats}