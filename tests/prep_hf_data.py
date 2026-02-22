import os
import json
import logging
from datasets import load_dataset
from rich.console import Console
from dotenv import load_dotenv

load_dotenv()

console = Console()
logging.basicConfig(level=logging.INFO, format="%(message)s")

MOCK_REPO_DIR = os.path.join(os.path.dirname(__file__), "mock_repo")
OUTPUT_JSON = os.path.join(os.path.dirname(__file__), "benchmark_data.json")
SAMPLE_SIZE = 10 

def setup_directories():
    if not os.path.exists(MOCK_REPO_DIR):
        os.makedirs(MOCK_REPO_DIR)
        console.print(f"[green]Created mock repository at: {MOCK_REPO_DIR}[/green]")
    else:
        for f in os.listdir(MOCK_REPO_DIR):
            os.remove(os.path.join(MOCK_REPO_DIR, f))
        console.print(f"[green]Cleaned existing mock repository.[/green]")

def fallback_generator():
    """If HF fails, use these hardcoded real-world examples to unblock the user."""
    console.print("[yellow]Using local fallback dataset...[/yellow]")
    return [
        {"code": "import sqlite3\ndef get_user(user_id):\n    conn = sqlite3.connect('app.db')\n    # Vulnerable: SQL Injection\n    query = 'SELECT * FROM users WHERE id = ' + user_id\n    return conn.execute(query).fetchall()", "label": "SQL Injection"},
        {"code": "import sqlite3\ndef get_user(user_id):\n    conn = sqlite3.connect('app.db')\n    # Safe: Parameterized Query\n    query = 'SELECT * FROM users WHERE id = ?'\n    return conn.execute(query, (user_id,)).fetchall()", "label": "safe"},
        {"code": "import subprocess\ndef ping_host(host):\n    # Vulnerable: Command Injection\n    return subprocess.check_output('ping -c 1 ' + host, shell=True)", "label": "Command Injection"},
        {"code": "import subprocess\ndef ping_host(host):\n    # Safe: No shell=True, input is passed as list\n    return subprocess.check_output(['ping', '-c', '1', host])", "label": "safe"}
    ]

def fetch_and_transform_data():
    console.print(f"Attempting to stream from Hugging Face public dataset...")
    benchmark_records = []
    
    try:
        # REPLACE THIS STRING WITH YOUR ACTUAL TOKEN
        HF_TOKEN = os.getenv("HF_TOKEN") 

        # We pass the token into the function to bypass anonymous rate limits
        dataset = load_dataset(
            "lemon42-ai/Code_Vulnerability_Labeled_Dataset", 
            split="train", 
            streaming=True,
            token=HF_TOKEN
        )
        iterator = iter(dataset)
    except Exception as e:
        console.print(f"[red]Hugging Face fetch failed: {e}[/red]")
        iterator = iter(fallback_generator())

    tp_count = 0
    fp_count = 0

    for row in iterator:
        if len(benchmark_records) >= SAMPLE_SIZE:
            break
            
        code = row.get("code", "")
        label = row.get("label", "unknown")
        
        # Simple heuristic to ensure we only test Python code
        if "def " not in code and "import " not in code:
            continue

        is_safe = (label.lower() == "safe")
        
        # Balance the dataset (Half True Positives, Half False Positives)
        if is_safe and fp_count >= (SAMPLE_SIZE // 2):
            continue
        if not is_safe and tp_count >= (SAMPLE_SIZE // 2):
            continue

        status = "FALSE_POSITIVE" if is_safe else "TRUE_POSITIVE"
        filename = f"{'safe' if is_safe else 'vuln'}_file_{len(benchmark_records)}.py"
        filepath = os.path.join(MOCK_REPO_DIR, filename)
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(code)
            
        benchmark_records.append({
            "id": f"{status[:2]}_{len(benchmark_records)}",
            "file_path": filename, 
            "line_number": 3, 
            "vuln_type": "Safe Code" if is_safe else label,
            "code_snippet": code[:250] + "\n...", 
            "expected_status": status
        })

        if is_safe:
            fp_count += 1
        else:
            tp_count += 1
            
        console.print(f"  [cyan]Generated Pair {len(benchmark_records)}/{SAMPLE_SIZE} ({status})[/cyan]")

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(benchmark_records, f, indent=4)
        
    console.print(f"\n[bold green]🎉 Data Prep Complete![/bold green]")
    console.print(f"Generated {len(benchmark_records)} test cases in {OUTPUT_JSON}")

if __name__ == "__main__":
    setup_directories()
    fetch_and_transform_data()