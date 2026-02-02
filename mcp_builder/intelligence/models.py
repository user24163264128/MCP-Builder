"""Data models for intelligence layer."""

from dataclasses import dataclass
from typing import List


@dataclass
class Insights:
    """AI-generated insights about the project."""
    problem: str
    solution: str
    value_proposition: str
    target_users: str
    key_features: List[str]
    current_focus: str
    future_plans: str