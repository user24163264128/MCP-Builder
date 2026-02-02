"""Tests for GitHub integration functionality."""

import os
import pytest
from unittest.mock import Mock, patch

from mcp_builder.github.client import GitHubClient
from mcp_builder.github.models import GitHubRepository, GitHubMetrics
from mcp_builder.ingestion.walker import ingest_repository, is_github_url


def test_is_github_url():
    """Test GitHub URL detection."""
    assert is_github_url("https://github.com/owner/repo")
    assert is_github_url("https://github.com/owner/repo.git")
    assert is_github_url("git@github.com:owner/repo.git")
    assert not is_github_url("/local/path")
    assert not is_github_url("https://gitlab.com/owner/repo")


def test_github_client_parse_url():
    """Test GitHub URL parsing."""
    client = GitHubClient()
    
    # Test various URL formats
    owner, repo = client.parse_github_url("https://github.com/owner/repo")
    assert owner == "owner"
    assert repo == "repo"
    
    owner, repo = client.parse_github_url("https://github.com/owner/repo.git")
    assert owner == "owner"
    assert repo == "repo"
    
    owner, repo = client.parse_github_url("git@github.com:owner/repo.git")
    assert owner == "owner"
    assert repo == "repo"
    
    # Test invalid URL
    with pytest.raises(ValueError):
        client.parse_github_url("https://invalid-url.com/repo")


@patch('mcp_builder.github.client.requests.Session.get')
def test_github_client_get_repository(mock_get):
    """Test GitHub repository metadata fetching."""
    # Mock API response
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "name": "test-repo",
        "full_name": "owner/test-repo",
        "description": "A test repository",
        "stargazers_count": 42,
        "forks_count": 10,
        "open_issues_count": 5,
        "language": "Python",
        "topics": ["python", "cli"],
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-12-01T00:00:00Z",
        "pushed_at": "2023-12-01T00:00:00Z",
        "size": 1024,
        "default_branch": "main",
        "license": {"name": "MIT"},
        "has_wiki": True,
        "has_pages": False,
        "has_projects": True,
        "archived": False,
        "disabled": False,
    }
    mock_get.return_value = mock_response
    
    client = GitHubClient("fake-token")
    repo = client.get_repository("owner", "test-repo")
    
    assert repo.name == "test-repo"
    assert repo.stars == 42
    assert repo.forks == 10
    assert repo.language == "Python"
    assert repo.license == "MIT"
    assert "python" in repo.topics


@patch('mcp_builder.github.cloner.git.Repo.clone_from')
@patch('mcp_builder.github.cloner.tempfile.mkdtemp')
def test_github_repository_ingestion(mock_mkdtemp, mock_clone, tmp_path):
    """Test ingesting a GitHub repository."""
    # Mock temporary directory
    temp_dir = tmp_path / "temp_clone"
    temp_dir.mkdir()
    mock_mkdtemp.return_value = str(temp_dir)
    
    # Create mock repository content
    (temp_dir / "README.md").write_text("# Test Repo\n\nA test repository.")
    (temp_dir / "main.py").write_text("print('hello world')")
    
    # Mock git clone
    mock_repo = Mock()
    mock_clone.return_value = mock_repo
    
    # Test ingestion
    github_url = "https://github.com/owner/test-repo"
    
    with patch('mcp_builder.ingestion.walker.ingest_local_repository') as mock_ingest:
        mock_snapshot = Mock()
        mock_snapshot.github_url = None
        mock_snapshot.is_github_clone = False
        mock_ingest.return_value = mock_snapshot
        
        snapshot = ingest_repository(github_url)
        
        # Verify the snapshot was marked as GitHub clone
        assert snapshot.github_url == github_url
        assert snapshot.is_github_clone == True


def test_github_metrics_calculations():
    """Test GitHub metrics calculations."""
    from datetime import datetime, timedelta
    from mcp_builder.github.models import GitHubRepository, GitHubContributor, GitHubLanguageStats, GitHubMetrics
    
    # Create test data
    repo = GitHubRepository(
        name="test-repo",
        full_name="owner/test-repo", 
        description="Test",
        stars=100,
        forks=20,
        open_issues=5,
        language="Python",
        topics=[],
        created_at=datetime.now() - timedelta(days=365),
        updated_at=datetime.now() - timedelta(days=1),
        pushed_at=datetime.now() - timedelta(days=1),
        size=1024,
        default_branch="main",
        license="MIT",
        has_wiki=True,
        has_pages=False,
        has_projects=True,
        archived=False,
        disabled=False
    )
    
    contributors = [
        GitHubContributor("user1", 50, "User"),
        GitHubContributor("user2", 30, "User"),
        GitHubContributor("user3", 10, "User"),
    ]
    
    lang_stats = GitHubLanguageStats(
        languages={"Python": 8000, "JavaScript": 2000},
        total_bytes=10000
    )
    
    metrics = GitHubMetrics(
        repository=repo,
        contributors=contributors,
        language_stats=lang_stats,
        clone_url="https://github.com/owner/test-repo.git",
        ssh_url="git@github.com:owner/test-repo.git"
    )
    
    # Test calculations
    assert metrics.popularity_score == 100 * 1.0 + 20 * 0.5 + 3 * 0.3  # 110.9
    assert metrics.activity_level == "very_active"  # pushed yesterday
    
    maturity = metrics.maturity_indicators
    assert maturity["has_license"] == True
    assert maturity["multiple_contributors"] == True
    assert maturity["established"] == True
    assert maturity["popular"] == True


if __name__ == "__main__":
    pytest.main([__file__])