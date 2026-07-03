# Xquik OpenAPI UTCP example

This example shows how to register Xquik's public OpenAPI document as a UTCP HTTP provider. It lets a UTCP client discover Xquik tools for X data workflows such as tweet search, user lookup, follower export, monitoring, webhooks, and write actions.

The script only lists matching tools by default. Set a real `XQUIK_API_KEY` before calling any Xquik endpoint.

## Setup

```sh
pip install -r requirements.txt
```

Edit `example.env` and replace the placeholder value:

```sh
XQUIK_API_KEY=xq_replace_with_your_key
```

## Run

```sh
python xquik_openapi_example.py
```

The example loads `providers.json`, fetches <https://xquik.com/openapi.json>, registers the discovered tools, and prints the first matching tools.

## Notes

- Keep API keys in local environment files or a secret store.
- Do not commit real API keys.
- Xquik MCP setup is documented at <https://docs.xquik.com/mcp/overview>.
