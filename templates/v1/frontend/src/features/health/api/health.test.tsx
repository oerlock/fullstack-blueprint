import { describe, expect, it } from 'vitest'
import { QueryClientProvider } from '@tanstack/react-query'
import { renderHook, waitFor } from '@testing-library/react'
import type { ReactNode } from 'react'
import { http, HttpResponse } from 'msw'
import { server } from '../../../mocks/server'
import { createQueryClient } from '../../../services/http/query-client'
import { ApiError } from '../../../services/http/error'
import { useHealthApiHealthGet } from './health'

function createWrapper() {
  const queryClient = createQueryClient()
  queryClient.clear()
  const wrapper = ({ children }: { children: ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  )
  return wrapper
}

describe('useHealthApiHealthGet', () => {
  it('fetches health status', async () => {
    const { result } = renderHook(() => useHealthApiHealthGet(), {
      wrapper: createWrapper(),
    })

    await waitFor(() => expect(result.current.isSuccess).toBe(true))
    expect(result.current.data).toEqual({ status: 'ok', version: '0.1.0' })
  })

  it('surfaces ApiError on failure', async () => {
    server.use(
      http.get('/api/health', () =>
        HttpResponse.json({ message: '内部错误' }, { status: 500 }),
      ),
    )

    const { result } = renderHook(() => useHealthApiHealthGet(), {
      wrapper: createWrapper(),
    })

    // 5xx 会按 query-client 配置自动重试，需等待重试耗尽
    await waitFor(() => expect(result.current.isError).toBe(true), {
      timeout: 6000,
    })
    expect(result.current.error).toBeInstanceOf(ApiError)
    expect((result.current.error as ApiError).status).toBe(500)
  })
})
