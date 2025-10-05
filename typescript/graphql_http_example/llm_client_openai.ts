import * as path from 'path';
import * as readline from 'readline';
import dotenv from 'dotenv';
import { OpenAI } from 'openai';
import type { ChatCompletionMessageParam } from 'openai/resources';

import { UtcpClient } from '@utcp/sdk/dist/src/client/utcp-client.js';
import { UtcpClientConfigSchema } from '@utcp/sdk/dist/src/client/utcp-client-config.js';
import { TextProviderSchema } from '@utcp/sdk/dist/src/shared/provider.js';
import type { TextProvider } from '@utcp/sdk/dist/src/shared/provider.js';
import type { Tool } from '@utcp/sdk/dist/src/shared/tool.js';

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

// Using OpenAI function calling; no regex extraction

// Direct tool invocation; tools are fully defined in the manual
async function callTool(utcpClient: UtcpClient, toolName: string, args: any) {
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
    'For repository discovery, call github.search_repos with {"body": {"query": "query ($q: String!, $first: Int!) {\n  search(query: $q, type: REPOSITORY, first: $first) {\n    repositoryCount\n    nodes {\n      ... on Repository { name url owner { login } description }\n    }\n  }\n}", "variables": {"q": "keywords in:name", "first": N}}}. ' +
    'For custom GraphQL, use github.graphql_query. ' +
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
        const response = await openai.chat.completions.create({
          model: 'gpt-4o-mini',
          messages,
          tools: [
            {
              type: 'function',
              function: {
                name: 'call_utcp_tool',
                description: 'Call a UTCP tool by name with arguments. Arguments should match the tool schema.',
                parameters: {
                  type: 'object',
                  properties: {
                    tool_name: { type: 'string' },
                    arguments: { type: 'object', additionalProperties: true }
                  },
                  required: ['tool_name', 'arguments']
                }
              }
            }
          ]
        });

        const choice = response.choices[0];
        const assistantMsg: any = choice.message;
        const toolCalls = assistantMsg.tool_calls || [];
        const assistantContent = assistantMsg.content || '';

        if (!toolCalls.length) {
          console.log('Assistant:', assistantContent);
          history.push({ role: 'user', content: userPrompt }, { role: 'assistant', content: assistantContent });
          if (history.length > MAX_HISTORY_MESSAGES) {
            history.splice(0, history.length - MAX_HISTORY_MESSAGES);
          }
          break;
        }

        const newMessages: ChatCompletionMessageParam[] = [
          { role: 'system', content: systemPrompt },
          ...history,
          { role: 'user', content: userPrompt },
          assistantMsg as ChatCompletionMessageParam
        ];

        for (const call of toolCalls) {
          if (call.type !== 'function' || call.function?.name !== 'call_utcp_tool') continue;
          const payloadText = call.function?.arguments || '{}';
          let payload: any = {};
          try {
            payload = JSON.parse(payloadText);
          } catch {
            console.error('Failed to parse tool arguments JSON');
            continue;
          }

          const toolName: string = payload.tool_name;
          const args = normalizeArguments(payload.arguments);
          console.log(`\nExecuting: ${toolName} with args: ${JSON.stringify(args, null, 2)}`);

          let toolOutput = '';
          try {
            const result: any = await callTool(utcpClient, toolName, args);
            const errors: any[] | undefined = Array.isArray(result?.errors) ? result.errors : undefined;
            if (errors && errors.length > 0) {
              const summaries = errors.map(e => (e?.message ?? JSON.stringify(e))).slice(0, 3);
              console.error(`GraphQL errors (${errors.length}): ${summaries.join(' | ')}`);
              toolOutput = JSON.stringify({
                ok: false,
                error_count: errors.length,
                error_messages: errors.map(e => e?.message ?? String(e)),
                data: result?.data ?? null,
                errors
              });
            } else {
              toolOutput = JSON.stringify({ ok: true, data: result?.data ?? result });
            }
          } catch (e: any) {
            toolOutput = `Error calling ${toolName}: ${e?.message || String(e)}`;
            console.error(toolOutput);
          }

          newMessages.push({
            role: 'tool',
            // @ts-expect-error: tool_call_id is a valid property for tool role in OpenAI tools
            tool_call_id: call.id,
            content: toolOutput
          } as any);

          if (history.length > MAX_HISTORY_MESSAGES) {
            history.splice(0, history.length - MAX_HISTORY_MESSAGES);
          }
        }

        messages = newMessages;
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
