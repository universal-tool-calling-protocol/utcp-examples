import asyncio
from os import getcwd
from utcp.utcp_client import UtcpClient
from utcp.data.utcp_client_config import UtcpClientConfigSerializer
from utcp.data.variable_loader import VariableLoaderSerializer

async def main():
    client: UtcpClient = await UtcpClient.create(
        root_dir=getcwd(),
        config=UtcpClientConfigSerializer().validate_dict(
            {
                "load_variables_from": [
                    VariableLoaderSerializer().validate_dict({
                        "variable_loader_type": "dotenv",
                        "env_file_path": "example.env"
                    })
                ],
                "manual_call_templates": [
                    {
                        "name": "my_cli",
                        "call_template_type": "text",
                        "file_path": "cli_manual.json"
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
        args = {"text": "TestText"}

        result = await client.call_tool(tool_to_call, args)
        print(f"\nTool call result for '{tool_to_call}':")
        print(result)
    else:
        print("No tools found.")

if __name__ == "__main__":
    asyncio.run(main())
