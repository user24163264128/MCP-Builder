"""CLI entrypoint for MCP Builder."""

import logging
import os
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from ..analyzers.signals import extract_signals
from ..ingestion.walker import ingest_repository
from ..intelligence.factory import create_reasoning_engine, list_available_providers
from ..intelligence.selector import select_content
from ..mcp.generator import generate_mcp, load_mcp, save_mcp, validate_mcp
from ..github.client import GitHubClient
from ..github.enricher import GitHubEnricher

app = typer.Typer()
console = Console()

# Configure logging
logging.basicConfig(level=logging.INFO)


@app.command()
def init(
    repo_path: str,
    github_token: Optional[str] = typer.Option(None, "--github-token", "-t", help="GitHub API token for enhanced metadata"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path (default: mcp.yaml in current dir)"),
    ai_provider: str = typer.Option("auto", "--ai-provider", help="AI provider: auto, openai, anthropic, local, simple, mock"),
    ai_model: Optional[str] = typer.Option(None, "--ai-model", help="Specific AI model to use"),
    openai_key: Optional[str] = typer.Option(None, "--openai-key", help="OpenAI API key"),
    anthropic_key: Optional[str] = typer.Option(None, "--anthropic-key", help="Anthropic API key"),
    no_interactive: bool = typer.Option(False, "--no-interactive", help="Disable interactive prompts")
) -> None:
    """Generate initial MCP YAML for a repository (local path or GitHub URL)."""
    try:
        # Get GitHub token from environment if not provided
        if not github_token:
            github_token = os.getenv("GITHUB_TOKEN")
        
        console.print(f"[bold blue]Analyzing repository:[/bold blue] {repo_path}")
        
        if github_token:
            console.print("[dim]Using GitHub token for enhanced metadata[/dim]")

        snapshot = ingest_repository(repo_path, github_token)
        signals = extract_signals(snapshot)
        
        # If this is a GitHub repository, enrich with GitHub data
        github_metrics = None
        if snapshot.github_url and github_token:
            try:
                github_client = GitHubClient(github_token)
                enricher = GitHubEnricher(github_client)
                snapshot, github_metrics = enricher.enrich_snapshot(snapshot, snapshot.github_url)
                
                # Display GitHub metrics
                console.print(f"[dim]GitHub metrics: {github_metrics.repository.stars} stars, "
                             f"{github_metrics.repository.forks} forks, "
                             f"{len(github_metrics.contributors)} contributors[/dim]")
            except Exception as e:
                console.print(f"[yellow]Warning: Could not fetch GitHub metadata: {e}[/yellow]")

        # Create AI reasoning engine
        api_key = openai_key or anthropic_key
        engine = create_reasoning_engine(ai_provider, api_key, ai_model, interactive=not no_interactive)
        
        # Show which reasoning engine is being used
        engine_name = engine.__class__.__name__.replace("ReasoningEngine", "").replace("LLM", " LLM")
        console.print(f"[dim]Using {engine_name} reasoning engine[/dim]")
        
        content = select_content(snapshot)
        insights = engine.reason(signals, content)
        mcp = generate_mcp(snapshot, signals, insights)

        # Determine output path
        if output:
            output_path = Path(output)
        elif snapshot.is_github_clone:
            # For GitHub repos, save to current directory
            output_path = Path.cwd() / "mcp.yaml"
        else:
            # For local repos, save in the repo directory
            output_path = Path(repo_path) / "mcp.yaml"
        
        save_mcp(mcp, output_path)

        console.print(f"[green]✓ MCP generated successfully at {output_path}[/green]")
        
        if github_metrics:
            console.print(f"[dim]Repository popularity score: {github_metrics.popularity_score:.1f}[/dim]")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def update(
    repo_path: str,
    github_token: Optional[str] = typer.Option(None, "--github-token", "-t", help="GitHub API token for enhanced metadata")
) -> None:
    """Intelligently update existing MCP YAML."""
    # TODO: Implement diff-based updates
    console.print("[yellow]Update functionality not yet implemented. Running init instead.[/yellow]")
    init(repo_path, github_token)


@app.command()
def analyze(
    repo_path: str,
    github_token: Optional[str] = typer.Option(None, "--github-token", "-t", help="GitHub API token for enhanced metadata")
) -> None:
    """Analyze repository and show insights without generating files."""
    try:
        # Get GitHub token from environment if not provided
        if not github_token:
            github_token = os.getenv("GITHUB_TOKEN")
            
        snapshot = ingest_repository(repo_path, github_token)
        signals = extract_signals(snapshot)
        
        # If this is a GitHub repository, enrich with GitHub data
        github_metrics = None
        if snapshot.github_url and github_token:
            try:
                github_client = GitHubClient(github_token)
                enricher = GitHubEnricher(github_client)
                snapshot, github_metrics = enricher.enrich_snapshot(snapshot, snapshot.github_url)
            except Exception as e:
                console.print(f"[yellow]Warning: Could not fetch GitHub metadata: {e}[/yellow]")
        
        engine = MockReasoningEngine()
        content = select_content(snapshot)
        insights = engine.reason(signals, content)

        table = Table(title="Repository Analysis")
        table.add_column("Aspect", style="cyan")
        table.add_column("Details", style="white")

        table.add_row("Project Type", signals.project_type.value)
        table.add_row("Maturity", signals.maturity.value)
        table.add_row("Activity Level", signals.activity_level)
        table.add_row("Languages", ", ".join(signals.languages))
        table.add_row("Frameworks", ", ".join(signals.frameworks))
        table.add_row("Tech Stack", ", ".join(signals.tech_stack))
        
        # Add GitHub-specific metrics if available
        if github_metrics:
            table.add_row("GitHub Stars", str(github_metrics.repository.stars))
            table.add_row("GitHub Forks", str(github_metrics.repository.forks))
            table.add_row("Contributors", str(len(github_metrics.contributors)))
            table.add_row("Popularity Score", f"{github_metrics.popularity_score:.1f}")
            table.add_row("Activity Level (GitHub)", github_metrics.activity_level)
        
        table.add_row("Problem", insights.problem[:100] + "..." if len(insights.problem) > 100 else insights.problem)
        table.add_row("Solution", insights.solution[:100] + "..." if len(insights.solution) > 100 else insights.solution)

        console.print(table)

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def github(
    github_url: str,
    github_token: Optional[str] = typer.Option(None, "--github-token", "-t", help="GitHub API token (or set GITHUB_TOKEN env var)"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path (default: mcp.yaml)"),
    ai_provider: str = typer.Option("auto", "--ai-provider", help="AI provider: auto, openai, anthropic, local, simple, mock"),
    ai_model: Optional[str] = typer.Option(None, "--ai-model", help="Specific AI model to use"),
    openai_key: Optional[str] = typer.Option(None, "--openai-key", help="OpenAI API key"),
    anthropic_key: Optional[str] = typer.Option(None, "--anthropic-key", help="Anthropic API key"),
    no_interactive: bool = typer.Option(False, "--no-interactive", help="Disable interactive prompts")
) -> None:
    """Generate MCP YAML specifically for a GitHub repository with enhanced metadata."""
    try:
        # Get GitHub token from environment if not provided
        if not github_token:
            github_token = os.getenv("GITHUB_TOKEN")
            if not github_token:
                console.print("[yellow]Warning: No GitHub token provided. Some features may be limited.[/yellow]")
                console.print("[dim]Set GITHUB_TOKEN environment variable or use --github-token flag[/dim]")
        
        console.print(f"[bold blue]Analyzing GitHub repository:[/bold blue] {github_url}")
        
        # Validate GitHub URL format
        if "github.com" not in github_url.lower():
            console.print("[red]Error: Please provide a valid GitHub URL[/red]")
            raise typer.Exit(1)

        snapshot = ingest_repository(github_url, github_token)
        signals = extract_signals(snapshot)
        
        # Enrich with GitHub data
        github_metrics = None
        if github_token:
            try:
                github_client = GitHubClient(github_token)
                enricher = GitHubEnricher(github_client)
                snapshot, github_metrics = enricher.enrich_snapshot(snapshot, github_url)
                
                # Display comprehensive GitHub metrics
                console.print(f"[bold green]GitHub Repository Metrics:[/bold green]")
                console.print(f"  Stars: {github_metrics.repository.stars}")
                console.print(f"  Forks: {github_metrics.repository.forks}")
                console.print(f"  Contributors: {len(github_metrics.contributors)}")
                console.print(f"  Open Issues: {github_metrics.repository.open_issues}")
                console.print(f"  Primary Language: {github_metrics.repository.language or 'Not specified'}")
                console.print(f"  License: {github_metrics.repository.license or 'None'}")
                console.print(f"  Activity Level: {github_metrics.activity_level}")
                console.print(f"  Popularity Score: {github_metrics.popularity_score:.1f}")
                
                if github_metrics.repository.topics:
                    console.print(f"  Topics: {', '.join(github_metrics.repository.topics)}")
                    
            except Exception as e:
                console.print(f"[yellow]Warning: Could not fetch GitHub metadata: {e}[/yellow]")

        # Create AI reasoning engine
        api_key = openai_key or anthropic_key
        engine = create_reasoning_engine(ai_provider, api_key, ai_model, interactive=not no_interactive)
        
        # Show which reasoning engine is being used
        engine_name = engine.__class__.__name__.replace("ReasoningEngine", "").replace("LLM", " LLM")
        console.print(f"[dim]Using {engine_name} reasoning engine[/dim]")
        
        content = select_content(snapshot)
        insights = engine.reason(signals, content)
        mcp = generate_mcp(snapshot, signals, insights)

        # Determine output path
        output_path = Path(output) if output else Path.cwd() / "mcp.yaml"
        save_mcp(mcp, output_path)

        console.print(f"[green]✓ MCP generated successfully at {output_path}[/green]")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def providers() -> None:
    """List available AI providers and their status."""
    try:
        providers = list_available_providers()
        
        table = Table(title="Available AI Providers")
        table.add_column("Provider", style="cyan")
        table.add_column("Package", style="white")
        table.add_column("Installed", style="green")
        table.add_column("API Key", style="yellow")
        table.add_column("Status", style="white")
        
        for name, info in providers.items():
            installed = "✓" if info["available"] else "✗"
            has_key = "✓" if info["has_key"] else "✗"
            
            if name in ["mock", "simple", "local"]:
                if name == "mock":
                    status = "Basic templates"
                elif name == "simple":
                    status = "Rule-based reasoning"
                else:
                    status = "Local models" if info["available"] else "Need installation"
            elif info["available"] and info["has_key"]:
                status = "Ready to use"
            elif info["available"] and not info["has_key"]:
                status = "Need API key"
            else:
                status = "Need installation"
            
            table.add_row(name.title(), info["package"], installed, has_key, status)
        
        console.print(table)
        
        console.print("\n[bold]Setup Instructions:[/bold]")
        console.print("• [green]OpenAI[/green]: pip install openai && export OPENAI_API_KEY=your_key")
        console.print("• [blue]Anthropic[/blue]: pip install anthropic && export ANTHROPIC_API_KEY=your_key")
        console.print("• [yellow]Local LLM[/yellow]: pip install transformers torch (downloads models automatically)")
        console.print("• [cyan]Simple[/cyan]: No setup required (intelligent rule-based analysis)")
        console.print("• [dim]Mock[/dim]: No setup required (basic templates)")
        
        console.print("\n[bold]Recommendations:[/bold]")
        console.print("• [green]Best quality[/green]: OpenAI GPT-4 or Anthropic Claude")
        console.print("• [yellow]Best cost[/yellow]: OpenAI GPT-4o-mini or Simple reasoning")
        console.print("• [blue]Privacy-focused[/blue]: Local LLM or Simple reasoning")
        console.print("• [cyan]No internet[/cyan]: Simple reasoning (works offline)")
        
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def rate_limit(
    github_token: Optional[str] = typer.Option(None, "--github-token", "-t", help="GitHub API token")
) -> None:
    """Check GitHub API rate limit status."""
    try:
        if not github_token:
            github_token = os.getenv("GITHUB_TOKEN")
            if not github_token:
                console.print("[red]Error: GitHub token required. Set GITHUB_TOKEN env var or use --github-token[/red]")
                raise typer.Exit(1)
        
        github_client = GitHubClient(github_token)
        rate_limit_info = github_client.check_rate_limit()
        
        if rate_limit_info:
            core = rate_limit_info.get("rate", {})
            console.print(f"[bold blue]GitHub API Rate Limit Status:[/bold blue]")
            console.print(f"  Remaining: {core.get('remaining', 'Unknown')}")
            console.print(f"  Limit: {core.get('limit', 'Unknown')}")
            console.print(f"  Reset: {core.get('reset', 'Unknown')}")
        else:
            console.print("[yellow]Could not fetch rate limit information[/yellow]")
            
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
    """Validate MCP YAML file against schema."""
    path = Path(mcp_path)
    if not path.exists():
        console.print(f"[red]MCP file not found:[/red] {mcp_path}")
        raise typer.Exit(1)

    try:
        mcp = load_mcp(path)
        if validate_mcp(mcp):
            console.print("[green]✓ MCP file is valid[/green]")
        else:
            console.print("[red]✗ MCP file is invalid[/red]")
            raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Validation error:[/red] {e}")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()

@app.command()
def validate(mcp_path: str) -> None:
    """Validate MCP YAML file against schema."""
    path = Path(mcp_path)
    if not path.exists():
        console.print(f"[red]MCP file not found:[/red] {mcp_path}")
        raise typer.Exit(1)

    try:
        mcp = load_mcp(path)
        if validate_mcp(mcp):
            console.print("[green]✓ MCP file is valid[/green]")
        else:
            console.print("[red]✗ MCP file is invalid[/red]")
            raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Validation error:[/red] {e}")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()