# Amazon Bedrock + UTCP Tool Calling Example

This example demonstrates how to integrate the Universal Tool Calling Protocol (UTCP) with Amazon Bedrock to enable dynamic tool discovery and execution. The system searches for relevant tools based on user queries, instructs Bedrock to make tool calls, and executes those tools using UTCP call templates that provide direct access to existing APIs as LLM tools.

## What This Example Does

1. **Tool Discovery**: Searches available UTCP tools based on user input
2. **LLM Integration**: Uses Amazon Bedrock to determine which tools to call
3. **Tool Execution**: Executes the selected tools via UTCP call templates and returns results
4. **Response Generation**: Provides final responses incorporating tool results

**Note**: This is a client-only example - no server is involved. The call templates provide a direct way for the client to use existing APIs as LLM tools.

## Project Structure

```
bedrock_llm_tool_calling_example/
├── bedrock_utcp_client_example.py    # Main application script
├── providers.json                    # UTCP client configuration
├── example.env                      # Environment variables template
├── newsapi_manual.json              # Sample tool manual for NewsAPI
├── requirements.txt                 # Python dependencies
└── README.md                       # This file
```

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
- API keys for any external tools (e.g., NewsAPI)

### 4. Run the Example

```bash
python bedrock_utcp_client_example.py
```

The script will start an interactive session where you can ask questions that might require tool usage.

## About UTCP

This example uses the [Universal Tool Calling Protocol (UTCP)](https://github.com/universal-tool-calling-protocol/python-utcp), a secure and scalable standard for defining and interacting with tools across various communication protocols.

Key UTCP features demonstrated:
- **Multiple Protocols**: HTTP and text file protocol support
- **Tool Discovery**: Automatic tool search and matching
- **Extensibility**: Easy integration with existing services and infrastructure

## Configuration

The `providers.json` file defines the UTCP client configuration, including:
- Tool repositories and search strategies
- Manual call templates for different protocols
- Variable substitution and authentication settings

## Dependencies

- **utcp**: Core UTCP library for tool protocol handling
- **utcp-http**: HTTP protocol plugin for REST API tools
- **utcp-text**: Text file protocol plugin for local tool manuals
- **boto3**: AWS SDK for Bedrock integration
- **python-dotenv**: Environment variable management

## Learn More

- [UTCP Python Library](https://github.com/universal-tool-calling-protocol/python-utcp)
- [UTCP Examples Repository](https://github.com/universal-tool-calling-protocol/utcp-examples)
- [Amazon Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
