# Amazon Bedrock + UTCP Tool Calling Example

This example demonstrates how to integrate the Universal Tool Calling Protocol (UTCP) with Amazon Bedrock to enable dynamic tool discovery and execution. The system searches for relevant tools based on user queries, instructs Bedrock to make tool calls, and executes those tools using UTCP call templates that provide direct access to existing APIs as LLM tools.

## What This Example Does

1. **Tool Discovery**: Searches available UTCP tools based on user input
2. **LLM Integration**: Uses Amazon Bedrock to determine which tools to call
3. **Tool Execution**: Executes the selected tools via UTCP call templates and returns results
4. **Response Generation**: Provides final responses incorporating tool results
5. **Multi-turn Conversations**: Handles complex tool chains and recursive tool calls
6. **Intelligent Tool Usage**: Balances between using tools and leveraging LLM knowledge

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
- API keys for any external tools (e.g., `newsapi_NEWS_API_KEY` for NewsAPI)
- Optional: `BEDROCK_MODEL_ID` to override the default model

### 4. Run the Example

```bash
python bedrock_utcp_client_example.py
```

The script will start an interactive session where you can ask questions that might require tool usage.

#### Command Line Options

- `--debug`: Enable detailed debug output for troubleshooting
- `--prompt "your question"`: Start with a specific prompt instead of interactive mode

Examples:
```bash
# Interactive mode with debug output
python bedrock_utcp_client_example.py --debug

# Automated mode with a specific question
python bedrock_utcp_client_example.py --prompt "What are the latest news about AI?"

# Both debug and automated mode
python bedrock_utcp_client_example.py --debug --prompt "Find books about machine learning"
```

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

## Troubleshooting

### Common Issues

1. **AWS Credentials Not Found**
   - Ensure AWS credentials are configured via AWS CLI or environment variables
   - Check that your AWS profile has Bedrock access permissions

2. **Tool API Failures**
   - Verify API keys are correctly set in `.env` file
   - Use `--debug` flag to see detailed error information
   - Check API rate limits and quotas

3. **Model Access Issues**
   - Ensure your AWS account has access to the specified Bedrock model
   - Try setting a different model via `BEDROCK_MODEL_ID` environment variable

4. **Debug Mode**
   - Use `--debug` for detailed execution logs
   - Check conversation history and tool call traces
   - Verify tool discovery and selection process

## Learn More

- [UTCP Python Library](https://github.com/universal-tool-calling-protocol/python-utcp)
- [UTCP Examples Repository](https://github.com/universal-tool-calling-protocol/utcp-examples)
- [Amazon Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
