import asyncio
import traceback
from os import getcwd
from typing import Literal, Optional
from google.cloud import secretmanager
from utcp.exceptions import UtcpSerializerValidationError
from utcp.interfaces.serializer import Serializer
from utcp.plugins.discovery import register_variable_loader
from utcp.utcp_client import UtcpClient
from utcp.data.utcp_client_config import UtcpClientConfigSerializer
from utcp.data.variable_loader import VariableLoader


class GcpSecretManager(VariableLoader):
    """Configuration for UTCP GCP Secret Manager client."""
    variable_loader_type: Literal["gcp_secret_manager"] = "gcp_secret_manager"
    project_id: str

    def __init__(self, variable_loader_type: Literal["gcp_secret_manager"], project_id: str):
        super().__init__(variable_loader_type=variable_loader_type, project_id=project_id)
        self._client: secretmanager.SecretManagerServiceClient = secretmanager.SecretManagerServiceClient()

    def get(self, key: str, version: str = "latest") -> Optional[str]:
        """Get a specific secret by key."""
        request = {"name": f"projects/{self.project_id}/secrets/{key}/versions/{version}"}
        response = self._client.access_secret_version(request=request)
        secret_value = response.payload.data.decode('UTF-8')
        return secret_value

class GcpSecretManagerSerializer(Serializer[GcpSecretManager]):
    def validate_dict(self, obj: dict) -> GcpSecretManager:
        try:
            return GcpSecretManager.model_validate(obj)
        except UtcpSerializerValidationError as e:
            raise UtcpSerializerValidationError("Invalid GcpSecretManager: " + traceback.format_exc()) from e

    def to_dict(self, obj: GcpSecretManager) -> dict:
        return obj.model_dump()

async def main():
    register_variable_loader("gcp_secret_manager", GcpSecretManagerSerializer())
    config = UtcpClientConfigSerializer().validate_dict(
        {
            "manual_call_templates": [
                {
                    "name": "test_provider",
                    "call_template_type": "http",
                    "http_method": "GET",
                    "url": "http://localhost:8080/utcp",
                    "auth": {
                        "auth_type": "api_key",
                        "api_key": "Bearer $API_KEY",
                        "var_name": "Authorization",
                        "location": "header"
                    }
                }
            ],
            "load_variables_from": [
                {
                    "variable_loader_type": "gcp_secret_manager",
                    "project_id": "your-gcp-project-id"
                }
            ],
        }
    )

    client: UtcpClient = await UtcpClient.create(root_dir=getcwd(), config=config)

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
