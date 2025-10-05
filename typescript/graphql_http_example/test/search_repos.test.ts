import { describe, it, expect, beforeAll, afterAll } from 'vitest';
import nock from 'nock';
import { UtcpClient } from '@utcp/sdk/dist/src/client/utcp-client.js';
import { UtcpClientConfigSchema } from '@utcp/sdk/dist/src/client/utcp-client-config.js';
import { TextProviderSchema } from '@utcp/sdk/dist/src/shared/provider.js';
import * as path from 'path';

describe('github.search_repos (mocked)', () => {
  let client: any;

  beforeAll(async () => {
    nock.disableNetConnect();
    nock('https://api.github.com')
      .post('/graphql')
      .reply(200, {
        data: {
          search: {
            repositoryCount: 1,
            nodes: [
              { name: 'utcp-examples', url: 'https://github.com/org/utcp-examples', owner: { login: 'org' }, description: 'examples' }
            ]
          }
        }
      });

    const manualProvider = TextProviderSchema.parse({
      name: 'github',
      provider_type: 'text',
      file_path: path.join(process.cwd(), 'graphql_manual.json')
    });

    client = await UtcpClient.create(UtcpClientConfigSchema.parse({
      variables: { GITHUB_TOKEN: 'test-token' },
      load_variables_from: []
    }));
    await client.register_tool_provider(manualProvider);
  });

  afterAll(() => {
    nock.cleanAll();
    nock.enableNetConnect();
  });

  it('returns mocked search results', async () => {
    const query = `query ($q: String!, $first: Int!) {\n  search(query: $q, type: REPOSITORY, first: $first) {\n    repositoryCount\n    nodes {\n      ... on Repository { name url owner { login } description }\n    }\n  }\n}`;
    const result = await client.call_tool('github.search_repos', {
      body: {
        query,
        variables: {
          q: 'utcp in:name',
          first: 1
        }
      }
    });

    expect(result?.data?.search?.repositoryCount).toBe(1);
    expect(result?.data?.search?.nodes?.[0]?.name).toBe('utcp-examples');
  });
});


