from langgraph.graph import StateGraph, START, END
from src.core.state import AgentState
from src.agents.scanner import scan_repo_node
from src.agents.verifier import verify_findings_node
from src.agents.reporter import report_generation_node

def create_workflow():
    """
    Constructs the LangGraph workflow.
    Flow: START -> Scanner -> Verifier -> Reporter -> END
    """
    # 1. Initialize the Graph with our State Schema
    workflow = StateGraph(AgentState)

    # 2. Add Nodes (The Workers)
    workflow.add_node("scanner", scan_repo_node)
    workflow.add_node("verifier", verify_findings_node)
    workflow.add_node("reporter", report_generation_node)

    # 3. Define Edges (The Logic Flow)
    workflow.add_edge(START, "scanner")
    workflow.add_edge("scanner", "verifier")
    workflow.add_edge("verifier", "reporter")
    workflow.add_edge("reporter", END)

    # 4. Compile into a Runnable App
    return workflow.compile()