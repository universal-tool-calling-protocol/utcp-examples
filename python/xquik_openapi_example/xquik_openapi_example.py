import asyncio
import json
from pathlib import Path

from utcp.data.utcp_client_config import UtcpClientConfigSerializer
from utcp.utcp_client import UtcpClient


async def main():
    base_dir = Path(__file__).parent
    config_path = base_dir / "providers.json"
    config_data = json.loads(config_path.read_text(encoding="utf-8"))

    for variable_loader in config_data.get("load_variables_from", []):
        if variable_loader.get("variable_loader_type") == "dotenv":
            variable_loader["env_file_path"] = str(base_dir / "example.env")

    config = UtcpClientConfigSerializer().validate_dict(config_data)
    client = await UtcpClient.create(root_dir=str(base_dir), config=config)

    tools = await client.search_tools("tweet search user lookup follower export", limit=12)
    print("Matching Xquik tools:")
    for tool in tools:
        description = getattr(tool, "description", "")
        print(f" - {tool.name}: {description}")

    print("\nSet XQUIK_API_KEY in example.env before calling a Xquik tool.")


if __name__ == "__main__":
    asyncio.run(main())
