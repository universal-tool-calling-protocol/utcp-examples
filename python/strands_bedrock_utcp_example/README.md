# Strands Bedrock UTCP Example

This example demonstrates the integration of UTCP tools with Strands Agents using Amazon Bedrock for multi-turn conversational AI interactions. It uses the [strands-utcp](https://github.com/universal-tool-calling-protocol/strands-utcp) library for tool discovery and the Strands Agent framework for LLM integration.

## About This Example

This example showcases:
- **Strands UTCP Integration**: Tool discovery and management via UTCP protocol
- **Amazon Bedrock LLM**: Claude Sonnet 4.5 for conversational AI
- **Multi-turn Conversations**: Interactive chat with tool-calling capabilities
- **External API Integration**: NewsAPI and OpenLibrary via UTCP tools
- **Professional Logging**: Structured debug output with --debug flag

## Prerequisites

- Python 3.8+
- AWS credentials configured (for Bedrock access)
- NewsAPI key (optional, for news search functionality)

## Setup

1. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment:**
   ```bash
   cp example.env .env
   # Edit .env with your AWS credentials and API keys
   ```

4. **Configure AWS credentials** (if not already done):
   ```bash
   aws configure
   # OR set environment variables: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
   ```

## Usage

**Basic usage:**
```bash
python strands_bedrock_utcp_example.py
```

**With debug output:**
```bash
python strands_bedrock_utcp_example.py --debug
```

**With initial prompt:**
```bash
python strands_bedrock_utcp_example.py --prompt "Which tools do you have?"
```

**Combined options:**
```bash
python strands_bedrock_utcp_example.py --debug --prompt "Search for recent news about Python"
```

**Example interactions:**
- "Which tools do you have?"
- "Search for recent news about Python programming"
- "Find the author ID for William Shakespeare"
- "Search for books by Shakespeare"

## What This Example Demonstrates

- **UTCP Tool Adapter**: Initialize and manage UTCP tools with configuration
- **Tool Discovery**: Automatic discovery from OpenAPI specs and manual definitions
- **Strands Agent Integration**: Create conversational AI agents with tool access
- **Amazon Bedrock LLM**: Claude Sonnet 4.5 for natural language interactions
- **Multi-turn Conversations**: Interactive chat with context and tool calling
- **External API Integration**: NewsAPI for news search, OpenLibrary for book data
- **Professional Logging**: Structured output with optional debug mode
- **Error Handling**: Graceful handling of API errors and edge cases


## Configuration

**`providers.json`** defines:
- **Environment variable loading**: Loads from .env file
- **OpenLibrary integration**: HTTP call template for OpenAPI spec discovery
- **NewsAPI integration**: Text call template referencing newsapi_manual.json

**`.env`** contains:
- **AWS credentials**: For Bedrock access
- **Bedrock model ID**: Claude Sonnet 4.5 model specification
- **NewsAPI key**: For news article search functionality

**`newsapi_manual.json`** defines:
- NewsAPI tool schema in UTCP format
- Authentication configuration
- Input/output parameter definitions

## More Examples

For more comprehensive examples and advanced usage patterns, see the official repository:
- **[Strands UTCP Examples](https://github.com/universal-tool-calling-protocol/strands-utcp/tree/main/examples)**
- **[Library Documentation](https://github.com/universal-tool-calling-protocol/strands-utcp)**

The official examples include:
- HTTP server/client communication
- CLI tool integration  
- MCP (Model Context Protocol) bridges
- Advanced tool composition patterns
- Multi-provider configurations
- Authentication and security patterns


## Troubleshooting

**Common Issues:**

1. **"No AWS credentials found"**
   - Configure AWS CLI: `aws configure`
   - Or set environment variables in .env file

2. **"UTCP tool adapter initialization failed"**
   - Ensure you're running from the correct directory
   - Check that newsapi_manual.json exists
   - Verify providers.json is valid JSON

3. **"utcp-text not available"**
   - Install missing dependency: `pip install utcp-text`
   - Or reinstall requirements: `pip install -r requirements.txt`

4. **Debug mode:**
   - Use `--debug` flag for detailed logging
   - Check tool registration and API calls

**Dependencies:**
- Ensure Python 3.8+
- All packages in requirements.txt installed
- AWS credentials properly configured
- NewsAPI key in .env (optional but recommended)