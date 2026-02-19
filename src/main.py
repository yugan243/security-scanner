import typer
import logging
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown
from src.agents.workflow import create_workflow
from src.config import settings

# Setup App
app = typer.Typer(help="AI-Powered Security Scanner")
console = Console()

# Setup Logging (Quiet by default, showing only INFO/ERROR)
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(settings.APP_NAME)

@app.command()
def scan(
    path: str = typer.Argument(..., help="Path to the repository to scan"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed logs")
):
    """
    Scans a local repository for security vulnerabilities.
    """
    console.print(Panel(f" Starting Scan on: [bold]{path}[/bold]", style="green"))
    
    # 1. Initialize Workflow
    workflow = create_workflow()
    
    # 2. Run the Graph
    try:
        inputs = {"repo_path": path, "findings": [], "verified_findings": []}
        
        # Invoke the graph (this triggers the chain: scanner -> verifier -> reporter)
        final_state = workflow.invoke(inputs)
        
        # 3. Extract Results
        stats = final_state.get("scan_summary", {})
        report_obj = stats.get("report_object")
        
        if not report_obj:
            console.print("[red] Error: No report generated.[/red]")
            return

        # 4. Print Executive Summary (The Supervisor's Request)
        console.print("\n")
        console.print(Panel(
            Markdown(f"**CISO Executive Summary:**\n\n{report_obj.executive_summary}"),
            title="AI Security Assessment",
            style="blue"
        ))

        # 5. Print Findings Table
        table = Table(title="Confirmed Vulnerabilities")
        table.add_column("Sev", style="red")
        table.add_column("Type", style="cyan")
        table.add_column("Location")
        table.add_column("Conf", justify="right")
        table.add_column("Status")

        for f in report_obj.findings:
            # Color code confidence
            conf_color = "green" if f.confidence_score > 0.8 else "yellow"
            
            table.add_row(
                f.severity.value,
                f.vuln_type,
                f"{f.file_path}:{f.line_number}",
                f"[{conf_color}]{f.confidence_score:.2f}[/{conf_color}]",
                f.status.value
            )

        console.print(table)
        console.print(f"\nScan Complete. Total Issues: {report_obj.total_findings}")

    except Exception as e:
        console.print(f"[bold red] Fatal Error:[/bold red] {e}")

if __name__ == "__main__":
    app()