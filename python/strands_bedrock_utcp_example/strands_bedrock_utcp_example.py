#!/usr/bin/env python3
"""
Strands UTCP + Amazon Bedrock Integration Example

This example demonstrates the integration of UTCP tools with Strands Agents
using Amazon Bedrock for multi-turn conversational AI interactions.

Based on the strands-utcp library integration patterns.
"""

import asyncio
import os
import json
import argparse
from pathlib import Path
from dotenv import load_dotenv
import traceback

from strands_utcp import UtcpToolAdapter
from strands import Agent
from strands.models import BedrockModel

# Global debug flag
DEBUG = False

# Optional: Only import if available
try:
    import boto3
    BEDROCK_AVAILABLE = True
except ImportError:
    BEDROCK_AVAILABLE = False
    print("Install Bedrock dependencies: pip install boto3")


def debug_print(function_name: str, message: str, data=None):
    """Standardized debug output function."""
    if DEBUG:
        print(f"[DEBUG] {function_name}: {message}")
        if data is not None:
            if isinstance(data, (dict, list)):
                print(f"[DEBUG] {function_name}: Data: {json.dumps(data, indent=2)}")
            else:
                print(f"[DEBUG] {function_name}: Data: {data}")


def debug_traceback(function_name: str):
    """Standardized debug traceback output."""
    if DEBUG:
        print(f"[DEBUG] {function_name}: Traceback: {traceback.format_exc()}")


async def main(args):
    """Strands UTCP + Bedrock integration example."""
    print("🤖 Strands UTCP + Amazon Bedrock Integration")
    print("=" * 50)
    
    # Set global debug flag
    global DEBUG
    DEBUG = args.debug
    
    # Load environment variables
    load_dotenv(Path(__file__).parent / ".env")
    
    if not BEDROCK_AVAILABLE:
        print("❌ Required dependencies not available.")
        print("Install with: pip install boto3")
        return
    
    # Check AWS credentials
    if not (os.environ.get("AWS_ACCESS_KEY_ID") and os.environ.get("AWS_SECRET_ACCESS_KEY")):
        print("Warning: AWS credentials not found in environment variables")
        print("Make sure you have configured AWS credentials using AWS CLI or environment variables")
    
    try:
        session = boto3.Session()
        credentials = session.get_credentials()
        if not credentials:
            print("❌ No AWS credentials found")
            print("Configure AWS credentials via AWS CLI or environment variables")
            return
        print("✅ AWS credentials found")
        debug_print("main", "AWS credentials validated successfully")
    except Exception as e:
        print(f"❌ AWS credential error: {e}")
        debug_traceback("main")
        return
    
    # Create UTCP tool adapter with configuration
    print("Initializing UTCP tool adapter...")
    try:
        config_path = Path(__file__).parent / "providers.json"
        debug_print("main", f"Using config path: {config_path}")
        
        # Load configuration from file
        with open(config_path, 'r') as f:
            config = json.load(f)
        debug_print("main", "Configuration loaded", config)
        
        async with UtcpToolAdapter(config) as adapter:
            print("UTCP tool adapter initialized successfully.")
            debug_print("main", "UTCP tool adapter created")
            
            # Load tools and convert to Strands format
            print("Loading UTCP tools...")
            tools = adapter.list_tools()
            print(f"Found {len(tools)} tools")
            debug_print("main", f"Loaded tools: {[tool.tool_name for tool in tools]}")
            
            if not tools:
                print("❌ No tools available. Cannot create agent.")
                return
            
            # Convert to Strands tools format
            print("Converting tools to Strands format...")
            strands_tools = adapter.to_strands_tools()
            print(f"Converted {len(strands_tools)} tools for agent use")
            debug_print("main", f"Strands tools created: {len(strands_tools)}")
            
            # Create Bedrock model
            print("Creating Bedrock model...")
            try:
                model_id = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-sonnet-20240229-v1:0")
                debug_print("main", f"Using model: {model_id}")
                
                bedrock_model = BedrockModel(
                    model_id=model_id,
                    temperature=0.1,
                    streaming=True
                )
                print(f"Bedrock model initialized successfully.")
                print(f"Using model {model_id}")
                debug_print("main", "Bedrock model created successfully")
            except Exception as e:
                print(f"Error initializing Bedrock model: {e}")
                debug_traceback("main")
                return
            
            # Create Strands agent
            print("Creating Strands agent...")
            try:
                agent = Agent(
                    model=bedrock_model,
                    tools=strands_tools,
                    system_prompt="You are a helpful assistant with access to external tools via UTCP. You can search for books and find news articles using the available APIs."
                )
                print("Agent created successfully.")
                debug_print("main", "Strands agent initialized with tools")
            except Exception as e:
                print(f"Error creating agent: {e}")
                debug_traceback("main")
                return
            
            # Interactive loop with optional initial prompt
            print("\n" + "="*50)
            print("🎯 Agent Ready! Ask questions or type 'quit' to exit")
            print("Example: 'Search for recent news about Python programming'")
            print("="*50)
            
            # Handle initial prompt if provided
            first_prompt = args.prompt if args.prompt else None
            
            while True:
                try:
                    if first_prompt:
                        user_input = first_prompt
                        print(f"\n💬 You: {user_input}")
                        first_prompt = None  # Only use it once
                    else:
                        user_input = input("\n💬 You: ").strip()
                    
                    if user_input.lower() in ['quit', 'exit', 'q']:
                        print("👋 Goodbye!")
                        break
                    
                    if not user_input:
                        continue
                    
                    debug_print("main", f"User input: {user_input}")
                    print("Sending request to Strands agent...")
                    
                    # Invoke the agent
                    response = agent(user_input)
                    debug_print("main", f"Agent response received: {type(response)}")
                    
                    # Display response
                    print(f"\nAssistant: {response}")
                    
                except KeyboardInterrupt:
                    print("\n👋 Goodbye!")
                    break
                except Exception as e:
                    print(f"Error: {e}")
                    debug_traceback("main")
                    
    except Exception as e:
        print(f"Error initializing UTCP adapter: {e}")
        debug_traceback("main")
        return


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Strands UTCP + Bedrock Integration Example")
    parser.add_argument("--debug", action="store_true", help="Enable debug output")
    parser.add_argument("--prompt", type=str, help="Initial prompt to start the conversation")
    args = parser.parse_args()
    
    # Set global debug flag
    DEBUG = args.debug
    
    asyncio.run(main(args))