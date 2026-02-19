from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field

class Severity(str, Enum):
    CRITICAL = "CRITICAL",
    HIGH = "HIGH",
    MEDIUM = "MEDIUM",
    LOW = "LOW",
    INFO = "INFO"
    
class FindingStatus(str, Enum):
    UNVERIFIED = "UNVERIFIED"   # Raw finding from Semgrep
    TRUE_POSITIVE = "TRUE_POSITIVE" # Confirmed by AI
    FALSE_POSITIVE = "FALSE_POSITIVE" # Rejected by AI
    NEEDS_REVIEW = "NEEDS_REVIEW" # AI wasn't sure
    
class Vulnerability(BaseModel):
    """
    Represents a single security flaw found in the codebase.
    This is the standard language our agents will speak.
    """
    id: str = Field(..., description="Unique ID of the finding")
    file_path: str = Field(..., description="Path to the vulnerable file")
    line_number: int = Field(..., description="Line number where the issue starts")
    severity: Severity = Field(..., description="How dangerous is this?")
    vuln_type: str = Field(..., description="Type of the vulnerability (e.g., SQL Injection)")
    description: str = Field(..., description="Human-readable explanation of the flaw")
    code_snippet: str = Field(..., description="The actual vulnerable code")
    
    # AI Enrichment Fields
    remediation: Optional[str] = Field(None, description="How to fix it?")
    status: FindingStatus = Field(default=FindingStatus.UNVERIFIED)
    confidence_score: float = Field(default=0.0, description="0.0 to 1.0 confidence")
    
class ScanReport(BaseModel):
    """
    The final report generated for the user
    """
    repo_url: str
    scan_time: str
    total_findings: int
    critical_count: int
    high_count: int
    executive_summary: str = Field(default="No summary generated.")
    findings: List[Vulnerability]