# 🚀 MCP Builder

**AI-Powered Repository Analysis & MCP Generation Platform**

Transform any GitHub repository or local project into structured, high-fidelity **MCP YAML** files that capture deep project context for AI agents. Built for developers, by developers.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-passing-green.svg)](tests/)

---

## ✨ Features

### 🤖 **AI-Powered Analysis**
- **5 AI Reasoning Engines**: OpenAI GPT, Anthropic Claude, Local LLM, Smart Rules, Templates
- **Interactive Setup**: Guided configuration for first-time users
- **Intelligent Fallbacks**: Always generates MCPs, even when AI services fail
- **Context-Aware Insights**: Project-specific analysis based on actual code and documentation

### 🌐 **GitHub Integration**
- **Direct GitHub URLs**: Analyze any public repository instantly
- **Enhanced Metadata**: Stars, forks, contributors, language statistics
- **Automatic Cloning**: Temporary, efficient repository processing
- **API Rate Limiting**: Smart GitHub API usage with status monitoring

### 🎯 **Smart Repository Analysis**
- **Multi-Language Detection**: Automatic programming language identification
- **Framework Recognition**: Detects popular frameworks and libraries
- **Project Classification**: CLI, Web App, API, Library, ML, Automation
- **Maturity Assessment**: Prototype, MVP, Production status evaluation

### 🔧 **Developer Experience**
- **Zero Configuration**: Works out of the box with intelligent defaults
- **Interactive Mode**: Guided setup for optimal user experience
- **Automation Ready**: Non-interactive mode for CI/CD pipelines
- **Comprehensive CLI**: Rich command-line interface with helpful outputs

---

## 🚀 Quick Start

### Installation

```bash
# Basic installation
pip install -e .

# With AI capabilities (recommended)
pip install -e ".[ai]"

# With local LLM support
pip install -e ".[local-llm]"

# Everything included
pip install -e ".[all]"
```

### Instant Analysis

```bash
# Analyze any GitHub repository
mcp-builder github https://github.com/microsoft/vscode

# Analyze local project
mcp-builder init ./my-project

# Check available AI providers
mcp-builder providers
```

---

## 🤖 AI-Powered Intelligence

MCP Builder offers multiple AI reasoning engines to suit different needs:

### 🌟 **Recommended Setup (Interactive)**

Just run any command - MCP Builder will guide you through the optimal setup:

```bash
mcp-builder github https://github.com/your-favorite/repo
```

**Interactive Flow:**
```
AI Provider Setup
No AI provider is currently configured. Choose an option:
1. OpenAI (recommended, requires API key)
2. Anthropic (high quality, requires API key)  
3. Local LLM (free, downloads models)
4. Simple reasoning (rule-based, no AI)
5. Mock reasoning (basic templates)

Select option [4]: 1
```

### ⚡ **Quick Manual Setup**

```bash
# OpenAI (best cost/performance ratio)
export OPENAI_API_KEY=your_key
pip install openai

# Anthropic (highest quality)
export ANTHROPIC_API_KEY=your_key
pip install anthropic

# Local LLM (privacy-focused)
pip install transformers torch

# Simple reasoning (no setup required)
# Works offline, intelligent rule-based analysis
```

### 🎯 **AI Provider Comparison**

| Provider | Quality | Cost | Privacy | Offline | Setup |
|----------|---------|------|---------|---------|-------|
| **OpenAI GPT** | ⭐⭐⭐⭐⭐ | 💰💰 | ❌ | ❌ | API Key |
| **Anthropic Claude** | ⭐⭐⭐⭐⭐ | 💰💰💰 | ❌ | ❌ | API Key |
| **Local LLM** | ⭐⭐⭐ | Free | ✅ | ✅ | Download |
| **Simple Rules** | ⭐⭐⭐⭐ | Free | ✅ | ✅ | None |
| **Mock Templates** | ⭐ | Free | ✅ | ✅ | None |

---

## 📖 Usage Guide

### 🌐 **GitHub Repository Analysis**

```bash
# Basic GitHub analysis
mcp-builder github https://github.com/fastapi/fastapi

# With GitHub token for enhanced metadata
export GITHUB_TOKEN=your_github_token
mcp-builder github https://github.com/private/repo

# Specify AI provider and model
mcp-builder github https://github.com/owner/repo \
  --ai-provider openai \
  --ai-model gpt-4o \
  --output detailed-analysis.yaml

# Check GitHub API rate limits
mcp-builder rate-limit --github-token your_token
```

### 💻 **Local Project Analysis**

```bash
# Analyze current directory
mcp-builder init .

# Analyze specific project
mcp-builder init /path/to/project --output project-mcp.yaml

# Use specific AI provider
mcp-builder init ./my-app --ai-provider anthropic --ai-model claude-3-sonnet-20240229
```

### 🔍 **Analysis Without Generation**

```bash
# Preview analysis results
mcp-builder analyze https://github.com/owner/repo

# Local project analysis
mcp-builder analyze ./project --ai-provider simple
```

### ⚙️ **Advanced Configuration**

```bash
# Non-interactive mode (for CI/CD)
mcp-builder github https://github.com/owner/repo \
  --ai-provider simple \
  --no-interactive \
  --output ci-mcp.yaml

# Custom API keys
mcp-builder init ./project \
  --ai-provider openai \
  --openai-key sk-your-key-here

# Local LLM with specific model
mcp-builder github https://github.com/owner/repo \
  --ai-provider local \
  --ai-model distilgpt2
```

### 📊 **Provider Management**

```bash
# Check available providers
mcp-builder providers

# Validate existing MCP file
mcp-builder validate mcp.yaml

# Update existing MCP (coming soon)
mcp-builder update ./project
```

---

## 🏗️ Architecture

MCP Builder is designed with modularity and extensibility in mind:

```
mcp_builder/
├── cli/              # Command-line interface
├── ingestion/        # Repository content extraction
├── analyzers/        # Technical signal detection
├── intelligence/     # AI reasoning engines
├── github/           # GitHub API integration
├── mcp/              # YAML generation & schemas
└── utils/            # Shared utilities
```

### 🔄 **Processing Pipeline**

1. **Ingestion**: Repository traversal and content extraction
2. **Analysis**: Language, framework, and pattern detection
3. **Intelligence**: AI-powered insight generation
4. **Enhancement**: GitHub metadata enrichment (if available)
5. **Generation**: Structured MCP YAML creation

---

## 📋 **MCP Output Format**

Generated MCP files contain comprehensive project context:

```yaml
project_name: "FastAPI Web Framework"
one_liner: "Modern, fast web framework for building APIs with Python 3.7+"
problem: "Building high-performance APIs requires balancing speed, type safety, and developer experience."
solution: "FastAPI provides automatic API documentation, data validation, and async support with minimal code."
value_proposition: "Delivers production-ready APIs with automatic documentation and type safety."
tech_stack:
  - Python
  - Starlette
  - Pydantic
project_type: library
status: production
key_features:
  - Automatic API documentation
  - Type hints and validation
  - Async/await support
  - High performance
  - Standards-based (OpenAPI, JSON Schema)
target_users: "Python developers building web APIs and microservices"
current_focus: "Performance optimization and ecosystem expansion"
future_plans: "Enhanced tooling and broader framework integrations"
metadata:
  version: "1.0"
  generated_at: "2026-02-02T22:45:00Z"
```

---

## 🧪 **Examples & Use Cases**

### 🎯 **Common Scenarios**

```bash
# Analyze a popular open-source project
mcp-builder github https://github.com/microsoft/typescript

# Quick local project assessment
mcp-builder analyze . --ai-provider simple

# Generate MCP for private repository
mcp-builder github https://github.com/company/private-repo \
  --github-token $GITHUB_TOKEN \
  --ai-provider openai

# Batch processing for multiple projects
for repo in project1 project2 project3; do
  mcp-builder init ./$repo --no-interactive --ai-provider simple
done
```

### 🔬 **Research & Analysis**

```bash
# Compare different AI providers on same project
mcp-builder init ./project --ai-provider simple --output simple-mcp.yaml
mcp-builder init ./project --ai-provider openai --output openai-mcp.yaml
mcp-builder init ./project --ai-provider local --output local-mcp.yaml

# Analyze project evolution over time
git checkout v1.0 && mcp-builder init . --output v1-mcp.yaml
git checkout v2.0 && mcp-builder init . --output v2-mcp.yaml
```

---

## 🛠️ **Development**

### 🧪 **Running Tests**

```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/test_ai_integration.py -v
pytest tests/test_github_integration.py -v

# Run with coverage
pytest --cov=mcp_builder tests/
```

### 🏗️ **Building**

```bash
# Build package
python -m build

# Install in development mode
pip install -e ".[all]"

# Run linting
flake8 mcp_builder/
mypy mcp_builder/
```

### 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes and add tests
4. Run the test suite: `pytest`
5. Commit your changes: `git commit -m 'Add amazing feature'`
6. Push to the branch: `git push origin feature/amazing-feature`
7. Open a Pull Request

---

## 🔧 **Configuration**

### 🌍 **Environment Variables**

```bash
# AI Provider API Keys
export OPENAI_API_KEY=your_openai_key
export ANTHROPIC_API_KEY=your_anthropic_key

# GitHub Integration
export GITHUB_TOKEN=your_github_token

# Hugging Face (for local LLM)
export HF_TOKEN=your_huggingface_token  # Optional, for faster downloads
```

### ⚙️ **Advanced Settings**

```bash
# Disable interactive prompts globally
export MCP_BUILDER_NO_INTERACTIVE=1

# Set default AI provider
export MCP_BUILDER_DEFAULT_PROVIDER=simple

# Custom model cache directory
export MCP_BUILDER_CACHE_DIR=/path/to/cache
```

---

## 🚨 **Troubleshooting**

### ❓ **Common Issues**

**Q: "No AI provider available" error**
```bash
# Check provider status
mcp-builder providers

# Install missing packages
pip install openai anthropic transformers torch
```

**Q: GitHub rate limiting**
```bash
# Check rate limit status
mcp-builder rate-limit --github-token your_token

# Use GitHub token for higher limits
export GITHUB_TOKEN=your_token
```

**Q: Local LLM download fails**
```bash
# Check internet connection and disk space
# Models can be 250MB - 2GB in size

# Try smaller model
mcp-builder init ./project --ai-provider local --ai-model distilgpt2
```

**Q: Permission errors on Windows**
```bash
# Run as administrator or enable Developer Mode
# Required for symlinks in model cache
```

### 🔍 **Debug Mode**

```bash
# Enable verbose logging
export MCP_BUILDER_LOG_LEVEL=DEBUG
mcp-builder init ./project

# Save debug output
mcp-builder init ./project 2>&1 | tee debug.log
```

---

## 📚 **Resources**

### 📖 **Documentation**
- [AI Usage Guide](examples/ai_usage.md)
- [GitHub Integration](examples/github_usage.md)
- [Interactive Demo](examples/interactive_demo.md)

### 🔗 **Links**
- [OpenAI API Keys](https://platform.openai.com/api-keys)
- [Anthropic Console](https://console.anthropic.com/)
- [GitHub Personal Access Tokens](https://github.com/settings/tokens)
- [Hugging Face Models](https://huggingface.co/models)

### 🆘 **Support**
- [Issues](https://github.com/your-org/mcp-builder/issues)
- [Discussions](https://github.com/your-org/mcp-builder/discussions)
- [Contributing Guide](CONTRIBUTING.md)

---

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 **Acknowledgments**

- **OpenAI** and **Anthropic** for providing excellent AI APIs
- **Hugging Face** for the transformers library and model hub
- **GitHub** for the comprehensive repository API
- **Typer** and **Rich** for the beautiful CLI experience
- **Pydantic** for robust data validation and schemas

---

## 🌟 **Star History**

If you find MCP Builder useful, please consider giving it a star! ⭐

---

<div align="center">

**Built with ❤️ for the developer community**

[⭐ Star on GitHub](https://github.com/your-org/mcp-builder) • [🐛 Report Bug](https://github.com/your-org/mcp-builder/issues) • [💡 Request Feature](https://github.com/your-org/mcp-builder/issues)

</div>