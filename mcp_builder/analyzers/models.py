"""Data models for analyzers."""

from dataclasses import dataclass
from typing import List

from mcp_builder.mcp.schemas import ProjectStatus, ProjectType


@dataclass
class TechnicalSignals:
    """Extracted technical signals from repository."""
    languages: List[str]
    frameworks: List[str]
    project_type: ProjectType
    maturity: ProjectStatus
    activity_level: str  # 'high', 'medium', 'low'
    tech_stack: List[str]