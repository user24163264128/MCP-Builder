# AI-Powered MCP Generation

This document shows how to use MCP Builder with AI providers for intelligent repository analysis.

## Quick Start

```bash
# Install with AI capabilities
pip install -e ".[ai]"

# Check available providers
mcp-builder providers

# Use auto-detection (recommended)
mcp-builder init /path/to/repo --ai-provider auto
```

## AI Provider Setup

### OpenAI (Recommended for Cost-Effectiveness)

```bash
# Install OpenAI package
pip install openai

# Set API key
export OPENAI_API_KEY=your_openai_api_key

# Use with auto-detection
mcp-builder github https://github.com/owner/repo

# Or specify explicitly
mcp-builder init /path/to/repo --ai-provider openai --ai-model gpt-4o-mini
```

### Anthropic Claude (Recommended for Accuracy)

```bash
# Install Anthropic package
pip install anthropic

# Set API key
export ANTHROPIC_API_KEY=your_anthropic_api_key

# Use with auto-detection
mcp-builder github https://github.com/owner/repo

# Or specify explicitly
mcp-builder init /path/to/repo --ai-provider anthropic --ai-model claude-3-haiku-20240307
```

## AI Models

### OpenAI Models
- `gpt-4o-mini` (default) - Cost-effective, good quality
- `gpt-4o` - Higher quality, more expensive
- `gpt-3.5-turbo` - Fastest, lowest cost

### Anthropic Models
- `claude-3-haiku-20240307` (default) - Fast and cost-effective
- `claude-3-sonnet-20240229` - Balanced performance
- `claude-3-opus-20240229` - Highest quality

## Usage Examples

### Basic AI Analysis

```bash
# Auto-detect provider and analyze GitHub repo
mcp-builder github https://github.com/fastapi/fastapi

# Analyze local repository with specific provider
mcp-builder init ./my-project --ai-provider openai
```

### Advanced Configuration

```bash
# Full configuration with all options
mcp-builder github https://github.com/owner/repo \
  --github-token $GITHUB_TOKEN \
  --ai-provider openai \
  --ai-model gpt-4o \
  --openai-key $OPENAI_API_KEY \
  --output detailed-mcp.yaml
```

### Command Line API Keys

```bash
# Pass API keys directly (not recommended for production)
mcp-builder init /path/to/repo \
  --ai-provider openai \
  --openai-key sk-your-key-here

mcp-builder init /path/to/repo \
  --ai-provider anthropic \
  --anthropic-key sk-ant-your-key-here
```

## AI vs Mock Comparison

### Mock Reasoning Engine (Default)
- ✅ Always available, no setup required
- ✅ Fast processing
- ❌ Generic insights, not project-specific
- ❌ Limited contextual understanding

### AI Reasoning Engines
- ✅ Project-specific, contextual insights
- ✅ Understands code patterns and documentation
- ✅ Identifies actual problems and solutions
- ✅ Generates relevant feature lists
- ❌ Requires API keys and internet connection
- ❌ Costs money per analysis
- ❌ Slower processing

## Example AI-Generated Output

When using AI, you'll get much more specific and accurate insights:

**Mock Output:**
```yaml
problem: "This project addresses a significant challenge in its domain..."
solution: "The project implements a comprehensive approach using best practices..."
```

**AI Output:**
```yaml
problem: "Developers struggle with creating responsive CSS Grid layouts manually, often resulting in inconsistent designs and time-consuming trial-and-error."
solution: "This visual CSS Grid generator provides an intuitive drag-and-drop interface for creating complex grid layouts with real-time preview and automatic code generation."
```

## Cost Considerations

### OpenAI Pricing (approximate)
- GPT-4o-mini: ~$0.001 per analysis
- GPT-4o: ~$0.01 per analysis

### Anthropic Pricing (approximate)
- Claude 3 Haiku: ~$0.001 per analysis
- Claude 3 Sonnet: ~$0.005 per analysis

### Recommendations
- Use **GPT-4o-mini** for most projects (best cost/quality ratio)
- Use **Claude 3 Haiku** for similar cost-effectiveness
- Use higher-tier models only for critical projects

## Troubleshooting

### No AI Provider Available
```bash
# Check provider status
mcp-builder providers

# Install missing packages
pip install openai anthropic

# Set API keys
export OPENAI_API_KEY=your_key
export ANTHROPIC_API_KEY=your_key
```

### API Key Issues
```bash
# Test API key validity
python -c "import openai; print(openai.OpenAI().models.list())"

# Check environment variables
echo $OPENAI_API_KEY
echo $ANTHROPIC_API_KEY
```

### Fallback Behavior
- If AI provider fails, automatically falls back to mock reasoning
- Logs warning messages for debugging
- Ensures MCP generation always succeeds

## Best Practices

1. **Use environment variables** for API keys (more secure)
2. **Start with auto-detection** to use available providers
3. **Use cost-effective models** for batch processing
4. **Keep API keys secure** and rotate them regularly
5. **Monitor usage** to control costs
6. **Test with mock first** to verify workflow before using AI