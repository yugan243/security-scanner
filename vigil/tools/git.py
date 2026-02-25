import subprocess
import logging
import tempfile
from contextlib import contextmanager
from vigil.config import settings

logger = logging.getLogger(settings.APP_NAME)

@contextmanager
def clone_repo(repo_url: str):
    """
    Context manager that clones a git repository into a temporary directory.
    Yields the path to the temporary directory.
    Automatically cleans up the directory when the context exits.
    """
    logger.info(f"[Git] Preparing to clone: {repo_url}")
    
    # Create a temporary directory that auto-deletes
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            # Run the shallow clone command
            # --depth 1: Only get the latest commit (fast & light)
            # --single-branch: Only get the default branch
            command = [
                "git", "clone", 
                "--depth", "1", 
                "--single-branch", 
                repo_url, 
                temp_dir
            ]
            
            logger.info(f"[Git] Cloning into temporary workspace...")
            subprocess.run(
                command, 
                capture_output=True, 
                text=True, 
                check=True
            )
            logger.info("[Git] Shallow clone complete.")
            
            # Yield the path back to the workflow graph
            yield temp_dir
            
        except subprocess.CalledProcessError as e:
            logger.error(f"[Git] Clone failed: {e.stderr}")
            raise RuntimeError(f"Failed to clone repository: {repo_url}")
        
        # Once the workflow finishes using the 'temp_dir', the block ends.
        # Python automatically deletes the folder and all source code here.