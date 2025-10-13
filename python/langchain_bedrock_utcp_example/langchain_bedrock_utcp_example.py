#!/usr/bin/env python3
"""
Minimal LangChain + Amazon Bedrock + UTCP Integration Example

This example demonstrates the basic integration of UTCP tools with LangChain agents
using Amazon Bedrock as the language model provider.

Based on the official langchain-utcp-adapters examples.
"""

import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv

from utcp.utcp_client import UtcpClient
from langchain_utcp_adapters import load_utcp_tools, create_bedrock_tool_mapping

# Optional: Only import if available
try:
    from langgraph.prebuilt import create_react_agent
    from langchain_aws import ChatBedrock
    import boto3
    BEDROCK_AVAILABLE = True
except ImportError:
    BEDROCK_AVAILABLE = False
    print("Install Bedrock dependencies: pip install langchain-aws boto3")


async def main():
    """Minimal Bedrock + UTCP integration example."""
    print("🤖 LangChain + Amazon Bedrock + UTCP Integration")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv(Path(__file__).parent / ".env")
    
    if not BEDROCK_AVAILABLE:
        print("❌ Required dependencies not available.")
        print("Install with: pip install langchain-aws boto3")
        return
    
    # Check AWS credentials
    try:
        session = boto3.Session()
        credentials = session.get_credentials()
        if not credentials:
            print("❌ No AWS credentials found")
            print("Configure AWS credentials via AWS CLI or environment variables")
            return
        print("✅ AWS credentials found")
    except Exception as e:
        print(f"❌ AWS credential error: {e}")
        return
    
    # Create UTCP client with configuration
    print("📡 Setting up UTCP client...")
    try:
        config_path = str(Path(__file__).parent / "providers.json")
        client = await UtcpClient.create(config=config_path)
        print("✅ UTCP client initialized")
    except Exception as e:
        print(f"❌ Failed to initialize UTCP client: {e}")
        return
    
    # Load tools and convert to LangChain format
    print("🔧 Loading UTCP tools...")
    try:
        original_tools = await load_utcp_tools(client)
        print(f"Loaded {len(original_tools)} tools")
        
        if not original_tools:
            print("❌ No tools available. Cannot create agent.")
            return
    except Exception as e:
        print(f"❌ Failed to load tools: {e}")
        return
    
    # Create Bedrock-compatible tools with name mapping
    print("🔧 Creating Bedrock-compatible tools...")
    bedrock_tools, name_mapping = create_bedrock_tool_mapping(original_tools)
    print(f"Created {len(bedrock_tools)} Bedrock-compatible tools")
    
    # Show tool name mapping examples
    mapped_count = sum(1 for b, o in name_mapping.items() if b != o)
    if mapped_count > 0:
        print(f"📝 {mapped_count} tool names mapped for Bedrock compatibility")
    
    # Create Bedrock LLM
    print("🤖 Creating Bedrock LLM...")
    try:
        model_id = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-sonnet-20240229-v1:0")
        llm = ChatBedrock(
            model_id=model_id,
            region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1"),
            model_kwargs={
                "temperature": 0.1,
                "max_tokens": 2000,
            }
        )
        print(f"✅ Bedrock LLM initialized with {model_id}")
    except Exception as e:
        print(f"❌ Failed to initialize Bedrock LLM: {e}")
        return
    
    # Create LangGraph agent
    print("🤖 Creating LangGraph agent...")
    try:
        agent = create_react_agent(llm, bedrock_tools)
        print("✅ Agent created successfully")
    except Exception as e:
        print(f"❌ Failed to create agent: {e}")
        return
    
    # Interactive loop
    print("\n" + "="*50)
    print("🎯 Agent Ready! Ask questions or type 'quit' to exit")
    print("Example: 'Search for books about Python programming'")
    print("="*50)
    
    while True:
        try:
            user_input = input("\n💬 You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if not user_input:
                continue
            
            print("🤔 Thinking...")
            
            # Invoke the agent
            response = await agent.ainvoke({
                "messages": [("user", user_input)]
            })
            
            # Display response
            print(f"🤖 Assistant: {response['messages'][-1].content}")
            
            # Show which tools were used (optional debug info)
            tool_calls = []
            for message in response["messages"]:
                if hasattr(message, 'tool_calls') and message.tool_calls:
                    tool_calls.extend(message.tool_calls)
            
            if tool_calls:
                print(f"\n🔧 Tools used: {', '.join(set(tc['name'] for tc in tool_calls))}")
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())