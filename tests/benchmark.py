import json
import logging
from rich.console import Console
from rich.table import Table

from vigil.agents.verifier import verify_findings_node
from vigil.core.models import Vulnerability, FindingStatus, Severity
from vigil.config import settings

console = Console()
logger = logging.getLogger(settings.APP_NAME)
# Mute standard logging so we only see the LLM's thought process and the final table
logger.setLevel(logging.ERROR) 

def run_benchmark():
    # 1. Load the Ground Truth dataset (The Answer Key)
    try:
        with open("tests/benchmark_data.json", "r", encoding="utf-8") as f:
            ground_truth = json.load(f)
    except FileNotFoundError:
        console.print("[red]❌Error: benchmark_data.json not found. Run prep_hf_data.py first![/red]")
        return

    # 2. Mock the LangGraph State (Bypassing Semgrep)
    mock_findings = []
    for item in ground_truth:
        mock_findings.append(Vulnerability(
            id=item["id"],
            file_path=item["file_path"],
            line_number=item["line_number"],
            vuln_type=item["vuln_type"],
            severity=Severity.HIGH, # Force it to High so the Verifier doesn't ignore it
            description="Mock vulnerability from benchmark dataset",
            code_snippet=item["code_snippet"],
            status=FindingStatus.UNVERIFIED
        ))

    mock_state = {
        "repo_path": "tests/mock_repo", # Point the "Hand" to our generated physical files!
        "findings": mock_findings
    }

    # 3. Run the Verifier Agent
    console.print("\n[bold cyan]🚀 Starting AI Benchmark...[/bold cyan]")
    console.print(f"Evaluating {len(ground_truth)} snippets. The LLM may use the File Reader tool...\n")
    
    # We pass the mock state directly into the node function
    final_state = verify_findings_node(mock_state)
    verified_findings = final_state.get("verified_findings", [])

    # 4. Calculate the Confusion Matrix
    tp, fp, tn, fn = 0, 0, 0, 0

    table = Table(title="AI Evaluation Results")
    table.add_column("File", style="cyan")
    table.add_column("Expected", style="blue")
    table.add_column("AI Decision", style="magenta")
    table.add_column("Result", style="bold")

    for original, evaluated in zip(ground_truth, verified_findings):
        expected = original["expected_status"]
        actual = evaluated.status.value

        # Grading Logic
        if expected == "TRUE_POSITIVE" and actual == "TRUE_POSITIVE":
            tp += 1
            result_str = "[green]✅ Correct (TP)[/green]"
        elif expected == "FALSE_POSITIVE" and actual == "FALSE_POSITIVE":
            tn += 1
            result_str = "[green]✅ Correct (TN)[/green]"
        elif expected == "TRUE_POSITIVE" and actual == "FALSE_POSITIVE":
            fn += 1
            result_str = "[red]❌ Missed Threat (FN)[/red]"
        elif expected == "FALSE_POSITIVE" and actual == "TRUE_POSITIVE":
            fp += 1
            result_str = "[yellow]⚠️ False Alarm (FP)[/yellow]"
        else:
            result_str = f"[dim]Unhandled: {actual}[/dim]"

        table.add_row(original["file_path"], expected, actual, result_str)

    # 5. Print the Report Card
    console.print(table)
    
    total = len(ground_truth)
    accuracy = ((tp + tn) / total) * 100 if total > 0 else 0
    fn_rate = (fn / (tp + fn)) * 100 if (tp + fn) > 0 else 0

    console.print("\n[bold]📊 Benchmark Metrics:[/bold]")
    console.print(f"Total Evaluated: {total}")
    console.print(f"Accuracy: [bold green]{accuracy:.1f}%[/bold green]")
    console.print(f"False Negative Rate (Critical Misses): [bold red]{fn_rate:.1f}%[/bold red]")
    
if __name__ == "__main__":
    run_benchmark()