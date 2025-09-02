# UTCP Secret Manager Example

This example demonstrates how to integrate the `utcp-client` with Google Cloud Secret Manager to securely load secrets and use them in your UTCP tool calls.

## How it Works

1. **`client.py`**:
    - Registers a custom variable loader for GCP Secret Manager.
    - Loads configuration from a secret using the loader.
    - Initializes the `UtcpClient` with the loaded configuration.
    - Lists available tools and calls one of them.

2. **Tool Manual**:
    - The tool manual (`manual_call_templates` in the config) can reference secrets loaded via the variable loader.
    - You should update your tool manual to use a secret, for example by referencing a secret value in the URL or headers.

## Example Usage

Suppose you have a secret named `api-key` in your GCP project. You can update your tool manual like this:

```json
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
  ]
}
```

This will automatically inject the secret value into the tool call.

## Setup

1. **Install requirements**:
    ```sh
    pip install -r requirements.txt
    ```

2. **Set up Google Cloud credentials**:
    - Make sure your environment is authenticated to GCP.

## Running the Example

1. **Start your UTCP server** (if needed):
    ```sh
    uvicorn server:app --host 0.0.0.0 --port 8080 --reload
    ```

2. **Run the client**:
    ```sh
    python client.py
    ```

You should see a list of registered tools and the result of a tool call.

## Notes

- Update your tool manual to use secrets as shown above.
- Make sure the secret exists in your GCP project.
