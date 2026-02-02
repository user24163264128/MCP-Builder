"""Basic tests for MCP Builder."""

import pytest
from pathlib import Path

from mcp_builder.ingestion.walker import ingest_repository
from mcp_builder.analyzers.signals import extract_signals
from mcp_builder.mcp.schemas import ProjectType, ProjectStatus


def test_ingest_repository(tmp_path):
    """Test repository ingestion."""
    (tmp_path / "README.md").write_text("# Test Project\n\nDescription.")
    (tmp_path / "main.py").write_text("print('hello')")

    snapshot = ingest_repository(str(tmp_path))

    assert snapshot.root_path == tmp_path
    assert len(snapshot.files) >= 2
    assert not snapshot.is_git_repo


def test_extract_signals(tmp_path):
    """Test signal extraction."""
    (tmp_path / "README.md").write_text("# CLI Tool")
    (tmp_path / "main.py").write_text("import typer\n\napp = typer.Typer()")
    (tmp_path / "requirements.txt").write_text("typer\npydantic")

    snapshot = ingest_repository(str(tmp_path))
    signals = extract_signals(snapshot)

    assert "Python" in signals.languages
    assert "Typer" in signals.frameworks
    assert signals.project_type == ProjectType.CLI
    assert signals.maturity in [ProjectStatus.PROTOTYPE, ProjectStatus.MVP]


def test_mcp_generation(tmp_path):
    """Test MCP YAML generation."""
    from mcp_builder.intelligence.mock import MockReasoningEngine
    from mcp_builder.intelligence.selector import select_content
    from mcp_builder.mcp.generator import generate_mcp, save_mcp, load_mcp

    (tmp_path / "README.md").write_text("# Test Project")

    snapshot = ingest_repository(str(tmp_path))
    signals = extract_signals(snapshot)
    engine = MockReasoningEngine()
    content = select_content(snapshot)
    insights = engine.reason(signals, content)
    mcp = generate_mcp(snapshot, signals, insights)

    assert mcp.project_name == "Test Project"
    assert mcp.project_type == ProjectType.OTHER  # since no specific indicators

    # Test save and load
    mcp_path = tmp_path / "mcp.yaml"
    save_mcp(mcp, mcp_path)
    loaded = load_mcp(mcp_path)

    assert loaded.project_name == mcp.project_name