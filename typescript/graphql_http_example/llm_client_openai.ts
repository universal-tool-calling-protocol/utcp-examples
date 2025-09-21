import * as path from 'path';
import * as readline from 'readline';
import dotenv from 'dotenv';
import { OpenAI } from 'openai';
import type { ChatCompletionMessageParam } from 'openai/resources';

import { UtcpClient, UtcpClientConfigSchema, TextProviderSchema, TextProvider, Tool } from '@utcp/sdk';

function createReadline() {
  return readline.createInterface({ input: process.stdin, output: process.stdout });
}

function ask(rl: readline.Interface, prompt: string) {
  return new Promise<string>(resolve => rl.question(prompt, resolve));
}

function sanitizeToolsForPrompt(tools: Tool[]): any[] {
  // Redact provider and headers; expose only safe, schema-relevant fields
  return tools.map((t: any) => ({
    name: t?.name,
    description: t?.description,
    tags: t?.tags,
    inputs: t?.inputs,
    outputs: t?.outputs
  }));
}

function formatToolsForPrompt(tools: Tool[]): string {
  return JSON.stringify(sanitizeToolsForPrompt(tools), null, 2);
}

function normalizeArguments(arguments_: any): any {
  // Ensure we always send { body: { query, variables? } }
  if (arguments_ && typeof arguments_ === 'object') {
    if (arguments_.body && typeof arguments_.body === 'object') {
      return { body: arguments_.body };
    }
    const { query, variables } = arguments_;
    const body: any = {};
    if (typeof query === 'string') body.query = query;
    if (variables && typeof variables === 'object') body.variables = variables;
    if (Object.keys(body).length > 0) return { body };
  }
  return arguments_;
}

async function initializeClient(): Promise<UtcpClient> {
  const manualProvider: TextProvider = TextProviderSchema.parse({
    name: 'github',
    provider_type: 'text',
    file_path: './graphql_manual.json'
  });

  const client = await UtcpClient.create(UtcpClientConfigSchema.parse({
    variables: {},
    load_variables_from: [
      {
        type: 'dotenv',
        env_file_path: path.join(process.cwd(), '.env')
      }
    ]
  }));

  await client.register_tool_provider(manualProvider);
  return client;
}

async function getOpenAIResponse(openai: OpenAI, messages: ChatCompletionMessageParam[]): Promise<string> {
  const response = await openai.chat.completions.create({
    model: 'gpt-4o-mini',
    messages
  });
  return response.choices[0]?.message?.content || '';
}

function extractToolJson(text: string): any | null {
  const match = text.match(/```json\n({[\s\S]*?})\n```/s) || text.match(/({[\s\S]*})/s);
  if (!match) return null;
  try {
    return JSON.parse(match[1] || '{}');
  } catch {
    return null;
  }
}

function buildSearchQuery(keywords: string, limit: number, user?: string) {
  const q = user ? `user:${user} ${keywords} in:name` : `${keywords} in:name`;
  return {
    query: `query ($q: String!, $first: Int!) {\n  search(query: $q, type: REPOSITORY, first: $first) {\n    repositoryCount\n    nodes {\n      ... on Repository { name url owner { login } description }\n    }\n  }\n}`,
    variables: { q, first: Math.max(1, Math.min(50, limit || 10)) }
  };
}

async function callTool(utcpClient: UtcpClient, toolName: string, args: any) {
  // Allow a higher-level tool alias for convenience
  if (toolName === 'github.search_repos') {
    const keywords = typeof args?.keywords === 'string' ? args.keywords : '';
    const limit = typeof args?.limit === 'number' ? args.limit : 10;
    const user = typeof args?.user === 'string' ? args.user : undefined;
    const { query, variables } = buildSearchQuery(keywords, limit, user);
    return await utcpClient.call_tool('github.graphql_query', { body: { query, variables } });
  }
  return await utcpClient.call_tool(toolName, args);
}

async function main() {
  dotenv.config({ path: path.join(process.cwd(), '.env') });
  if (!process.env.OPENAI_API_KEY) {
    console.error('Missing OPENAI_API_KEY in .env');
    process.exit(1);
  }
  if (!process.env.GITHUB_TOKEN) {
    console.error('Missing GITHUB_TOKEN in .env');
    process.exit(1);
  }

  const utcpClient = await initializeClient();
  const tools = await utcpClient.search_tools('');
  const toolsJson = formatToolsForPrompt(tools);

  const systemPrompt =
    'You are a helpful assistant with access to two tools: a generic GraphQL executor and a convenience repository search tool. ' +
    'When you need to use a tool, respond ONLY with a JSON object with keys "tool_name" and "arguments". ' +
    'Do not add any other text. The "arguments" must be a JSON object. ' +
    'Prefer github.search_repos when the user asks for repository discovery without a specific query structure; fallback to github.graphql_query for custom queries. ' +
    'Search guidance: use keywords and optionally scope by user login. ' +
    `Available tools:\n${toolsJson}`;

  const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });
  const rl = createReadline();
  const history: ChatCompletionMessageParam[] = [];
  const MAX_HISTORY_MESSAGES = 20;

  try {
    while (true) {
      const userPrompt = await ask(rl, "\nEnter your request (or 'exit'): ");
      if (userPrompt.toLowerCase() === 'exit' || userPrompt.toLowerCase() === 'quit') break;

      // Start a tool/answer loop allowing multiple tool invocations
      let messages: ChatCompletionMessageParam[] = [
        { role: 'system', content: systemPrompt },
        ...history,
        { role: 'user', content: userPrompt }
      ];

      while (true) {
        const assistant = await getOpenAIResponse(openai, messages);
        const toolJson = extractToolJson(assistant);

        if (!toolJson || !toolJson.tool_name || typeof toolJson.arguments !== 'object') {
          console.log('Assistant:', assistant);
          history.push({ role: 'user', content: userPrompt }, { role: 'assistant', content: assistant });
          if (history.length > MAX_HISTORY_MESSAGES) {
            history.splice(0, history.length - MAX_HISTORY_MESSAGES);
          }
          break;
        }

        const toolName: string = toolJson.tool_name;
        const args = normalizeArguments(toolJson.arguments);
        console.log(`\nExecuting: ${toolName} with args: ${JSON.stringify(args, null, 2)}`);

        let toolOutput = '';
        try {
          // Basic validation for alias to avoid empty searches
          if (toolName === 'github.search_repos') {
            const kw = (args?.keywords ?? '').toString().trim();
            if (!kw) {
              throw new Error('keywords is required for github.search_repos');
            }
          }
          const result = await callTool(utcpClient, toolName, args);
          toolOutput = JSON.stringify(result);
        } catch (e: any) {
          toolOutput = `Error calling ${toolName}: ${e?.message || String(e)}`;
          console.error(toolOutput);
        }

        // Extend the conversation with the tool decision and output
        messages = [
          { role: 'system', content: systemPrompt },
          ...history,
          { role: 'user', content: userPrompt },
          { role: 'assistant', content: JSON.stringify(toolJson) },
          { role: 'user', content: `Tool output: ${toolOutput}. If needed, call another tool. Otherwise, answer.` }
        ];

        if (history.length > MAX_HISTORY_MESSAGES) {
          history.splice(0, history.length - MAX_HISTORY_MESSAGES);
        }

        continue;
      }
    }
  } finally {
    rl.close();
  }
}

// Direct invocation for ES modules
main().catch(err => {
  console.error('Error in main:', err);
  process.exit(1);
});
