"""GitHub API client."""

import logging
import re
from datetime import datetime
from typing import Optional, Tuple
from urllib.parse import urlparse

import requests

from .models import GitHubContributor, GitHubLanguageStats, GitHubMetrics, GitHubRepository

logger = logging.getLogger(__name__)


class GitHubClient:
    """GitHub API client for fetching repository metadata."""
    
    def __init__(self, token: Optional[str] = None):
        """Initialize GitHub client with optional authentication token."""
        self.token = token
        self.base_url = "https://api.github.com"
        self.session = requests.Session()
        
        if token:
            self.session.headers.update({"Authorization": f"token {token}"})
        
        # Set user agent as required by GitHub API
        self.session.headers.update({
            "User-Agent": "MCP-Builder/1.0",
            "Accept": "application/vnd.github.v3+json"
        })
    
    def parse_github_url(self, url: str) -> Tuple[str, str]:
        """Parse GitHub URL to extract owner and repo name."""
        # Handle various GitHub URL formats
        patterns = [
            r"github\.com[:/]([^/]+)/([^/]+?)(?:\.git)?/?$",
            r"github\.com/([^/]+)/([^/]+)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                owner, repo = match.groups()
                return owner, repo
        
        raise ValueError(f"Invalid GitHub URL format: {url}")
    
    def get_repository(self, owner: str, repo: str) -> GitHubRepository:
        """Fetch repository metadata from GitHub API."""
        url = f"{self.base_url}/repos/{owner}/{repo}"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            data = response.json()
            
            return GitHubRepository(
                name=data["name"],
                full_name=data["full_name"],
                description=data.get("description"),
                stars=data["stargazers_count"],
                forks=data["forks_count"],
                open_issues=data["open_issues_count"],
                language=data.get("language"),
                topics=data.get("topics", []),
                created_at=datetime.fromisoformat(data["created_at"].replace("Z", "+00:00")),
                updated_at=datetime.fromisoformat(data["updated_at"].replace("Z", "+00:00")),
                pushed_at=datetime.fromisoformat(data["pushed_at"].replace("Z", "+00:00")),
                size=data["size"],
                default_branch=data["default_branch"],
                license=data["license"]["name"] if data.get("license") else None,
                has_wiki=data["has_wiki"],
                has_pages=data["has_pages"],
                has_projects=data["has_projects"],
                archived=data["archived"],
                disabled=data["disabled"],
            )
            
        except requests.RequestException as e:
            logger.error(f"Failed to fetch repository {owner}/{repo}: {e}")
            raise
    
    def get_contributors(self, owner: str, repo: str, limit: int = 30) -> list[GitHubContributor]:
        """Fetch repository contributors."""
        url = f"{self.base_url}/repos/{owner}/{repo}/contributors"
        params = {"per_page": limit}
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            return [
                GitHubContributor(
                    login=contributor["login"],
                    contributions=contributor["contributions"],
                    type=contributor["type"]
                )
                for contributor in data
            ]
            
        except requests.RequestException as e:
            logger.warning(f"Failed to fetch contributors for {owner}/{repo}: {e}")
            return []
    
    def get_language_stats(self, owner: str, repo: str) -> GitHubLanguageStats:
        """Fetch programming language statistics."""
        url = f"{self.base_url}/repos/{owner}/{repo}/languages"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            languages = response.json()
            
            total_bytes = sum(languages.values())
            
            return GitHubLanguageStats(
                languages=languages,
                total_bytes=total_bytes
            )
            
        except requests.RequestException as e:
            logger.warning(f"Failed to fetch language stats for {owner}/{repo}: {e}")
            return GitHubLanguageStats(languages={}, total_bytes=0)
    
    def get_repository_metrics(self, github_url: str) -> GitHubMetrics:
        """Fetch comprehensive repository metrics."""
        owner, repo = self.parse_github_url(github_url)
        
        logger.info(f"Fetching GitHub metrics for {owner}/{repo}")
        
        repository = self.get_repository(owner, repo)
        contributors = self.get_contributors(owner, repo)
        language_stats = self.get_language_stats(owner, repo)
        
        return GitHubMetrics(
            repository=repository,
            contributors=contributors,
            language_stats=language_stats,
            clone_url=f"https://github.com/{owner}/{repo}.git",
            ssh_url=f"git@github.com:{owner}/{repo}.git"
        )
    
    def check_rate_limit(self) -> dict:
        """Check current GitHub API rate limit status."""
        url = f"{self.base_url}/rate_limit"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.warning(f"Failed to check rate limit: {e}")
            return {}