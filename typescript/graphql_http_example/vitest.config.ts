import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    environment: 'node'
  },
  resolve: {
    conditions: ['node', 'import', 'module', 'default']
  }
});


