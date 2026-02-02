# GitHub Integration Examples

This document shows how to use MCP Builder with GitHub repositories.

## Basic Usage (No Token Required)

```bash
# Analyze any public GitHub repository
mcp-builder github https://github.com/tiangolo/typer

# Generate MCP for a GitHub repository
mcp-builder init https://github.com/microsoft/vscode --output vscode-mcp.yaml

# Analyze without generating files
mcp-builder analyze https://github.com/python/cpython
```

## Enhanced Usage (With GitHub Token)

For enhanced metadata including stars, forks, contributors, and more detailed analysis:

### 1. Set up GitHub Token

```bash
# Option 1: Environment variable (recommended)
export GITHUB_TOKEN=your_personal_access_token_here

# Option 2: Command line flag
mcp-builder github https://github.com/owner/repo --github-token your_token
```

### 2. Generate Enhanced MCP

```bash
# With environment variable
mcp-builder github https://github.com/tiangolo/typer --output typer-mcp.yaml

# With command line token
mcp-builder github https://github.com/fastapi/fastapi \
  --github-token your_token \
  --output fastapi-mcp.yaml
```

### 3. Check API Rate Limits

```bash
mcp-builder rate-limit --github-token your_token
```

## Example Output

When using a GitHub token, you'll see enhanced output like:

```
GitHub Repository Metrics:
  Stars: 15,234
  Forks: 1,456
  Contributors: 89
  Open Issues: 234
  Primary Language: Python
  License: MIT
  Activity Level: very_active
  Popularity Score: 15,678.2
  Topics: python, cli, typer, fastapi
```

## Supported Repository Types

- **Public repositories**: Work without authentication
- **Private repositories**: Require GitHub token with appropriate permissions
- **Organization repositories**: Work with proper token permissions
- **Forked repositories**: Supported with full metadata

## GitHub Token Permissions

For optimal functionality, your GitHub token should have:

- `public_repo` (for public repositories)
- `repo` (for private repositories you have access to)
- `read:org` (for organization repository metadata)

## Error Handling

The tool gracefully handles:

- **Network issues**: Falls back to local analysis
- **Rate limiting**: Shows clear error messages with suggestions
- **Invalid URLs**: Validates GitHub URL format
- **Private repositories**: Clear permission error messages
- **Repository not found**: Helpful error messages

## Performance Notes

- **Shallow cloning**: Only downloads the latest commit for faster processing
- **Temporary directories**: Automatically cleaned up after analysis
- **Efficient API usage**: Minimizes GitHub API calls to respect rate limits
- **Caching**: Future versions will include intelligent caching