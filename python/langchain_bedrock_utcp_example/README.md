# LangChain + Amazon Bedrock + UTCP Integration Example

A minimal example demonstrating how to integrate UTCP tools with LangChain agents using Amazon Bedrock as the language model provider.

This example is based on the official [langchain-utcp-adapters](https://github.com/universal-tool-calling-protocol/langchain-utcp-adapters) library and follows the same patterns as the [bedrock_langgraph.py example](https://github.com/universal-tool-calling-protocol/langchain-utcp-adapters/blob/main/examples/bedrock_langgraph.py).

## What This Example Does

1. **UTCP Integration**: Loads tools from UTCP providers (NewsAPI, OpenLibrary) using `load_utcp_tools()`
2. **Bedrock Compatibility**: Uses `create_bedrock_tool_mapping()` to ensure tool names meet Bedrock requirements
3. **LangGraph Agent**: Creates a ReAct agent with `create_react_agent()` that can use tools intelligently
4. **Interactive Chat**: Provides a simple chat interface to test the integration
5. **Minimal Implementation**: Follows official adapter library patterns for clean, maintainable code

## Setup Instructions

### 1. Create and Activate Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

Copy the example environment file and configure your credentials:

```bash
cp example.env .env
```

Edit `.env` with your actual credentials:
- AWS credentials for Bedrock access
- API keys for any external tools (e.g., `newsapi_NEWS_API_KEY` for NewsAPI)
- Optional: `BEDROCK_MODEL_ID` to override the default model

### 4. Run the Example

```bash
python langchain_bedrock_utcp_example.py
```

## Key Features

### Official Library Integration
- Uses the official `langchain-utcp-adapters` library functions:
  - `load_utcp_tools()` - Loads and converts all UTCP tools to LangChain format
  - `create_bedrock_tool_mapping()` - Creates Bedrock-compatible tool names
- Follows the same patterns as the [official examples](https://github.com/universal-tool-calling-protocol/langchain-utcp-adapters/tree/main/examples)

### Amazon Bedrock Integration
- Uses `ChatBedrock` with Claude models (default: Claude 3 Sonnet)
- Automatic tool name mapping for Bedrock's naming requirements
- Configurable model selection via `BEDROCK_MODEL_ID` environment variable

### LangGraph Agent
- Creates a ReAct agent using `create_react_agent()` from LangGraph
- Intelligent tool selection and reasoning
- Proper async/await handling for tool execution

### Interactive Testing
- Simple chat interface for testing tool integration
- Shows which tools were used for each query
- Clean error handling and user feedback

## Configuration

The example uses `providers.json` to configure UTCP tool providers:

```json
{
    "load_variables_from": [
        {
            "variable_loader_type": "dotenv",
            "env_file_path": ".env"
        }
    ],
    "manual_call_templates": [
        {
            "name": "openlibrary",
            "call_template_type": "http",
            "http_method": "GET",
            "url": "https://openlibrary.org/static/openapi.json",
            "content_type": "application/json"
        },
        {
            "name": "newsapi",
            "call_template_type": "text",
            "file_path": "./newsapi_manual.json"
        }
    ]
}
```

## Dependencies

- **langchain**: Core LangChain library for agent workflows
- **langchain-aws**: Amazon Bedrock integration for LangChain
- **langchain-utcp-adapters**: Official UTCP to LangChain conversion library
- **langgraph**: LangGraph for creating ReAct agents
- **utcp**: Core UTCP library for tool protocol handling
- **utcp-http**: HTTP protocol plugin for REST APIs (OpenLibrary)
- **utcp-text**: Text file protocol plugin for local tool manuals (NewsAPI)
- **boto3**: AWS SDK for Bedrock integration
- **python-dotenv**: Environment variable management

## Example Usage

```bash
$ python langchain_bedrock_utcp_example.py

🤖 LangChain + Amazon Bedrock + UTCP Integration
==================================================
✅ AWS credentials found
✅ UTCP client initialized
🔧 Loading UTCP tools...
Loaded 13 tools
🔧 Creating Bedrock-compatible tools...
Created 13 Bedrock-compatible tools
📝 11 tool names mapped for Bedrock compatibility
🤖 Creating Bedrock LLM...
✅ Bedrock LLM initialized with anthropic.claude-3-sonnet-20240229-v1:0
🤖 Creating LangGraph agent...
✅ Agent created successfully

==================================================
🎯 Agent Ready! Ask questions or type 'quit' to exit
Example: 'Search for books about Python programming'
==================================================

💬 You: Search for books about Python programming
🤔 Thinking...
🤖 Assistant: I found several Python programming books for you! Here are some popular options:

1. **"Learning Python"** by Mark Lutz - A comprehensive guide covering Python fundamentals
2. **"Python Crash Course"** by Eric Matthes - Great for beginners with hands-on projects
3. **"Automate the Boring Stuff with Python"** by Al Sweigart - Focuses on practical automation
4. **"Effective Python"** by Brett Slatkin - Advanced techniques for experienced programmers
5. **"Python Cookbook"** by David Beazley - Solutions to common programming problems

🔧 Tools used: openlibrary_read_search_json_search_json_get

💬 You: which tool would you use to search for author id?
🤔 Thinking...
🤖 Assistant: To search for an author ID, I would use the **openlibrary_read_search_authors_json_search_authors_json_get** tool.

**Why this tool?**
1. **Purpose-built for author search**: This tool is specifically designed to search for authors
2. **Returns author information**: It returns author records that include the author's Open Library ID (OLID)
3. **Simple query parameter**: It only requires a search query, making it straightforward to use
4. **Appropriate for discovery**: When you don't have an author ID and need to find it, search is the logical starting point

💬 You: quit
👋 Goodbye!
```

## Troubleshooting

### Common Issues

1. **AWS Credentials Not Found**
   - Ensure AWS credentials are configured via AWS CLI or environment variables
   - Check that your AWS profile has Bedrock access permissions

2. **Tool Loading Errors**
   - Verify UTCP tools are properly configured in `providers.json`
   - Check API keys are correctly set in `.env` file
   - Ensure external APIs (OpenLibrary, NewsAPI) are accessible

3. **Bedrock Model Access**
   - Verify the model ID is available in your AWS region
   - Check Bedrock service permissions in your AWS account

## More Examples

For additional examples and advanced usage patterns, see the official [langchain-utcp-adapters examples](https://github.com/universal-tool-calling-protocol/langchain-utcp-adapters/tree/main/examples):

### Basic Examples (No API Keys Required)
- **[basic_usage.py](https://github.com/universal-tool-calling-protocol/langchain-utcp-adapters/blob/main/examples/basic_usage.py)** - Basic tool loading and usage (31 tools from Petstore + OpenLibrary)
- **[providers.py](https://github.com/universal-tool-calling-protocol/langchain-utcp-adapters/blob/main/examples/providers.py)** - Real-world call template examples (11 OpenLibrary tools)
- **[authentication.py](https://github.com/universal-tool-calling-protocol/langchain-utcp-adapters/blob/main/examples/authentication.py)** - Authentication methods demonstration

### OpenAI Examples (Requires OPENAI_API_KEY)
- **[openai_langgraph.py](https://github.com/universal-tool-calling-protocol/langchain-utcp-adapters/blob/main/examples/openai_langgraph.py)** - LangGraph integration with OpenAI
- **[openai_advanced.py](https://github.com/universal-tool-calling-protocol/langchain-utcp-adapters/blob/main/examples/openai_advanced.py)** - Advanced LangGraph integration

### Amazon Bedrock Examples (Requires AWS Credentials)
- **[bedrock_langgraph.py](https://github.com/universal-tool-calling-protocol/langchain-utcp-adapters/blob/main/examples/bedrock_langgraph.py)** - Simple Amazon Bedrock integration (this example is based on this)
- **[bedrock_advanced.py](https://github.com/universal-tool-calling-protocol/langchain-utcp-adapters/blob/main/examples/bedrock_advanced.py)** - Comprehensive Amazon Bedrock integration

## Learn More

- **[LangChain UTCP Adapters](https://github.com/universal-tool-calling-protocol/langchain-utcp-adapters)** - Official adapter library with comprehensive examples
- **[LangChain Documentation](https://python.langchain.com/)** - Core framework documentation
- **[LangGraph Documentation](https://langchain-ai.github.io/langgraph/)** - Agent creation and workflows
- **[UTCP Python Library](https://github.com/universal-tool-calling-protocol/python-utcp)** - Core tool protocol implementation
- **[Amazon Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)** - Claude models and API reference