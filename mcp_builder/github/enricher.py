"""GitHub data enrichment for repository snapshots."""

import logging
from typing import Optional

from .client import GitHubClient
from .models import GitHubMetrics
from ..ingestion.models import RepositorySnapshot

logger = logging.getLogger(__name__)


class GitHubEnricher:
    """Enriches repository snapshots with GitHub metadata."""
    
    def __init__(self, github_client: GitHubClient):
        """Initialize with GitHub client."""
        self.github_client = github_client
    
    def enrich_snapshot(self, snapshot: RepositorySnapshot, github_url: str) -> tuple[RepositorySnapshot, GitHubMetrics]:
        """Enrich repository snapshot with GitHub metadata.
        
        Args:
            snapshot: Local repository snapshot
            github_url: GitHub repository URL
            
        Returns:
            Tuple of (original snapshot, GitHub metrics)
        """
        try:
            github_metrics = self.github_client.get_repository_metrics(github_url)
            logger.info(f"Enriched snapshot with GitHub data: {github_metrics.repository.stars} stars, "
                       f"{len(github_metrics.contributors)} contributors")
            return snapshot, github_metrics
            
        except Exception as e:
            logger.error(f"Failed to enrich snapshot with GitHub data: {e}")
            raise
    
    def should_use_github_data(self, github_metrics: GitHubMetrics) -> bool:
        """Determine if GitHub data should be prioritized over local analysis."""
        # Use GitHub data if repository has significant activity/popularity
        return (github_metrics.repository.stars > 5 or 
                len(github_metrics.contributors) > 2 or
                github_metrics.activity_level in ["active", "very_active"])
    
    def merge_language_data(self, local_languages: list[str], github_metrics: GitHubMetrics) -> list[str]:
        """Merge local language detection with GitHub language stats."""
        github_languages = []
        
        if github_metrics.language_stats.languages:
            # Sort by bytes and take top languages
            sorted_langs = sorted(
                github_metrics.language_stats.languages.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            # Convert to percentage and filter significant languages (>5%)
            total_bytes = github_metrics.language_stats.total_bytes
            for lang, bytes_count in sorted_langs:
                percentage = (bytes_count / total_bytes) * 100 if total_bytes > 0 else 0
                if percentage >= 5.0:  # Only include languages that are 5%+ of codebase
                    github_languages.append(lang)
        
        # Combine and deduplicate, prioritizing GitHub data if available
        if github_languages:
            combined = github_languages + [lang for lang in local_languages if lang not in github_languages]
        else:
            combined = local_languages
        
        return combined[:10]  # Limit to top 10 languages