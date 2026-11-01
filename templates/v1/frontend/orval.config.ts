import { defineConfig } from 'orval'

export default defineConfig({
  api: {
    input: './openapi/api.json',
    output: {
      target: './src/generated/api/endpoints.ts',
      schemas: './src/generated/models',
      client: 'react-query',
      httpClient: 'fetch',
      mode: 'single',
      clean: true,
      override: {
        fetch: {
          includeHttpResponseReturnType: false,
        },
        mutator: {
          path: './src/services/http/request.ts',
          name: 'request',
        },
        query: {
          signal: true,
        },
      },
    },
  },
})
