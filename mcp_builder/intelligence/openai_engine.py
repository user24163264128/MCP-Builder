"""OpenAI-powered reasoning engine."""

import json
import logging
from typing import Optional

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from .base import ReasoningEngine
from .models import Insights
from ..analyzers.models import TechnicalSignals

logger = logging.getLogger(__name__)


class OpenAIReasoningEngine(ReasoningEngine):
    """OpenAI GPT-powered reasoning engine for generating project insights."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
        """Initialize OpenAI reasoning engine.
        
        Args:
            api_key: OpenAI API key (if None, uses environment variable)
            model: OpenAI model to use
        """
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI package not installed. Run: pip install openai")
        
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model
    
    def reason(self, signals: TechnicalSignals, content: str) -> Insights:
        """Generate insights using OpenAI GPT."""
        try:
            prompt = self._build_prompt(signals, content)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert software analyst. Analyze the provided repository information and generate structured insights in JSON format."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            result = response.choices[0].message.content
            return self._parse_response(result)
            
        except Exception as e:
            logger.error(f"OpenAI reasoning failed: {e}")
            # Fallback to mock insights
            return self._fallback_insights()
    
    def _build_prompt(self, signals: TechnicalSignals, content: str) -> str:
        """Build the analysis prompt."""
        return f"""
Analyze this software repository and provide structured insights.

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
"""
    
    def _parse_response(self, response: str) -> Insights:
        """Parse OpenAI response into Insights object."""
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
            logger.warning(f"Failed to parse OpenAI response: {e}")
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