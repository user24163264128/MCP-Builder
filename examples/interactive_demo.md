# Interactive AI Setup Demo

This document shows how the interactive AI setup works in MCP Builder.

## Scenario 1: First-time User (No AI Configured)

When a user runs MCP Builder for the first time without any AI providers configured:

```bash
$ mcp-builder github https://github.com/user24163264128/CssGridGenerator
```

**Interactive Flow:**
```
Warning: No GitHub token provided. Some features may be limited.
Set GITHUB_TOKEN environment variable or use --github-token flag
Analyzing GitHub repository: https://github.com/user24163264128/CssGridGenerator

AI Provider Setup
No AI provider is currently configured. Choose an option:
1. OpenAI (recommended, requires API key)
2. Anthropic (high quality, requires API key)
3. Local LLM (free, downloads models)
4. Simple reasoning (rule-based, no AI)
5. Mock reasoning (basic templates)

Select option [4]: 1

OpenAI Setup
You need an OpenAI API key. Get one at: https://platform.openai.com/api-keys
Do you have an OpenAI API key? [y/N]: y
Enter your OpenAI API key: [hidden input]
✓ OpenAI API key configured for this session
Tip: Add 'export OPENAI_API_KEY=your_key' to your shell profile for permanent setup

Using OpenAI reasoning engine
✓ MCP generated successfully at mcp.yaml
```

## Scenario 2: Missing Package Installation

When a user selects a provider but doesn't have the package installed:

```bash
$ mcp-builder init /path/to/repo --ai-provider openai
```

**Interactive Flow:**
```
No OpenAI API key found
Would you like to enter your OpenAI API key now? [y/N]: y
Enter your OpenAI API key: [hidden input]

OpenAI package not installed
Would you like to install it? (pip install openai) [y/N]: y
✓ OpenAI package installed
✓ OpenAI API key configured for this session

Using OpenAI reasoning engine
✓ MCP generated successfully at mcp.yaml
```

## Scenario 3: Local LLM Setup

When a user chooses local LLM for privacy:

```bash
$ mcp-builder github https://github.com/owner/repo --ai-provider local
```

**Interactive Flow:**
```
Local LLM Setup
Available models:
1. microsoft/DialoGPT-medium (default, ~350MB)
2. gpt2 (lightweight, ~500MB)
3. distilgpt2 (smallest, ~250MB)

Select model [1]: 1
Loading local model: microsoft/DialoGPT-medium
[Progress bars showing model download]
✓ Local model loaded successfully

Using Local LLM reasoning engine
✓ MCP generated successfully at mcp.yaml
```

## Scenario 4: Non-Interactive Mode (CI/Scripts)

For automated environments:

```bash
$ mcp-builder github https://github.com/owner/repo --ai-provider simple --no-interactive
```

**Output:**
```
Analyzing GitHub repository: https://github.com/owner/repo
Using Simple LLM reasoning engine
✓ MCP generated successfully at mcp.yaml
```

## Scenario 5: Provider Status Check

Users can check what's available:

```bash
$ mcp-builder providers
```

**Output:**
```
                         Available AI Providers                          
┏━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┓
┃ Provider  ┃ Package      ┃ Installed ┃ API Key ┃ Status               ┃
┡━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━┩
│ Openai    │ openai       │ ✓         │ ✓       │ Ready to use         │
│ Anthropic │ anthropic    │ ✗         │ ✗       │ Need installation    │
│ Local     │ transformers │ ✓         │ ✓       │ Local models         │
│ Simple    │ built-in     │ ✓         │ ✓       │ Rule-based reasoning │
│ Mock      │ built-in     │ ✓         │ ✓       │ Basic templates      │
└───────────┴──────────────┴───────────┴─────────┴──────────────────────┘

Setup Instructions:
• OpenAI: pip install openai && export OPENAI_API_KEY=your_key
• Anthropic: pip install anthropic && export ANTHROPIC_API_KEY=your_key
• Local LLM: pip install transformers torch (downloads models automatically)
• Simple: No setup required (intelligent rule-based analysis)
• Mock: No setup required (basic templates)

Recommendations:
• Best quality: OpenAI GPT-4 or Anthropic Claude
• Best cost: OpenAI GPT-4o-mini or Simple reasoning
• Privacy-focused: Local LLM or Simple reasoning
• No internet: Simple reasoning (works offline)
```

## Key Features

### 🎯 **Smart Defaults**
- Auto-detects available providers
- Falls back gracefully when providers unavailable
- Recommends best options based on user needs

### 🔒 **Security-Conscious**
- API keys entered securely (hidden input)
- Environment variable recommendations
- Session-only storage by default

### 🚀 **User-Friendly**
- Clear setup instructions with URLs
- Progress indicators for downloads
- Helpful error messages and suggestions

### ⚙️ **Flexible Configuration**
- Interactive mode for guided setup
- Non-interactive mode for automation
- Command-line overrides for all options

### 📊 **Transparent Status**
- Clear provider availability information
- Installation and configuration status
- Performance and cost recommendations

This interactive approach makes AI-powered MCP generation accessible to users of all technical levels while maintaining flexibility for advanced users and automation scenarios.