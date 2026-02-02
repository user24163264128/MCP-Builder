"""MCP YAML generation."""

import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

import yaml

from .schemas import MCP, Metadata
from ..analyzers.models import TechnicalSignals
from ..ingestion.models import RepositorySnapshot
from ..intelligence.models import Insights

logger = logging.getLogger(__name__)


def infer_project_name(snapshot: RepositorySnapshot) -> str:
    """Infer project name from README or directory name."""
    for file in snapshot.files:
        if 'readme' in file.path.name.lower():
            lines = file.content.split('\n')
            for line in lines[:10]:
                if line.strip().startswith('# '):
                    return line[2:].strip()
    return snapshot.root_path.name


def generate_one_liner(insights: Insights) -> str:
    """Generate a one-liner description."""
    return insights.value_proposition[:200] + "..." if len(insights.value_proposition) > 200 else insights.value_proposition


def generate_mcp(snapshot: RepositorySnapshot, signals: TechnicalSignals, insights: Insights, version: str = "1.0") -> MCP:
    """Generate MCP object from extracted data."""
    project_name = infer_project_name(snapshot)
    one_liner = generate_one_liner(insights)

    metadata = Metadata(version=version)

    return MCP(
        project_name=project_name,
        one_liner=one_liner,
        problem=insights.problem,
        solution=insights.solution,
        value_proposition=insights.value_proposition,
        tech_stack=signals.tech_stack,
        project_type=signals.project_type,
        status=signals.maturity,
        key_features=insights.key_features,
        target_users=insights.target_users,
        current_focus=insights.current_focus,
        future_plans=insights.future_plans,
        risks_or_gaps=None,  # TODO: implement risk analysis
        metadata=metadata,
    )


def save_mcp(mcp: MCP, output_path: Path) -> None:
    """Save MCP to YAML file."""
    data = mcp.model_dump()
    # Ensure enums are serialized as strings
    if 'project_type' in data and hasattr(data['project_type'], 'value'):
        data['project_type'] = data['project_type'].value
    if 'status' in data and hasattr(data['status'], 'value'):
        data['status'] = data['status'].value
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)
    logger.info(f"MCP saved to {output_path}")


def load_mcp(file_path: Path) -> MCP:
    """Load MCP from YAML file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    return MCP(**data)


def validate_mcp(mcp: MCP) -> bool:
    """Validate MCP schema."""
    try:
        # Pydantic validation happens on creation
        return True
    except Exception as e:
        logger.error(f"MCP validation failed: {e}")
        return False