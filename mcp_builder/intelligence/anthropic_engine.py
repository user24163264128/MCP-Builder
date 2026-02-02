"""Anthropic Claude-powered reasoning engine."""

import json
import logging
from typing import Optional

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

from .base import ReasoningEngine
from .models import Insights
from ..analyzers.models import TechnicalSignals

logger = logging.getLogger(__name__)


class AnthropicReasoningEngine(ReasoningEngine):
    """Anthropic Claude-powered reasoning engine for generating project insights."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-haiku-20240307"):
        """Initialize Anthropic reasoning engine.
        
        Args:
            api_key: Anthropic API key (if None, uses environment variable)
            model: Claude model to use
        """
        if not ANTHROPIC_AVAILABLE:
            raise ImportError("Anthropic package not installed. Run: pip install anthropic")
        
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
    
    def reason(self, signals: TechnicalSignals, content: str) -> Insights:
        """Generate insights using Anthropic Claude."""
        try:
            prompt = self._build_prompt(signals, content)
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.3,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            result = response.content[0].text
            return self._parse_response(result)
            
        except Exception as e:
            logger.error(f"Anthropic reasoning failed: {e}")
            # Fallback to mock insights
            return self._fallback_insights()
    
    def _build_prompt(self, signals: TechnicalSignals, content: str) -> str:
        """Build the analysis prompt."""
        return f"""
You are an expert software analyst. Analyze this software repository and provide structured insights.

TECHNICAL SIGNALS:
- Languages: {', '.join(signals.languages)}
- Frameworks: {', '.join(signals.frameworks)}
- Project Type: {signals.project_type.value}
- Maturity: {signals.maturity.value}
- Activity Level: {signals.activity_level}

REPOSITORY CONTENT (first 8000 chars):
{content[:8000]}

Please analyze this repository and respond with a JSON object containing:
{{
    "problem": "What specific problem does this project solve? (1-2 sentences)",
    "solution": "How does this project solve the problem? (1-2 sentences)", 
    "value_proposition": "What value does this provide to users? (1-2 sentences)",
    "target_users": "Who are the primary users of this project? (1 sentence)",
    "key_features": ["List 3-5 key features as short phrases"],
    "current_focus": "What is the current development focus? (1 sentence)",
    "future_plans": "What are likely future plans for this project? (1 sentence)"
}}

Base your analysis on the actual code, documentation, and project structure. Be specific and accurate.
Respond only with the JSON object, no additional text.
"""
    
    def _parse_response(self, response: str) -> Insights:
        """Parse Anthropic response into Insights object."""
        try:
            # Extract JSON from response (handle markdown code blocks)
            if "```json" in response:
                json_start = response.find("```json") + 7
                json_end = response.find("```", json_start)
                json_str = response[json_start:json_end].strip()
            elif "```" in response:
                json_start = response.find("```") + 3
                json_end = response.find("```", json_start)
                json_str = response[json_start:json_end].strip()
            else:
                json_str = response.strip()
            
            data = json.loads(json_str)
            
            return Insights(
                problem=data.get("problem", "Project addresses domain-specific challenges."),
                solution=data.get("solution", "Implements comprehensive solution using modern practices."),
                value_proposition=data.get("value_proposition", "Provides efficiency and reliability benefits."),
                target_users=data.get("target_users", "Developers and technical professionals."),
                key_features=data.get("key_features", ["Modern architecture", "Easy to use", "Well documented"]),
                current_focus=data.get("current_focus", "Improving core functionality and user experience."),
                future_plans=data.get("future_plans", "Expanding features and community adoption.")
            )
            
        except (json.JSONDecodeError, KeyError) as e:
            logger.warning(f"Failed to parse Anthropic response: {e}")
            return self._fallback_insights()
    
    def _fallback_insights(self) -> Insights:
        """Fallback insights when AI fails."""
        return Insights(
            problem="This project addresses specific technical challenges in its domain.",
            solution="The project provides a comprehensive solution using modern development practices.",
            value_proposition="Offers improved efficiency, reliability, and user experience.",
            target_users="Developers, engineers, and technical professionals.",
            key_features=[
                "Modern architecture and design",
                "Comprehensive functionality", 
                "Developer-friendly interface",
                "Reliable performance"
            ],
            current_focus="Enhancing core features and improving documentation.",
            future_plans="Expanding capabilities and growing the user community."
        )