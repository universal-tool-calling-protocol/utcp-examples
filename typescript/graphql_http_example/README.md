## TypeScript UTCP - GraphQL via HTTP Provider (GitHub GraphQL)

This example shows how to call a GraphQL API (GitHub GraphQL) using UTCP's HTTP provider. It defines a UTCP manual that models a generic GraphQL query tool and uses a bearer token loaded from `.env` for authentication.

### Prerequisites
- Node.js 18+
- A GitHub Personal Access Token with `public_repo` (or relevant) scopes

### Setup
1. Install dependencies:
```bash
npm install
```
2. Create `.env` from `example.env` and set your environment variables:
```bash
cp example.env .env
```

### Files
- `graphql_manual.json`: UTCP manual with GraphQL-powered tools
  - `github.graphql_query`: Execute any GitHub GraphQL query
  - `github.search_repos`: Search public repositories by keywords (convenience wrapper over GraphQL search)
- `llm_client_openai.ts`: OpenAI-driven client that lets the LLM decide the query and variables (and use `github.search_repos` for discovery)
- `package.json`, `tsconfig.json`: Project configuration

### Key benefits
- **Zero server scaffolding**: Model GraphQL operations as UTCP tools without writing any backend glue. The manual captures auth, headers, and body shape once; every consumer benefits.
- **LLM-ready by construction**: Tools are discoverable, have JSON schemas, and can be surfaced to an LLM for autonomous tool use (query selection, variable filling, and retries).
- **Security by configuration**: Tokens and headers are injected via variable loaders (`.env` here). Swap in a secret manager later without touching call sites.
- **Portable across stacks**: The exact same manual can be used by different clients (TS/Python) and different LLM backends (OpenAI, Bedrock) with no API rewrites.


### Running with LLM variant (OpenAI)
1. Ensure `.env` has both `GITHUB_TOKEN` and `OPENAI_API_KEY`.
2. Run the LLM client:
```bash
npm run start:llm
```
3. Try prompts like:
- "What is my login?"
- "Search public repos for 'utcp' and list top 5 with URLs"
- "Find repositories mentioning 'universal tool calling' (any owner) and show name + URL"
- "Limit to my account: search my repos for 'agent' in the name"

### Testing without hitting GitHub
1. Install dev deps (already in `package.json`): `npm i`
2. Run tests: `npm test`
3. We use `nock` to mock `https://api.github.com/graphql` so queries resolve locally.

The client supports multi-step tool use. For repo discovery:
- The model can call `github.graphql_query` to get `viewer.login`, then use `github.search_repos` with either global keywords or `user:LOGIN` scoping.


