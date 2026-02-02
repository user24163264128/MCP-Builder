"""GitHub repository cloning utilities."""

import logging
import shutil
import tempfile
from pathlib import Path
from typing import Optional

import git

from .client import GitHubClient

logger = logging.getLogger(__name__)


class GitHubCloner:
    """Handles cloning GitHub repositories for analysis."""
    
    def __init__(self, github_client: GitHubClient):
        """Initialize with GitHub client for metadata fetching."""
        self.github_client = github_client
    
    def clone_repository(self, github_url: str, target_dir: Optional[Path] = None, shallow: bool = True) -> Path:
        """Clone a GitHub repository to local directory.
        
        Args:
            github_url: GitHub repository URL
            target_dir: Target directory (creates temp dir if None)
            shallow: Whether to perform shallow clone (faster, less history)
            
        Returns:
            Path to cloned repository
        """
        owner, repo = self.github_client.parse_github_url(github_url)
        clone_url = f"https://github.com/{owner}/{repo}.git"
        
        if target_dir is None:
            target_dir = Path(tempfile.mkdtemp(prefix=f"mcp-{repo}-"))
        else:
            target_dir = Path(target_dir)
            target_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Cloning {clone_url} to {target_dir}")
        
        try:
            # Clone options for efficiency
            clone_kwargs = {
                "depth": 1 if shallow else None,
                "single_branch": True,
                "branch": None,  # Use default branch
            }
            
            # Remove None values
            clone_kwargs = {k: v for k, v in clone_kwargs.items() if v is not None}
            
            repo_obj = git.Repo.clone_from(clone_url, target_dir, **clone_kwargs)
            
            logger.info(f"Successfully cloned {owner}/{repo} to {target_dir}")
            return target_dir
            
        except git.GitCommandError as e:
            logger.error(f"Failed to clone repository {clone_url}: {e}")
            # Clean up failed clone directory
            if target_dir.exists():
                shutil.rmtree(target_dir, ignore_errors=True)
            raise
    
    def clone_to_temp(self, github_url: str) -> Path:
        """Clone repository to a temporary directory.
        
        Returns:
            Path to temporary directory containing cloned repo
        """
        return self.clone_repository(github_url, target_dir=None, shallow=True)
    
    def cleanup_temp_clone(self, clone_path: Path) -> None:
        """Clean up temporary clone directory."""
        if clone_path.exists() and clone_path.is_dir():
            logger.info(f"Cleaning up temporary clone at {clone_path}")
            shutil.rmtree(clone_path, ignore_errors=True)