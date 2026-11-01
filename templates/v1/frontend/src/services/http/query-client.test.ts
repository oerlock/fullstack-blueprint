import { describe, expect, it, vi } from 'vitest'
import { ApiError } from './error'
import {
  createQueryClient,
  notifyApiError,
  shouldRetryQuery,
} from './query-client'

vi.mock('sonner', () => ({
  toast: { error: vi.fn() },
}))

import { toast } from 'sonner'

describe('shouldRetryQuery', () => {
  it('retries 5xx up to twice', () => {
    const error = new ApiError('boom', { status: 502 })
    expect(shouldRetryQuery(0, error)).toBe(true)
    expect(shouldRetryQuery(1, error)).toBe(true)
    expect(shouldRetryQuery(2, error)).toBe(false)
  })

  it('does not retry 4xx or unknown errors', () => {
    expect(shouldRetryQuery(0, new ApiError('bad', { status: 400 }))).toBe(false)
    expect(shouldRetryQuery(0, new Error('other'))).toBe(false)
  })
})

describe('notifyApiError', () => {
  it('notifies on network errors', () => {
    vi.mocked(toast.error).mockClear()
    notifyApiError(new ApiError('Network request failed'))
    expect(toast.error).toHaveBeenCalledOnce()
  })

  it('notifies on 5xx', () => {
    vi.mocked(toast.error).mockClear()
    notifyApiError(new ApiError('内部错误', { status: 500, code: 500001 }))
    expect(toast.error).toHaveBeenCalledOnce()
  })

  it('ignores 4xx and non-ApiError', () => {
    vi.mocked(toast.error).mockClear()
    notifyApiError(new ApiError('bad', { status: 400 }))
    notifyApiError(new Error('other'))
    expect(toast.error).not.toHaveBeenCalled()
  })
})

describe('createQueryClient', () => {
  it('applies stale time and no mutation retry', () => {
    const client = createQueryClient()
    expect(client.getDefaultOptions().queries?.staleTime).toBe(30_000)
    expect(client.getDefaultOptions().mutations?.retry).toBe(false)
  })
})
