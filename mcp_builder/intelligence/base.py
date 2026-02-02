"""Base interface for reasoning engines."""

from abc import ABC, abstractmethod

from .models import Insights
from ..analyzers.models import TechnicalSignals


class ReasoningEngine(ABC):
    """Abstract base class for AI reasoning engines."""

    @abstractmethod
    def reason(self, signals: TechnicalSignals, content: str) -> Insights:
        """Generate project insights from signals and content.

        Args:
            signals: Extracted technical signals
            content: Selected repository content

        Returns:
            Structured insights about the project
        """
        pass