"""Local LLM reasoning engine using Python-based models."""

import json
import logging
from typing import Optional

try:
    import transformers
    from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

from .base import ReasoningEngine
from .models import Insights
from ..analyzers.models import TechnicalSignals

logger = logging.getLogger(__name__)


class LocalLLMReasoningEngine(ReasoningEngine):
    """Local LLM reasoning engine using Hugging Face transformers."""
    
    def __init__(self, model_name: str = "microsoft/DialoGPT-medium"):
        """Initialize local LLM reasoning engine.
        
        Args:
            model_name: Hugging Face model name to use
        """
        if not TRANSFORMERS_AVAILABLE:
            raise ImportError("Transformers package not installed. Run: pip install transformers torch")
        
        self.model_name = model_name
        self.pipeline = None
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the local model pipeline."""
        try:
            logger.info(f"Loading local model: {self.model_name}")
            
            # Use a lightweight model for text generation
            self.pipeline = pipeline(
                "text-generation",
                model=self.model_name,
                tokenizer=self.model_name,
                max_length=1000,
                do_sample=True,
                temperature=0.7,
                pad_token_id=50256  # GPT-2 pad token
            )
            
            logger.info("Local model loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load local model: {e}")
            self.pipeline = None
    
    def reason(self, signals: TechnicalSignals, content: str) -> Insights:
        """Generate insights using local LLM."""
        if not self.pipeline:
            logger.warning("Local model not available, using fallback")
            return self._fallback_insights()
        
        try:
            prompt = self._build_prompt(signals, content)
            
            # Generate response using local model
            response = self.pipeline(
                prompt,
                max_length=len(prompt) + 500,
                num_return_sequences=1,
                temperature=0.3,
                do_sample=True
            )
            
            generated_text = response[0]['generated_text']
            # Extract only the generated part (after the prompt)
            result = generated_text[len(prompt):].strip()
            
            return self._parse_response(result)
            
        except Exception as e:
            logger.error(f"Local LLM reasoning failed: {e}")
            return self._fallback_insights()
    
    def _build_prompt(self, signals: TechnicalSignals, content: str) -> str:
        """Build a simple prompt for local models."""
        return f"""Analyze this software project:

Languages: {', '.join(signals.languages)}
Type: {signals.project_type.value}
Content: {content[:2000]}

What problem does this solve?"""
    
    def _parse_response(self, response: str) -> Insights:
        """Parse local model response into structured insights."""
        # Local models may not produce structured JSON, so we extract key information
        lines = response.split('\n')
        
        # Try to extract meaningful information from the response
        problem = "Addresses specific technical challenges in software development."
        solution = "Provides a comprehensive solution using modern development practices."
        
        # Look for problem/solution indicators in the response
        for line in lines:
            line = line.strip()
            if line and len(line) > 20:
                if any(word in line.lower() for word in ['problem', 'challenge', 'issue']):
                    problem = line[:200]
                elif any(word in line.lower() for word in ['solution', 'solves', 'addresses']):
                    solution = line[:200]
        
        return Insights(
            problem=problem,
            solution=solution,
            value_proposition="Improves development efficiency and code quality.",
            target_users="Software developers and engineering teams.",
            key_features=[
                "Modern architecture",
                "Developer-friendly design",
                "Reliable performance",
                "Easy integration"
            ],
            current_focus="Enhancing core functionality and user experience.",
            future_plans="Expanding features and improving performance."
        )
    
    def _fallback_insights(self) -> Insights:
        """Fallback insights when local LLM fails."""
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


class SimpleLLMReasoningEngine(ReasoningEngine):
    """Simple rule-based reasoning engine that mimics LLM behavior."""
    
    def reason(self, signals: TechnicalSignals, content: str) -> Insights:
        """Generate insights using rule-based analysis."""
        
        # Analyze project type and generate specific insights
        project_insights = self._analyze_project_type(signals)
        content_insights = self._analyze_content(content)
        
        return Insights(
            problem=project_insights["problem"],
            solution=project_insights["solution"],
            value_proposition=project_insights["value_proposition"],
            target_users=project_insights["target_users"],
            key_features=content_insights["features"],
            current_focus=content_insights["current_focus"],
            future_plans=project_insights["future_plans"]
        )
    
    def _analyze_project_type(self, signals: TechnicalSignals) -> dict:
        """Generate insights based on project type."""
        
        if signals.project_type.value == "web_app":
            return {
                "problem": "Building modern web applications requires managing complex frontend and backend interactions, state management, and user experience optimization.",
                "solution": "This web application provides a streamlined architecture with modern frameworks and best practices for scalable development.",
                "value_proposition": "Delivers fast, responsive user experiences with maintainable code architecture.",
                "target_users": "Web developers, frontend engineers, and product teams building user-facing applications.",
                "future_plans": "Expanding cross-platform support and adding advanced user interface components."
            }
        elif signals.project_type.value == "cli":
            return {
                "problem": "Developers need efficient command-line tools that are easy to use, well-documented, and integrate seamlessly into existing workflows.",
                "solution": "This CLI tool provides intuitive commands with comprehensive help documentation and robust error handling.",
                "value_proposition": "Streamlines development workflows and automates repetitive tasks with reliable command-line interface.",
                "target_users": "Software developers, DevOps engineers, and system administrators.",
                "future_plans": "Adding more automation features and improving cross-platform compatibility."
            }
        elif signals.project_type.value == "api":
            return {
                "problem": "Creating robust APIs requires careful design of endpoints, data validation, authentication, and comprehensive documentation.",
                "solution": "This API provides well-structured endpoints with automatic validation, clear documentation, and scalable architecture.",
                "value_proposition": "Enables reliable data exchange and integration with comprehensive API documentation and testing tools.",
                "target_users": "Backend developers, API consumers, and integration teams.",
                "future_plans": "Expanding API endpoints and improving performance optimization."
            }
        elif signals.project_type.value == "library":
            return {
                "problem": "Developers need reusable, well-tested libraries that solve common problems without adding unnecessary complexity.",
                "solution": "This library provides clean APIs, comprehensive documentation, and thorough testing for reliable integration.",
                "value_proposition": "Accelerates development by providing tested, reusable components with clear documentation.",
                "target_users": "Software developers and engineering teams building applications.",
                "future_plans": "Adding new features and maintaining backward compatibility."
            }
        else:
            return {
                "problem": "This project addresses specific technical challenges in its domain with innovative solutions.",
                "solution": "Implements comprehensive functionality using modern development practices and proven patterns.",
                "value_proposition": "Provides reliable, efficient solutions that improve productivity and code quality.",
                "target_users": "Developers, engineers, and technical professionals in the relevant domain.",
                "future_plans": "Expanding capabilities and improving user experience based on community feedback."
            }
    
    def _analyze_content(self, content: str) -> dict:
        """Analyze repository content for additional insights."""
        content_lower = content.lower()
        
        features = []
        current_focus = "Improving core functionality and user experience."
        
        # Detect common features from content
        if "test" in content_lower or "spec" in content_lower:
            features.append("Comprehensive testing suite")
        
        if "docker" in content_lower:
            features.append("Containerized deployment")
        
        if "api" in content_lower or "endpoint" in content_lower:
            features.append("RESTful API design")
        
        if "react" in content_lower or "vue" in content_lower or "angular" in content_lower:
            features.append("Modern frontend framework")
        
        if "typescript" in content_lower:
            features.append("Type-safe development")
        
        if "auth" in content_lower or "login" in content_lower:
            features.append("Authentication system")
        
        if "database" in content_lower or "db" in content_lower:
            features.append("Database integration")
        
        # Default features if none detected
        if not features:
            features = [
                "Clean, maintainable code architecture",
                "Comprehensive documentation",
                "User-friendly interface",
                "Reliable performance"
            ]
        
        # Analyze current focus based on recent activity indicators
        if "todo" in content_lower or "fixme" in content_lower:
            current_focus = "Addressing technical debt and implementing planned improvements."
        elif "beta" in content_lower or "alpha" in content_lower:
            current_focus = "Stabilizing features and preparing for production release."
        elif "v1" in content_lower or "release" in content_lower:
            current_focus = "Finalizing features and ensuring production readiness."
        
        return {
            "features": features[:5],  # Limit to 5 features
            "current_focus": current_focus
        }