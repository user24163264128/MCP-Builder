"""Tests for AI integration functionality."""

import pytest
from unittest.mock import Mock, patch

from mcp_builder.intelligence.factory import create_reasoning_engine, list_available_providers
from mcp_builder.intelligence.mock import MockReasoningEngine
from mcp_builder.intelligence.local_llm import SimpleLLMReasoningEngine
from mcp_builder.analyzers.models import TechnicalSignals
from mcp_builder.mcp.schemas import ProjectType, ProjectStatus


def test_create_mock_reasoning_engine():
    """Test creating mock reasoning engine."""
    engine = create_reasoning_engine("mock", interactive=False)
    assert isinstance(engine, MockReasoningEngine)


def test_create_simple_reasoning_engine():
    """Test creating simple reasoning engine."""
    engine = create_reasoning_engine("simple", interactive=False)
    assert isinstance(engine, SimpleLLMReasoningEngine)


def test_list_available_providers():
    """Test listing available AI providers."""
    providers = list_available_providers()
    
    # Simple and Mock should always be available
    assert "simple" in providers
    assert providers["simple"]["available"] == True
    assert providers["simple"]["has_key"] == True
    
    assert "mock" in providers
    assert providers["mock"]["available"] == True
    assert providers["mock"]["has_key"] == True
    
    # OpenAI, Anthropic, and Local should be listed
    assert "openai" in providers
    assert "anthropic" in providers
    assert "local" in providers


def test_auto_provider_detection():
    """Test automatic provider detection."""
    # Without any API keys, should fall back to simple
    engine = create_reasoning_engine("auto", interactive=False)
    assert isinstance(engine, SimpleLLMReasoningEngine)


@patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'})
def test_openai_engine_creation():
    """Test OpenAI engine creation with API key."""
    try:
        engine = create_reasoning_engine("openai", interactive=False)
        # Should either create OpenAI engine or fall back to simple if package not installed
        assert engine is not None
    except ImportError:
        # Expected if openai package not installed
        pass


@patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'})
def test_anthropic_engine_creation():
    """Test Anthropic engine creation with API key."""
    try:
        engine = create_reasoning_engine("anthropic", interactive=False)
        # Should either create Anthropic engine or fall back to simple if package not installed
        assert engine is not None
    except ImportError:
        # Expected if anthropic package not installed
        pass


def test_local_llm_engine_creation():
    """Test local LLM engine creation."""
    try:
        engine = create_reasoning_engine("local", interactive=False)
        # Should either create Local LLM engine or fall back to simple if package not installed
        assert engine is not None
    except ImportError:
        # Expected if transformers package not installed
        pass


def test_simple_reasoning_engine_interface():
    """Test that simple reasoning engine implements the interface correctly."""
    engine = SimpleLLMReasoningEngine()
    
    # Create test signals for web app
    signals = TechnicalSignals(
        languages=["JavaScript", "TypeScript"],
        frameworks=["React"],
        project_type=ProjectType.WEB_APP,
        maturity=ProjectStatus.MVP,
        activity_level="high",
        tech_stack=["JavaScript", "TypeScript", "React"]
    )
    
    content = "# React Dashboard\n\nA modern web application for data visualization."
    
    # Should return Insights object
    insights = engine.reason(signals, content)
    
    assert hasattr(insights, 'problem')
    assert hasattr(insights, 'solution')
    assert hasattr(insights, 'value_proposition')
    assert hasattr(insights, 'target_users')
    assert hasattr(insights, 'key_features')
    assert hasattr(insights, 'current_focus')
    assert hasattr(insights, 'future_plans')
    
    assert isinstance(insights.key_features, list)
    assert len(insights.problem) > 0
    assert len(insights.solution) > 0
    
    # Should contain web app specific insights
    assert "web" in insights.problem.lower() or "application" in insights.problem.lower()


def test_simple_reasoning_cli_project():
    """Test simple reasoning for CLI project."""
    engine = SimpleLLMReasoningEngine()
    
    signals = TechnicalSignals(
        languages=["Python"],
        frameworks=["Typer"],
        project_type=ProjectType.CLI,
        maturity=ProjectStatus.PRODUCTION,
        activity_level="medium",
        tech_stack=["Python", "Typer"]
    )
    
    content = "# CLI Tool\n\nA command-line interface for file processing."
    
    insights = engine.reason(signals, content)
    
    # Should contain CLI-specific insights
    assert "cli" in insights.problem.lower() or "command" in insights.problem.lower()
    assert "developers" in insights.target_users.lower()


def test_simple_reasoning_api_project():
    """Test simple reasoning for API project."""
    engine = SimpleLLMReasoningEngine()
    
    signals = TechnicalSignals(
        languages=["Python"],
        frameworks=["FastAPI"],
        project_type=ProjectType.API,
        maturity=ProjectStatus.MVP,
        activity_level="high",
        tech_stack=["Python", "FastAPI"]
    )
    
    content = "# REST API\n\nA RESTful API for user management with authentication."
    
    insights = engine.reason(signals, content)
    
    # Should contain API-specific insights
    assert "api" in insights.problem.lower() or "endpoint" in insights.problem.lower()
    assert "backend" in insights.target_users.lower() or "api" in insights.target_users.lower()


def test_content_analysis_features():
    """Test that content analysis detects features correctly."""
    engine = SimpleLLMReasoningEngine()
    
    signals = TechnicalSignals(
        languages=["Python"],
        frameworks=[],
        project_type=ProjectType.OTHER,
        maturity=ProjectStatus.PROTOTYPE,
        activity_level="low",
        tech_stack=["Python"]
    )
    
    # Content with various features
    content = """
    # Project with Features
    
    This project includes:
    - Docker support
    - TypeScript for type safety
    - Authentication system
    - Database integration
    - Comprehensive test suite
    """
    
    insights = engine.reason(signals, content)
    
    # Should detect features from content
    features_text = " ".join(insights.key_features).lower()
    assert any(keyword in features_text for keyword in ["docker", "container"])
    assert any(keyword in features_text for keyword in ["type", "typescript"])
    assert any(keyword in features_text for keyword in ["auth", "authentication"])
    assert any(keyword in features_text for keyword in ["database", "db"])
    assert any(keyword in features_text for keyword in ["test", "testing"])


def test_invalid_provider_fallback():
    """Test that invalid provider names fall back to simple."""
    engine = create_reasoning_engine("invalid_provider", interactive=False)
    assert isinstance(engine, SimpleLLMReasoningEngine)


if __name__ == "__main__":
    pytest.main([__file__])