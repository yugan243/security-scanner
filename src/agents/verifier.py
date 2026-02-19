import logging
from langchain_core.prompts import ChatPromptTemplate
from src.core.state import AgentState
from src.core.llm import get_llm
from src.core.models import FindingStatus, Severity
from src.config import settings

logger = logging.getLogger(settings.APP_NAME)

def verify_findings_node(state: AgentState) -> dict:
    """
    Node 2: AI Verification.
    Filters false positives using the configured LLM.
    """
    findings = state.get("findings", [])
    verified_list = []
    
    # If no findings, skip
    if not findings:
        return {"verified_findings": []}

    llm = get_llm()
    logger.info(f"[Verifier] Reviewing {len(findings)} findings with {settings.LLM_PROVIDER}...")

    # Prompt Engineering: A strict "Judge" persona
    prompt = ChatPromptTemplate.from_template(
        """
        You are a Senior Security Engineer. Review this static analysis finding.

        CONTEXT:
        - Vulnerability Type: {vuln_type}
        - Severity: {severity}
        - File: {file_path}:{line_number}

        CODE SNIPPET:
        ```
        {code}
        ```

        YOUR TASK:
        1. Analyze if the code is actually vulnerable or if it is a False Positive (e.g., test code, sanitized input).
        2. If Vulnerable, suggest a brief fix.
        
        OUTPUT FORMAT:
        Start your response with either "TRUE_POSITIVE" or "FALSE_POSITIVE", followed by a separator "||", then your explanation.
        Example: "FALSE_POSITIVE || Input is sanitized by regex on line 42."
        """
    )

    chain = prompt | llm

    for finding in findings:
        # Optimization: Skip Low severity to save tokens
        if finding.severity not in [Severity.CRITICAL, Severity.HIGH]:
            finding.status = FindingStatus.UNVERIFIED
            verified_list.append(finding)
            continue

        try:
            response = chain.invoke({
                "vuln_type": finding.vuln_type,
                "severity": finding.severity.value,
                "file_path": finding.file_path,
                "line_number": finding.line_number,
                "code": finding.code_snippet
            })
            
            # Simple parsing of the "TRUE_POSITIVE || Explanation" format
            content = response.content.strip()
            if "||" in content:
                status_str, explanation = content.split("||", 1)
            else:
                status_str, explanation = content, "No explanation provided."

            if "TRUE_POSITIVE" in status_str.upper():
                finding.status = FindingStatus.TRUE_POSITIVE
                finding.remediation = explanation.strip()
            elif "FALSE_POSITIVE" in status_str.upper():
                finding.status = FindingStatus.FALSE_POSITIVE
                finding.description += f" [AI Dismissed: {explanation.strip()}]"
            else:
                finding.status = FindingStatus.NEEDS_REVIEW

        except Exception as e:
            logger.error(f"[Verifier] LLM Failed on {finding.id}: {e}")
        
        verified_list.append(finding)

    return {"verified_findings": verified_list}