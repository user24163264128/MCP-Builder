"""Data models for ingestion layer."""

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional


@dataclass
class FileContent:
    """Represents content of a file with metadata."""
    path: Path
    content: str
    priority: int  # Higher values for more important files


@dataclass
class GitCommit:
    """Represents a git commit."""
    hash: str
    message: str
    author: str
    date: str


@dataclass
class RepositorySnapshot:
    """Snapshot of repository content."""
    root_path: Path
    files: List[FileContent]
    recent_commits: List[GitCommit]
    is_git_repo: bool
    github_url: Optional[str] = None  # GitHub URL if this is a GitHub repository
    is_github_clone: bool = False  # True if this was cloned from GitHub