"""Schemas for MCP YAML data structures."""

from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class ProjectType(str, Enum):
    """Enumeration of possible project types."""
    CLI = "cli"
    API = "api"
    WEB_APP = "web_app"
    ML = "ml"
    AUTOMATION = "automation"
    LIBRARY = "library"
    OTHER = "other"


class ProjectStatus(str, Enum):
    """Enumeration of project maturity stages."""
    PROTOTYPE = "prototype"
    MVP = "mvp"
    PRODUCTION = "production"


class Metadata(BaseModel):
    """Metadata for MCP YAML."""
    version: str = Field(..., description="Version of the MCP schema")
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Timestamp of generation")


class MCP(BaseModel):
    """Main MCP YAML schema."""
    project_name: str = Field(..., description="Name of the project")
    one_liner: str = Field(..., description="Brief one-line description")
    problem: str = Field(..., description="Problem the project solves")
    solution: str = Field(..., description="How the project solves the problem")
    value_proposition: str = Field(..., description="Value proposition for users")
    tech_stack: List[str] = Field(default_factory=list, description="List of technologies used")
    project_type: ProjectType = Field(..., description="Type of the project")
    status: ProjectStatus = Field(..., description="Maturity status of the project")
    key_features: List[str] = Field(default_factory=list, description="Key features of the project")
    target_users: str = Field(..., description="Target user base")
    current_focus: str = Field(..., description="Current development focus")
    future_plans: str = Field(..., description="Future plans for the project")
    risks_or_gaps: Optional[str] = Field(None, description="Known risks or gaps")
    metadata: Metadata = Field(..., description="Metadata about the MCP generation")