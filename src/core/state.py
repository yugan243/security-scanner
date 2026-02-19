import operator
from typing import List, Annotated, Dict, Any
from typing_extensions import TypedDict
from src.core.models import Vulnerability

class AgentState(TypedDict):
    """
    The 'Memory' of our workflow. 
    As the graph runs, this dictionary gets updated.
    """
    # Input: The path to the repo we are scanning
    repo_path: str
    
    # The raw findings from Semgrep
    # operator.add means: if multiple agents return findings, merge them (don't overwrite)
    findings: Annotated[List[Vulnerability], operator.add]
    
    # The final filtered list after LLM verification
    verified_findings: List[Vulnerability]
    
    # Stats for the final report
    scan_summary: Dict[str, Any]