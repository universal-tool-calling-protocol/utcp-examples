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
                        "name": "test_manual",
                        "call_template_type": "http",
                        "http_method": "GET",
                        "url": "http://localhost:8080/utcp"
                    }
                ]
            }
        )
    )

    # List all available tools
    print("Registered tools:")
    tools = await client.search_tools("")
    for tool in tools:
        print(f" - {tool.name}")

    # Call one of the tools
    if tools:
        tool_to_call = tools[0].name
        args = {"body": {"value": "test"}}

        result = await client.call_tool(tool_to_call, args)
        print(f"\nTool call result for '{tool_to_call}':")
        print(result)
    else:
        print("No tools found.")

if __name__ == "__main__":
    asyncio.run(main())
