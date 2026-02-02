import os
import shutil
from git import Repo
from pathlib import Path
import stat

class RepoIngestor:
    def __init__(self, base_data_dir="./data"):
        self.base_data_dir = Path(base_data_dir)
        self.base_data_dir.mkdir(exist_ok=True)
        # Extensions we care about for a "Senior Dev" perspective
        self.supported_ext = {'.py', '.js', '.ts', '.jsx', '.tsx', '.go', '.rs', '.c', '.cpp', '.java'}
        self.ignore_folders = {'.git', 'node_modules', 'venv', '__pycache__', 'dist', 'build', '.next'}

    def clone_repo(self, repo_url):
        """Clones repo into a unique folder based on the URL."""
        repo_name = repo_url.split("/")[-1].replace(".git", "")
        target_path = self.base_data_dir / repo_name
        
        if target_path.exists():
            print(f"Directory {target_path} exists. Deleting to refresh...")
            # Use a standalone function or lambda for the error handler
            shutil.rmtree(target_path, onerror=self._handle_remove_readonly)
            
        print(f"Cloning {repo_url}...")
        Repo.clone_from(repo_url, target_path)
        return target_path

    def map_codebase(self, repo_path):
        """Walks through the code and creates the formatted text block."""
        repo_path = Path(repo_path)
        formatted_content = []
        
        for path in repo_path.rglob('*'):
            # Skip ignored directories
            if any(part in self.ignore_folders for part in path.parts):
                continue
            
            if path.is_file() and path.suffix in self.supported_ext:
                try:
                    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                        relative_path = path.relative_to(repo_path)
                        content = f.read()
                        # This format helps Gemini understand the file hierarchy
                        block = f"\n--- FILE: {relative_path} ---\n{content}\n"
                        formatted_content.append(block)
                except Exception as e:
                    print(f"Error reading {path}: {e}")
                    
        return "".join(formatted_content)

    def _handle_remove_readonly(self, func, path, exc_info):
        """Handle read-only files during deletion."""
        os.chmod(path, stat.S_IWRITE)
        func(path)