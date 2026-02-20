import logging
from pathlib import Path
from src.config import settings

logger = logging.getLogger(settings.APP_NAME)

def read_code_segment(repo_root: str, file_path: str, start_line: int, end_line: int = None) -> str:
    """
    Safely reads a specific segment of a file from the repository.
    
    Args:
        repo_root (str): The absolute path to the cloned repository.
        file_path (str): The relative path to the file (e.g., "src/main.py").
        start_line (int): The line number to start reading from (1-based).
        end_line (int): The line number to stop reading (optional).
                        If None, reads 10 lines of context.
    
    Returns:
        str: The content of the file segment or an error message.
    """
    try:
        # 1. Resolve paths to absolute system paths
        root_path = Path(repo_root).resolve()
        target_path = (root_path / file_path).resolve()
        
        # 2. SECURITY CHECK: Prevent Path Traversal
        # We ensure the target file is actually INSIDE the repo folder.
        if not target_path.is_relative_to(root_path):
            logger.warning(f"[File Reader] Blocked attempt to read outside repo: {file_path}")
            return "Error: Access Denied. You cannot read files outside the repository."

        if not target_path.exists():
            return f"Error: File not found: {file_path}"

        # 3. Read the file content
        with open(target_path, "r", encoding="utf-8", errors="ignore") as f:
            all_lines = f.readlines()
            
        # 4. Calculate indices (Convert 1-based line numbers to 0-based list indices)
        total_lines = len(all_lines)
        start_idx = max(0, start_line - 1)
        
        # Default to reading 10 lines if end_line is missing
        if end_line is None:
            end_idx = min(total_lines, start_idx + 10)
        else:
            end_idx = min(total_lines, end_line)
            
        # 5. Extract and format the segment
        segment = "".join(all_lines[start_idx:end_idx])
        
        # Add a header for the LLM to understand what it's looking at
        return f"--- File: {file_path} | Lines: {start_idx+1}-{end_idx} ---\n{segment}"

    except Exception as e:
        logger.error(f"[File Reader] Failed to read {file_path}: {e}")
        return f"Error reading file: {str(e)}"