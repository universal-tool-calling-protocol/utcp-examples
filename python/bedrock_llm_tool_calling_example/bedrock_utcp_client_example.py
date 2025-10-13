"""
UTCP Amazon Bedrock Integration Example

This example demonstrates how to:
1. Initialize a UTCP client with tool providers from a config file
2. For each user request, search for relevant tools
3. Instruct Amazon Bedrock to respond with a tool call
4. Parse the tool call and execute it using the UTCP client
5. Return the results to Amazon Bedrock for a final response
"""

import asyncio
import os
import json
import argparse
from pathlib import Path
from typing import Dict, Any, List, Tuple
import uuid
import traceback

import boto3
from dotenv import load_dotenv

from utcp.utcp_client import UtcpClient
from utcp.data.tool import Tool

# Global debug flag
DEBUG = False

# Amazon Bedrock model ID - use environment variable with fallback
modelId = os.environ.get('BEDROCK_MODEL_ID', 'anthropic.claude-3-sonnet-20240229-v1:0')


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


def validate_message_content(message):
    """
    Validate that a message has non-empty content.
    
    Args:
        message: Message dictionary with role and content
        
    Returns:
        bool: True if message has valid content, False otherwise
    """
    if not isinstance(message, dict):
        return False
    
    content = message.get("content", [])
    if not content:
        return False
    
    if isinstance(content, list):
        for item in content:
            if isinstance(item, dict):
                if "text" in item and item["text"].strip():
                    return True
                if "toolResult" in item:
                    return True
                if "toolUse" in item:
                    return True
            elif isinstance(item, str) and item.strip():
                return True
        return False
    
    return bool(content)

async def initialize_utcp_client() -> UtcpClient:
    """Initialize the UTCP client with configuration."""
    try:
        # Load configuration from the providers.json file
        config_path = str(Path(__file__).parent / "providers.json")
        client = await UtcpClient.create(config=config_path)
        return client
    except Exception as e:
        print(f"Error in initialize_utcp_client: {str(e)}")
        debug_traceback("initialize_utcp_client")
        raise


def format_tools_for_bedrock(tools: List[Tool]) -> Tuple[List[Dict[str, Any]], Dict[str, str]]:
    """
    Convert UTCP tools to Bedrock tool format.
    
    Args:
        tools: List of UTCP tools
        
    Returns:
        Tuple containing:
        - List of tools formatted for Bedrock
        - Mapping between modified tool names and original names
    """
    try:
        bedrock_tools = []
        tool_name_mapping = {}
        
        for tool in tools:
            # Use exclude_none=True to remove UTCP's null fields that break Bedrock validation
            schema = tool.model_dump(exclude_none=True)
        
            # Create the input schema JSON
            input_schema_json = {
                "type": "object",
                "properties": {},
                "required": []
            }
            
            # Add inputs to the input schema
            if "inputs" in schema and "properties" in schema["inputs"]:
                input_schema_json["properties"] = schema["inputs"]["properties"]
                if "required" in schema["inputs"]:
                    input_schema_json["required"] = schema["inputs"]["required"]
            
            # Replace periods in tool name with underscores
            original_name = tool.name
            bedrock_tool_name = original_name.replace(".", "_")
            
            # Truncate if longer than 64 characters (Bedrock's limit)
            if len(bedrock_tool_name) > 64:
                short_uuid = str(uuid.uuid4())[:8]
                short_name = f"{bedrock_tool_name[:55]}_{short_uuid}"
                debug_print("format_tools_for_bedrock", f"Tool name '{bedrock_tool_name}' is too long, using '{short_name}' instead")
                bedrock_tool_name = short_name
            
            # Store the mapping between the modified name and original name
            tool_name_mapping[bedrock_tool_name] = original_name
            
            # Format the tool for Bedrock
            tool_spec = {
                "name": bedrock_tool_name,
                "description": tool.description,
                "inputSchema": {
                    "json": input_schema_json
                }
            }
        
            bedrock_tools.append({"toolSpec": tool_spec})
        
        return bedrock_tools, tool_name_mapping
    except Exception as e:
        print(f"Error in format_tools_for_bedrock: {str(e)}")
        debug_traceback("format_tools_for_bedrock")
        raise


async def get_bedrock_response(messages: List[Dict[str, str]], tools=None, system_prompt=None) -> Dict[str, Any]:
    """
    Get a response from Amazon Bedrock using the Converse API.
    
    Args:
        messages: List of conversation messages
        tools: Optional list of tools formatted for Bedrock
        system_prompt: Optional system prompt
        
    Returns:
        Response from Bedrock Converse API
    """
    bedrock_runtime = boto3.client('bedrock-runtime')
    
    # Add tools configuration if provided
    tool_config = None
    if tools:
        tool_config = {"tools": tools}
        debug_print("get_bedrock_response", "Tool config", tool_config)
    
    # Prepare system prompt if provided
    system = None
    if system_prompt:
        system = [{"text": system_prompt}]
    
    try:
        # Build the API call parameters
        converse_params = {
            "modelId": modelId,
            "messages": messages
        }
        
        # Add optional parameters if provided
        if tool_config:
            converse_params["toolConfig"] = tool_config
        
        if system:
            converse_params["system"] = system
        
        debug_print("get_bedrock_response", "Calling Bedrock converse API...")
            
        response = bedrock_runtime.converse(**converse_params)
        
        debug_print("get_bedrock_response", "Bedrock API call successful")
        debug_print("get_bedrock_response", f"Response keys: {list(response.keys())}")
        debug_print("get_bedrock_response", "Response structure", response)
        
        return response
    except Exception as e:
        print(f"Error in get_bedrock_response: {str(e)}")
        debug_traceback("get_bedrock_response")
        raise


def extract_text_from_content(content):
    """
    Extract text from a content block or list of content blocks.
    
    Args:
        content: Content block or list of content blocks
        
    Returns:
        Extracted text or empty string if no text found
    """
    try:
        if not content:
            return ""
            
        if isinstance(content, list):
            for item in content:
                if isinstance(item, dict) and "text" in item:
                    return item["text"]
                elif isinstance(item, str):
                    return item
            return ""
        elif isinstance(content, dict) and "text" in content:
            return content["text"]
        elif isinstance(content, str):
            return content
        
        return ""
    except Exception as e:
        print(f"Error in extract_text_from_content: {str(e)}")
        debug_traceback("extract_text_from_content")
        return ""


async def process_bedrock_response_with_tools(utcp_client, response, tool_name_mapping, bedrock_tools, system_prompt, conversation_history):
    """
    Recursively process Bedrock responses that may contain tool calls until we get a final text response.
    
    Args:
        utcp_client: UTCP client instance
        response: Bedrock response
        tool_name_mapping: Mapping between modified tool names and original names
        bedrock_tools: Formatted tools for Bedrock
        system_prompt: System prompt
        conversation_history: Current conversation history
        
    Returns:
        Final text response from the assistant
    """
    try:
        if "output" not in response or "message" not in response["output"]:
            return "Error: Unexpected response format."
            
        message = response["output"]["message"]
        
        # Check if this response contains tool calls
        if response.get("stopReason") == "tool_use":
            # Add the assistant's message to conversation history
            conversation_history.append(message)
            
            # Process any text content first
            for content_block in message["content"]:
                if "text" in content_block:
                    print(f"\nAssistant: {content_block['text']}")
            
            # Process all tool calls in this message
            tool_results = []
            for content_block in message["content"]:
                if "toolUse" in content_block:
                    tool_result = await process_tool_calls(
                        utcp_client, 
                        content_block["toolUse"], 
                        tool_name_mapping
                    )
                    tool_results.append(tool_result)
            
            # Add tool results to conversation history
            if tool_results:
                tool_results_message = {
                    "role": "user", 
                    "content": tool_results
                }
                if validate_message_content(tool_results_message):
                    conversation_history.append(tool_results_message)
                
                # Get the next response from Bedrock
                print("\nSending tool results to Amazon Bedrock for interpretation...")
                
                next_messages = conversation_history.copy()
                next_response = await get_bedrock_response(next_messages, bedrock_tools, system_prompt)
                
                # Recursively process the next response (it might also contain tool calls)
                return await process_bedrock_response_with_tools(
                    utcp_client, next_response, tool_name_mapping, 
                    bedrock_tools, system_prompt, conversation_history
                )
        else:
            # This is a final text response
            final_text = extract_text_from_content(message.get("content", []))
            if final_text.strip() and validate_message_content(message):
                conversation_history.append(message)
                return final_text
            else:
                # If no text content, return a default message
                return "I apologize, but I couldn't generate a proper response. Please try rephrasing your question."
            
    except Exception as e:
        debug_print("process_bedrock_response_with_tools", f"Error: {str(e)}")
        debug_traceback("process_bedrock_response_with_tools")
        return f"Error processing response: {str(e)}"


async def process_tool_calls(utcp_client, tool_use, tool_name_mapping):
    """
    Process a tool call and execute it using the UTCP client.
    
    Args:
        utcp_client: UTCP client instance
        tool_use: Tool use information from Bedrock
        tool_name_mapping: Mapping between modified tool names and original names
        
    Returns:
        Dictionary containing tool result information
    """
    try:
        tool_use_id = tool_use["toolUseId"]
        modified_tool_name = tool_use["name"]
        
        # Map the modified tool name back to the original tool name
        original_tool_name = tool_name_mapping.get(modified_tool_name, modified_tool_name)
        
        print(f"\nTool call detected: {original_tool_name}")
        
        # Get the tool arguments
        tool_args = tool_use["input"]
        print(f"Arguments: {json.dumps(tool_args, indent=2)}")
        debug_print("process_tool_calls", f"Tool arguments for {original_tool_name}", tool_args)
        
        try:
            print(f"Executing tool call: {original_tool_name}")
            debug_print("process_tool_calls", f"Executing tool: {original_tool_name}")
            result = await utcp_client.call_tool(original_tool_name, tool_args)
            print(f"Tool execution successful!")
            print(f"Result: {result}")
            debug_print("process_tool_calls", f"Tool execution result for {original_tool_name}", result)
            
            # Format the tool result as expected by Bedrock
            return {
                "toolResult": {
                    "toolUseId": tool_use_id,
                    "content": [{"json": result}]
                }
            }
        except Exception as e:
            error_message = f"Error calling {original_tool_name}: {str(e)}"
            print(f"Error: {error_message}")
            debug_traceback("process_tool_calls")
            
            # Format the error as a tool result
            return {
                "toolResult": {
                    "toolUseId": tool_use_id,
                    "content": [{"json": {"error": str(e)}}]
                }
            }
    except Exception as e:
        print(f"Error in process_tool_calls: {str(e)}")
        debug_traceback("process_tool_calls")
        # Return a generic error response if we can't even parse the tool_use
        return {
            "toolResult": {
                "toolUseId": "unknown",
                "content": [{"json": {"error": f"Failed to process tool call: {str(e)}"}}]
            }
        }


async def main(initial_prompt=None):
    """Main function to demonstrate Amazon Bedrock with UTCP integration."""
    load_dotenv(Path(__file__).parent / ".env")
    
    # Check for AWS credentials
    if not (os.environ.get("AWS_ACCESS_KEY_ID") and os.environ.get("AWS_SECRET_ACCESS_KEY")):
        print("Warning: AWS credentials not found in environment variables")
        print("Make sure you have configured AWS credentials using AWS CLI or environment variables")
    
    print("Initializing UTCP client...")
    try:
        utcp_client = await initialize_utcp_client()
        print("UTCP client initialized successfully.")
        print(f"Using model {modelId}")
    except Exception as e:
        print(f"Failed to initialize UTCP client: {str(e)}")
        return

    conversation_history = []
    tool_name_mapping = {}

    system_prompt = (
        "You are a helpful assistant with access to external tools. Use your judgment to decide when tools "
        "are beneficial versus when you can provide a better answer from your knowledge. "
        "Prefer using tools when:\n"
        "- The query requires real-time or current information (news, weather, stock prices)\n"
        "- You need to search specific databases or APIs (books, articles, specific data)\n"
        "- The information might have changed since your training data\n"
        "Use your internal knowledge when:\n"
        "- The query involves general knowledge, math, or well-established facts\n"
        "- The available tools are not relevant or helpful for the specific question\n"
        "- You can provide a complete and accurate answer without external data\n"
        "When you do use a tool, analyze the required parameters carefully and provide them accurately."
    )

    # Handle initial prompt if provided
    first_iteration = True
    
    while True:
        if first_iteration and initial_prompt:
            user_prompt = initial_prompt
            print(f"\nUsing provided prompt: {user_prompt}")
            first_iteration = False
        else:
            user_prompt = input("\nEnter your prompt (or 'exit' to quit): ")
            if user_prompt.lower() in ["exit", "quit"]:
                break

        print("\nSearching for relevant tools...")
        try:
            relevant_tools = await utcp_client.search_tools(user_prompt, limit=10)
            
            if relevant_tools:
                print(f"Found {len(relevant_tools)} relevant tools.")
                for tool in relevant_tools:
                    print(f"- {tool.name}")
            else:
                print("No relevant tools found.")

            # Get the formatted tools and the mapping between modified and original names
            bedrock_tools, name_mapping = format_tools_for_bedrock(relevant_tools)
            tool_name_mapping.update(name_mapping)
        except Exception as e:
            print(f"Error searching for tools: {str(e)}")
            debug_traceback("main")
            # Continue with empty tools list
            relevant_tools = []
            bedrock_tools = []
            name_mapping = {}

        # Prepare messages for Bedrock
        messages = conversation_history.copy()
        messages.append({"role": "user", "content": [{"text": user_prompt}]})

        # Debug: Print conversation history structure
        if DEBUG:
            debug_print("main", f"Conversation history length: {len(conversation_history)}")
            for i, msg in enumerate(conversation_history):
                debug_print("main", f"Message {i}: role={msg.get('role')}, content_type={type(msg.get('content'))}")

        print("\nSending request to Amazon Bedrock...")
        try:
            response = await get_bedrock_response(messages, bedrock_tools, system_prompt)
            
            # Process the response
            if "output" not in response or "message" not in response["output"]:
                print(f"Error: Unexpected response format. Missing 'output.message' key.")
                debug_print("main", "Unexpected response format", response)
                continue
                
            assistant_message = response["output"]["message"]
            
            # Add user message to conversation history BEFORE processing response
            conversation_history.append({"role": "user", "content": [{"text": user_prompt}]})
            
            # Check if the stop reason is tool_use or handle any response
            if response.get("stopReason") == "tool_use":
                # Use the recursive function to handle all tool calls until we get a final response
                final_text = await process_bedrock_response_with_tools(
                    utcp_client, response, tool_name_mapping, 
                    bedrock_tools, system_prompt, conversation_history
                )
                if final_text and final_text.strip():
                    print(f"\nAssistant's final response: {final_text}")
                else:
                    print(f"\nAssistant completed the tool calls but didn't provide a final response.")
            else:
                # No tool call, just display the response
                assistant_text = extract_text_from_content(assistant_message.get("content", []))
                if assistant_text and assistant_text.strip() and validate_message_content(assistant_message):
                    print(f"\nAssistant: {assistant_text}")
                    conversation_history.append(assistant_message)
                else:
                    print(f"\nError: Unexpected assistant message format")
                    debug_print("main", "Unexpected assistant message format", assistant_message)

                
        except Exception as e:
            print(f"Error calling Amazon Bedrock: {str(e)}")
            debug_traceback("main")


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="UTCP Amazon Bedrock Integration Example")
    parser.add_argument("--debug", action="store_true", help="Enable debug output")
    parser.add_argument("--prompt", type=str, help="Start with this prompt instead of waiting for user input")
    args = parser.parse_args()
    
    # Set global debug flag
    DEBUG = args.debug
    
    asyncio.run(main(args.prompt))
