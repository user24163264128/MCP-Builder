"""Repository walker and content collector."""

import logging
from pathlib import Path
from typing import List, Optional

import git

from .models import FileContent, GitCommit, RepositorySnapshot
from ..github.client import GitHubClient
from ..github.cloner import GitHubCloner
from ..github.enricher import GitHubEnricher

logger = logging.getLogger(__name__)

# Directories to ignore during traversal
IGNORE_DIRS = {
    '.git',
    '__pycache__',
    'node_modules',
    'venv',
    'env',
    '.venv',
    'build',
    'dist',
    '.pytest_cache',
    '.mypy_cache',
    '.tox',
    '.eggs',
    '*.egg-info',
}

# High priority files
HIGH_PRIORITY_FILES = {
    'readme.md',
    'readme.txt',
    'readme.rst',
    'readme',
}

# Configuration and manifest files
CONFIG_FILES = {
    'requirements.txt',
    'pyproject.toml',
    'setup.py',
    'setup.cfg',
    'package.json',
    'tsconfig.json',
    'dockerfile',
    'docker-compose.yml',
    'makefile',
    '.gitignore',
    'license',
    'license.txt',
    'license.md',
}


def calculate_priority(path: Path) -> int:
    """Calculate priority score for a file (higher is more important)."""
    name = path.name.lower()
    if name in HIGH_PRIORITY_FILES:
        return 10
    if name in CONFIG_FILES:
        return 8
    if path.suffix.lower() in {'.py', '.js', '.ts', '.java', '.cpp', '.c', '.h', '.go', '.rs'}:
        return 5
    if path.suffix.lower() in {'.md', '.txt', '.rst'}:
        return 7
    return 1


def should_ignore_path(path: Path) -> bool:
    """Check if path should be ignored."""
    return any(part in IGNORE_DIRS for part in path.parts)


def collect_files(root: Path) -> List[FileContent]:
    """Collect readable text files from the repository."""
    files = []
    for path in root.rglob('*'):
        if path.is_file() and not should_ignore_path(path):
            try:
                content = path.read_text(encoding='utf-8', errors='ignore')
                priority = calculate_priority(path)
                files.append(FileContent(path, content, priority))
            except (OSError, UnicodeDecodeError):
                logger.debug(f"Skipping unreadable file: {path}")
                continue
    # Sort by priority descending
    files.sort(key=lambda f: f.priority, reverse=True)
    return files


def get_recent_commits(root: Path, limit: int = 10) -> List[GitCommit]:
    """Get recent git commits if repository is a git repo."""
    try:
        repo = git.Repo(root)
        commits = list(repo.iter_commits('HEAD', max_count=limit))
        return [
            GitCommit(
                hash=c.hexsha,
                message=c.message.strip(),
                author=c.author.name,
                date=str(c.authored_datetime),
            )
            for c in commits
        ]
    except git.InvalidGitRepositoryError:
        return []


def ingest_repository(repo_path: str, github_token: Optional[str] = None) -> RepositorySnapshot:
    """Ingest repository content into a snapshot.
    
    Args:
        repo_path: Local path or GitHub URL
        github_token: Optional GitHub API token for enhanced metadata
    """
    # Check if this is a GitHub URL
    if is_github_url(repo_path):
        return ingest_github_repository(repo_path, github_token)
    else:
        return ingest_local_repository(repo_path)


def is_github_url(path: str) -> bool:
    """Check if the path is a GitHub URL."""
    return "github.com" in path.lower()


def ingest_github_repository(github_url: str, github_token: Optional[str] = None) -> RepositorySnapshot:
    """Ingest a GitHub repository by cloning it temporarily."""
    github_client = GitHubClient(github_token)
    cloner = GitHubCloner(github_client)
    
    try:
        # Clone to temporary directory
        clone_path = cloner.clone_to_temp(github_url)
        
        # Ingest the cloned repository
        snapshot = ingest_local_repository(str(clone_path))
        
        # Mark as GitHub clone and add URL
        snapshot.github_url = github_url
        snapshot.is_github_clone = True
        
        logger.info(f"Successfully ingested GitHub repository: {github_url}")
        return snapshot
        
    except Exception as e:
        logger.error(f"Failed to ingest GitHub repository {github_url}: {e}")
        raise
    finally:
        # Clean up temporary clone
        if 'clone_path' in locals():
            cloner.cleanup_temp_clone(clone_path)


def ingest_local_repository(repo_path: str) -> RepositorySnapshot:
    """Ingest local repository content into a snapshot."""
    root = Path(repo_path).resolve()
    if not root.exists():
        raise ValueError(f"Repository path does not exist: {repo_path}")
    if not root.is_dir():
        raise ValueError(f"Repository path is not a directory: {repo_path}")

    logger.info(f"Ingesting repository at {root}")
    files = collect_files(root)
    commits = get_recent_commits(root)
    is_git_repo = len(commits) > 0

    return RepositorySnapshot(
        root_path=root,
        files=files,
        recent_commits=commits,
        is_git_repo=is_git_repo,
        github_url=None,
        is_github_clone=False
    )