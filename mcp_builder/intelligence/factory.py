"""Factory for creating reasoning engines."""

import os
import logging
from typing import Optional

import typer
from rich.console import Console
from rich.prompt import Prompt, Confirm

from .base import ReasoningEngine
from .mock import MockReasoningEngine

logger = logging.getLogger(__name__)
console = Console()


def create_reasoning_engine(
    provider: str = "auto",
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    interactive: bool = True
) -> ReasoningEngine:
    """Create a reasoning engine based on provider and availability.
    
    Args:
        provider: AI provider ("openai", "anthropic", "local", "simple", "mock", or "auto")
        api_key: API key for the provider
        model: Specific model to use
        interactive: Whether to prompt user for missing configuration
        
    Returns:
        Configured reasoning engine
    """
    
    if provider == "mock":
        return MockReasoningEngine()
    
    if provider == "simple":
        return _create_simple_engine()
    
    if provider == "local":
        return _create_local_llm_engine(model, interactive)
    
    # Auto-detect available providers
    if provider == "auto":
        provider = _detect_available_provider(interactive)
    
    if provider == "openai":
        return _create_openai_engine(api_key, model, interactive)
    elif provider == "anthropic":
        return _create_anthropic_engine(api_key, model, interactive)
    elif provider == "simple":
        return _create_simple_engine()
    elif provider == "local":
        return _create_local_llm_engine(model, interactive)
    else:
        logger.warning(f"Unknown provider '{provider}', falling back to simple reasoning")
        return _create_simple_engine()


def _detect_available_provider(interactive: bool = True) -> str:
    """Detect which AI provider is available based on API keys."""
    
    # Check for OpenAI
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        try:
            from .openai_engine import OpenAIReasoningEngine
            logger.info("Using OpenAI reasoning engine")
            return "openai"
        except ImportError:
            logger.warning("OpenAI API key found but package not installed")
    
    # Check for Anthropic
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    if anthropic_key:
        try:
            from .anthropic_engine import AnthropicReasoningEngine
            logger.info("Using Anthropic reasoning engine")
            return "anthropic"
        except ImportError:
            logger.warning("Anthropic API key found but package not installed")
    
    # Check for local LLM capability
    try:
        import transformers
        if interactive:
            console.print("[yellow]No cloud AI provider found.[/yellow]")
            use_local = Confirm.ask("Would you like to use a local LLM? (requires downloading models)")
            if use_local:
                return "local"
    except ImportError:
        pass
    
    # Offer interactive setup if no provider is available
    if interactive:
        return _interactive_provider_setup()
    
    logger.info("No AI provider available, using simple reasoning engine")
    return "simple"


def _interactive_provider_setup() -> str:
    """Interactive setup for AI providers."""
    console.print("\n[bold blue]AI Provider Setup[/bold blue]")
    console.print("No AI provider is currently configured. Choose an option:")
    console.print("1. [green]OpenAI[/green] (recommended, requires API key)")
    console.print("2. [blue]Anthropic[/blue] (high quality, requires API key)")
    console.print("3. [yellow]Local LLM[/yellow] (free, downloads models)")
    console.print("4. [cyan]Simple reasoning[/cyan] (rule-based, no AI)")
    console.print("5. [dim]Mock reasoning[/dim] (basic templates)")
    
    choice = Prompt.ask("Select option", choices=["1", "2", "3", "4", "5"], default="4")
    
    if choice == "1":
        return _setup_openai_interactive()
    elif choice == "2":
        return _setup_anthropic_interactive()
    elif choice == "3":
        return "local"
    elif choice == "4":
        return "simple"
    else:
        return "mock"


def _setup_openai_interactive() -> str:
    """Interactive OpenAI setup."""
    console.print("\n[bold green]OpenAI Setup[/bold green]")
    console.print("You need an OpenAI API key. Get one at: https://platform.openai.com/api-keys")
    
    if Confirm.ask("Do you have an OpenAI API key?"):
        api_key = Prompt.ask("Enter your OpenAI API key", password=True)
        if api_key:
            # Set environment variable for this session
            os.environ["OPENAI_API_KEY"] = api_key
            console.print("[green]✓ OpenAI API key configured for this session[/green]")
            console.print("[dim]Tip: Add 'export OPENAI_API_KEY=your_key' to your shell profile for permanent setup[/dim]")
            return "openai"
    
    console.print("[yellow]Falling back to simple reasoning[/yellow]")
    return "simple"


def _setup_anthropic_interactive() -> str:
    """Interactive Anthropic setup."""
    console.print("\n[bold blue]Anthropic Setup[/bold blue]")
    console.print("You need an Anthropic API key. Get one at: https://console.anthropic.com/")
    
    if Confirm.ask("Do you have an Anthropic API key?"):
        api_key = Prompt.ask("Enter your Anthropic API key", password=True)
        if api_key:
            # Set environment variable for this session
            os.environ["ANTHROPIC_API_KEY"] = api_key
            console.print("[green]✓ Anthropic API key configured for this session[/green]")
            console.print("[dim]Tip: Add 'export ANTHROPIC_API_KEY=your_key' to your shell profile for permanent setup[/dim]")
            return "anthropic"
    
    console.print("[yellow]Falling back to simple reasoning[/yellow]")
    return "simple"


def _create_openai_engine(api_key: Optional[str], model: Optional[str], interactive: bool) -> ReasoningEngine:
    """Create OpenAI reasoning engine."""
    try:
        from .openai_engine import OpenAIReasoningEngine
        
        # Use provided key or environment variable
        if not api_key:
            api_key = os.getenv("OPENAI_API_KEY")
        
        if not api_key and interactive:
            console.print("[yellow]No OpenAI API key found[/yellow]")
            if Confirm.ask("Would you like to enter your OpenAI API key now?"):
                api_key = Prompt.ask("Enter your OpenAI API key", password=True)
                if api_key:
                    os.environ["OPENAI_API_KEY"] = api_key
        
        if not api_key:
            logger.warning("No OpenAI API key provided, falling back to simple reasoning")
            return _create_simple_engine()
        
        # Use provided model or default
        if not model:
            model = "gpt-4o-mini"  # Cost-effective default
        
        return OpenAIReasoningEngine(api_key=api_key, model=model)
        
    except ImportError:
        if interactive:
            console.print("[red]OpenAI package not installed[/red]")
            if Confirm.ask("Would you like to install it? (pip install openai)"):
                import subprocess
                try:
                    subprocess.check_call(["pip", "install", "openai"])
                    console.print("[green]✓ OpenAI package installed[/green]")
                    return _create_openai_engine(api_key, model, False)
                except subprocess.CalledProcessError:
                    console.print("[red]Failed to install OpenAI package[/red]")
        
        logger.error("OpenAI package not installed. Run: pip install openai")
        return _create_simple_engine()


def _create_anthropic_engine(api_key: Optional[str], model: Optional[str], interactive: bool) -> ReasoningEngine:
    """Create Anthropic reasoning engine."""
    try:
        from .anthropic_engine import AnthropicReasoningEngine
        
        # Use provided key or environment variable
        if not api_key:
            api_key = os.getenv("ANTHROPIC_API_KEY")
        
        if not api_key and interactive:
            console.print("[yellow]No Anthropic API key found[/yellow]")
            if Confirm.ask("Would you like to enter your Anthropic API key now?"):
                api_key = Prompt.ask("Enter your Anthropic API key", password=True)
                if api_key:
                    os.environ["ANTHROPIC_API_KEY"] = api_key
        
        if not api_key:
            logger.warning("No Anthropic API key provided, falling back to simple reasoning")
            return _create_simple_engine()
        
        # Use provided model or default
        if not model:
            model = "claude-3-haiku-20240307"  # Cost-effective default
        
        return AnthropicReasoningEngine(api_key=api_key, model=model)
        
    except ImportError:
        if interactive:
            console.print("[red]Anthropic package not installed[/red]")
            if Confirm.ask("Would you like to install it? (pip install anthropic)"):
                import subprocess
                try:
                    subprocess.check_call(["pip", "install", "anthropic"])
                    console.print("[green]✓ Anthropic package installed[/green]")
                    return _create_anthropic_engine(api_key, model, False)
                except subprocess.CalledProcessError:
                    console.print("[red]Failed to install Anthropic package[/red]")
        
        logger.error("Anthropic package not installed. Run: pip install anthropic")
        return _create_simple_engine()


def _create_local_llm_engine(model: Optional[str], interactive: bool) -> ReasoningEngine:
    """Create local LLM reasoning engine."""
    try:
        from .local_llm import LocalLLMReasoningEngine
        
        if not model:
            if interactive:
                console.print("\n[bold yellow]Local LLM Setup[/bold yellow]")
                console.print("Available models:")
                console.print("1. microsoft/DialoGPT-medium (default, ~350MB)")
                console.print("2. gpt2 (lightweight, ~500MB)")
                console.print("3. distilgpt2 (smallest, ~250MB)")
                
                choice = Prompt.ask("Select model", choices=["1", "2", "3"], default="1")
                model_map = {
                    "1": "microsoft/DialoGPT-medium",
                    "2": "gpt2", 
                    "3": "distilgpt2"
                }
                model = model_map[choice]
            else:
                model = "microsoft/DialoGPT-medium"
        
        console.print(f"[dim]Loading local model: {model}[/dim]")
        return LocalLLMReasoningEngine(model_name=model)
        
    except ImportError:
        if interactive:
            console.print("[red]Transformers package not installed[/red]")
            if Confirm.ask("Would you like to install it? (pip install transformers torch)"):
                import subprocess
                try:
                    subprocess.check_call(["pip", "install", "transformers", "torch"])
                    console.print("[green]✓ Transformers package installed[/green]")
                    return _create_local_llm_engine(model, False)
                except subprocess.CalledProcessError:
                    console.print("[red]Failed to install transformers package[/red]")
        
        logger.error("Transformers package not installed. Run: pip install transformers torch")
        return _create_simple_engine()


def _create_simple_engine() -> ReasoningEngine:
    """Create simple rule-based reasoning engine."""
    from .local_llm import SimpleLLMReasoningEngine
    return SimpleLLMReasoningEngine()


def list_available_providers() -> dict[str, bool]:
    """List available AI providers and their status."""
    providers = {}
    
    # Check OpenAI
    try:
        import openai
        providers["openai"] = {
            "available": True,
            "has_key": bool(os.getenv("OPENAI_API_KEY")),
            "package": "openai"
        }
    except ImportError:
        providers["openai"] = {
            "available": False,
            "has_key": bool(os.getenv("OPENAI_API_KEY")),
            "package": "openai"
        }
    
    # Check Anthropic
    try:
        import anthropic
        providers["anthropic"] = {
            "available": True,
            "has_key": bool(os.getenv("ANTHROPIC_API_KEY")),
            "package": "anthropic"
        }
    except ImportError:
        providers["anthropic"] = {
            "available": False,
            "has_key": bool(os.getenv("ANTHROPIC_API_KEY")),
            "package": "anthropic"
        }
    
    # Check Local LLM
    try:
        import transformers
        providers["local"] = {
            "available": True,
            "has_key": True,
            "package": "transformers"
        }
    except ImportError:
        providers["local"] = {
            "available": False,
            "has_key": True,
            "package": "transformers"
        }
    
    # Simple and Mock are always available
    providers["simple"] = {
        "available": True,
        "has_key": True,
        "package": "built-in"
    }
    
    providers["mock"] = {
        "available": True,
        "has_key": True,
        "package": "built-in"
    }
    
    return providers