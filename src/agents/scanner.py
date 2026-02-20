import logging
from src.core.state import AgentState
from src.tools.semgrep import SemgrepScanner
from src.config import settings

logger = logging.getLogger(settings.APP_NAME)

# Initialize the tool once
scanner_tool = SemgrepScanner()

def scan_repo_node(state: AgentState) -> dict:
    """
    The 'Scanner Agent'.
    1. Reads the repo path from State.
    2. Runs the Semgrep Tool.
    3. Returns the raw findings to update the State.
    """
    repo_path = state["repo_path"]
    logger.info(f"[Scanner Agent] Starting scan on: {repo_path}")
    
    try:
        # Run the tool we built earlier
        raw_results = scanner_tool.scan_repo(repo_path)
        
        count = len(raw_results)
        if count == 0:
            logger.warning("[Scanner Agent] Semgrep found 0 issues. (Is the path correct?)")
        else:
            logger.info(f"[Scanner Agent] Semgrep found {count} potential issues.")
        
        # Return ONLY the key we want to update in the state
        return {"findings": raw_results}
        
    except Exception as e:
        logger.error(f"[Scanner Agent] Scan failed: {e}")
        return {"findings": []}