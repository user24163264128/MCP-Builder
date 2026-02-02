"""Mock reasoning engine for testing and offline mode."""

from .base import ReasoningEngine
from .models import Insights


class MockReasoningEngine(ReasoningEngine):
    """Mock implementation that returns predefined insights."""

    def reason(self, signals, content: str) -> Insights:
        """Return mock insights regardless of input."""
        return Insights(
            problem="This project addresses a significant challenge in its domain by providing innovative solutions to common pain points.",
            solution="The project implements a comprehensive approach using best practices and modern technologies to deliver reliable results.",
            value_proposition="Offers substantial benefits including improved efficiency, reduced complexity, and enhanced user experience.",
            target_users="Developers, engineers, and organizations looking to streamline their workflows and improve productivity.",
            key_features=[
                "Modular architecture for easy customization",
                "Comprehensive documentation and examples",
                "Strong type safety and error handling",
                "Extensible plugin system",
                "High performance and scalability"
            ],
            current_focus="Enhancing core functionality, improving documentation, and gathering user feedback for future improvements.",
            future_plans="Expand platform support, add advanced features, and build a vibrant community ecosystem.",
        )