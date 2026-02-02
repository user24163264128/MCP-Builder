"""GitHub-specific data models."""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class GitHubRepository:
    """GitHub repository metadata."""
    name: str
    full_name: str
    description: Optional[str]
    stars: int
    forks: int
    open_issues: int
    language: Optional[str]
    topics: List[str]
    created_at: datetime
    updated_at: datetime
    pushed_at: datetime
    size: int  # KB
    default_branch: str
    license: Optional[str]
    has_wiki: bool
    has_pages: bool
    has_projects: bool
    archived: bool
    disabled: bool


@dataclass
class GitHubContributor:
    """GitHub contributor information."""
    login: str
    contributions: int
    type: str  # User or Bot


@dataclass
class GitHubLanguageStats:
    """Programming language statistics from GitHub."""
    languages: dict[str, int]  # language -> bytes
    total_bytes: int


@dataclass
class GitHubMetrics:
    """Aggregated GitHub metrics for analysis."""
    repository: GitHubRepository
    contributors: List[GitHubContributor]
    language_stats: GitHubLanguageStats
    clone_url: str
    ssh_url: str
    
    @property
    def popularity_score(self) -> float:
        """Calculate popularity score based on stars, forks, and contributors."""
        return (self.repository.stars * 1.0 + 
                self.repository.forks * 0.5 + 
                len(self.contributors) * 0.3)
    
    @property
    def activity_level(self) -> str:
        """Determine activity level based on recent updates."""
        from datetime import timezone
        
        # Ensure both datetimes are timezone-aware
        now = datetime.now(timezone.utc)
        pushed_at = self.repository.pushed_at
        
        # If pushed_at is naive, assume UTC
        if pushed_at.tzinfo is None:
            pushed_at = pushed_at.replace(tzinfo=timezone.utc)
        
        days_since_update = (now - pushed_at).days
        if days_since_update <= 7:
            return "very_active"
        elif days_since_update <= 30:
            return "active"
        elif days_since_update <= 90:
            return "moderate"
        else:
            return "inactive"
    
    @property
    def maturity_indicators(self) -> dict[str, bool]:
        """Indicators of project maturity."""
        from datetime import timezone
        
        # Ensure timezone-aware comparison
        now = datetime.now(timezone.utc)
        created_at = self.repository.created_at
        
        # If created_at is naive, assume UTC
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)
        
        return {
            "has_license": self.repository.license is not None,
            "has_wiki": self.repository.has_wiki,
            "has_pages": self.repository.has_pages,
            "multiple_contributors": len(self.contributors) > 1,
            "established": (now - created_at).days > 90,
            "popular": self.repository.stars > 10,
        }