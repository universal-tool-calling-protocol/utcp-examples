import asyncio
from os import getcwd
from utcp.utcp_client import UtcpClient
from utcp.data.utcp_client_config import UtcpClientConfigSerializer

async def main():
    client: UtcpClient = await UtcpClient.create(
        root_dir=getcwd(),
        config=UtcpClientConfigSerializer().validate_dict(
            {
                "manual_call_templates": [
                    {
                        "name": "playwright",
                        "call_template_type": "text",
                        "file_path": "mcp_manual.json"
                    }
                ]
            }
        )
    )

    # List all available tools
    print("Registered tools:")
    tools = await client.search_tools("", limit=30)
    for tool in tools:
        print(f" - {tool.name}")

    # Call one of the tools
    if tools:
        tool_to_call = "playwright.mcp_playwright.browser_navigate"
        args = {"url": "https://www.google.com"}

        result = await client.call_tool(tool_to_call, args)
        print(f"\nTool call result for '{tool_to_call}':")
        print(result)

        tool_to_call = "playwright.mcp_playwright.browser_close"
        result = await client.call_tool(tool_to_call, {})
        print(f"\nTool call result for '{tool_to_call}':")
        print(result)
    else:
        print("No tools found.")

if __name__ == "__main__":
    asyncio.run(main())
