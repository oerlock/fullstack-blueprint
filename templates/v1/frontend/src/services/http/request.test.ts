import { afterEach, describe, expect, it, vi } from 'vitest'
import { ApiError } from './error'
import { buildApiUrl, request } from './request'

vi.mock('../config', () => ({
  config: { apiBaseUrl: '' },
}))

import { config } from '../../config'

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'content-type': 'application/json' },
  })
}

function stubFetch(response: Response | Error): ReturnType<typeof vi.fn> {
  const fn = vi.fn(async () => {
    if (response instanceof Error) throw response
    return response
  })
  vi.stubGlobal('fetch', fn)
  return fn
}

afterEach(() => {
  vi.unstubAllGlobals()
})

describe('buildApiUrl', () => {
  it('joins base url and path', () => {
    (config as { apiBaseUrl: string }).apiBaseUrl = 'http://api.example.com/v1'
    expect(buildApiUrl('/api/health')).toBe('http://api.example.com/v1/api/health')
  })

  it('keeps absolute urls untouched', () => {
    expect(buildApiUrl('https://other.example.com/api')).toBe(
      'https://other.example.com/api',
    )
  })

  it('uses relative path when base url is empty', () => {
    (config as { apiBaseUrl: string }).apiBaseUrl = ''
    expect(buildApiUrl('/api/health')).toBe('/api/health')
  })
})

describe('request', () => {
  it('returns parsed json body', async () => {
    stubFetch(jsonResponse({ status: 'ok' }))
    await expect(request('/api/health')).resolves.toEqual({ status: 'ok' })
  })

  it('throws ApiError with backend error body fields', async () => {
    stubFetch(
      jsonResponse({ code: 422001, message: '数据校验失败', metadata: {} }, 422),
    )
    const error = await request('/api/health').catch((e: unknown) => e)
    expect(error).toBeInstanceOf(ApiError)
    expect((error as ApiError).status).toBe(422)
    expect((error as ApiError).code).toBe(422001)
    expect((error as ApiError).message).toBe('数据校验失败')
  })

  it('wraps network failures', async () => {
    stubFetch(new Error('offline'))
    const error = await request('/api/health').catch((e: unknown) => e)
    expect(error).toBeInstanceOf(ApiError)
    expect((error as ApiError).status).toBeUndefined()
  })

  it('rethrows AbortError untouched', async () => {
    const abortError = new DOMException('aborted', 'AbortError')
    vi.stubGlobal('fetch', vi.fn(async () => { throw abortError }))
    await expect(request('/api/health')).rejects.toBe(abortError)
  })

  it('returns undefined for 204', async () => {
    stubFetch(new Response(null, { status: 204 }))
    await expect(request('/api/health')).resolves.toBeUndefined()
  })
})
