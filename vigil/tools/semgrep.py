import subprocess
import os
import json
import logging
from typing import List
from pathlib import Path
from vigil.core.models import Vulnerability, Severity, FindingStatus
from vigil.config import settings

# Setup logger
logger = logging.getLogger(settings.APP_NAME)

class SemgrepScanner:
    """
    A wrapper around the Semgrep CLI tool.
    """

    def __init__(self):
        # We verify semgrep is installed when this class is created
        self._check_installation()

    def _check_installation(self):
        """Checks if semgrep is available in the system PATH."""
        try:
            subprocess.run(
                ["semgrep", "--version"], 
                capture_output=True, 
                check=True
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise RuntimeError(
                "Semgrep is not installed! Please run 'pipx install semgrep' or 'pip install semgrep'."
            )

    def scan_repo(self, repo_path: str) -> List[Vulnerability]:
        """
        Runs semgrep on the given path and returns structured findings.
        """
        repo_path_obj = Path(repo_path)
        if not repo_path_obj.exists():
            raise FileNotFoundError(f"Repository path not found: {repo_path}")

        logger.info(f"Starting Semgrep scan on: {repo_path}")

        # 1. Run the Command
        # We use the standard 'p/security-audit' ruleset.
        # --json: ensures we get machine-readable output.
        # --quiet: stops it from printing progress bars to stdout (we want clean logs).
        command = [
            "semgrep",
            "scan",
            "--config", "p/security-audit",
            "--json",
            "--quiet",
            str(repo_path_obj)
        ]

        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True # Raises error if semgrep crashes
            )
        except subprocess.CalledProcessError as e:
            logger.error(f"Semgrep failed: {e.stderr}")
            return []

        # 2. Parse the Output
        try:
            data = json.loads(result.stdout)
            return self._parse_findings(data, repo_path)
        except json.JSONDecodeError:
            logger.error("Failed to parse Semgrep JSON output.")
            return []

    def _parse_findings(self, raw_data: dict, repo_path: str) -> List[Vulnerability]:
        """
        Converts raw Semgrep JSON into our clean Vulnerability objects.
        """
        findings = []
        
        # Semgrep returns results in a "results" list
        for item in raw_data.get("results", []):
            
            # Map Semgrep severity (ERROR/WARNING) to our Enum
            severity_map = {
                "ERROR": Severity.HIGH,
                "WARNING": Severity.MEDIUM,
                "INFO": Severity.LOW
            }
            # Default to MEDIUM if unknown
            semgrep_severity = item.get("extra", {}).get("severity", "WARNING")
            mapped_severity = severity_map.get(semgrep_severity, Severity.MEDIUM)
            
            # --- Sanitize the path ---
            raw_path = item.get("path", "unknown")
            if raw_path != "unknown":
                try:
                    clean_path = os.path.relpath(raw_path, repo_path)
                    clean_path = clean_path.replace("\\", "/") # Standardize slashes
                except ValueError:
                    clean_path = raw_path
            else:
                clean_path = "unknown"

            # Create our specific object
            vuln = Vulnerability(
                id=item.get("check_id", "unknown"),
                file_path=clean_path,
                line_number=item.get("start", {}).get("line", 0),
                severity=mapped_severity,
                vuln_type=item.get("check_id", "Generic Vulnerability"),
                description=item.get("extra", {}).get("message", "No description"),
                code_snippet=item.get("extra", {}).get("lines", ""),
                status=FindingStatus.UNVERIFIED # It's raw, so it's unverified!
            )
            findings.append(vuln)
            
        return findings

# Usage Example (for testing only)
if __name__ == "__main__":
    scanner = SemgrepScanner()
    # Test on the current directory
    results = scanner.scan_repo(".")
    print(f"Found {len(results)} issues.")
    for r in results[:2]:
        print(f" - [{r.severity.value}] {r.vuln_type} in {r.file_path}:{r.line_number}")