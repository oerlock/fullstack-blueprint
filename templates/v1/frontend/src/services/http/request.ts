import { config } from '../../config'
import { ApiError } from './error'

export function buildApiUrl(path: string): string {
  if (/^https?:\/\//i.test(path)) return path

  const baseUrl = config.apiBaseUrl.replace(/\/+$/, '')
  const relativePath = path.replace(/^\/+/, '')
  return baseUrl ? `${baseUrl}/${relativePath}` : `/${relativePath}`
}

function isAbortError(error: unknown): boolean {
  return (
    typeof error === 'object' &&
    error !== null &&
    'name' in error &&
    error.name === 'AbortError'
  )
}

type ErrorBody = {
  code?: unknown
  message?: unknown
  metadata?: unknown
}

async function parseError(response: Response): Promise<ApiError> {
  let body: ErrorBody | undefined

  try {
    body = (await response.json()) as ErrorBody
  } catch {
    body = undefined
  }

  const message =
    typeof body?.message === 'string'
      ? body.message
      : response.statusText || `Request failed with status ${response.status}`

  return new ApiError(message, {
    status: response.status,
    code: typeof body?.code === 'number' ? body.code : undefined,
    metadata: body?.metadata,
  })
}

async function parseSuccess<T>(response: Response): Promise<T> {
  if (response.status === 204 || response.status === 205) {
    return undefined as T
  }

  const contentType = response.headers.get('content-type')?.toLowerCase() ?? ''

  try {
    if (contentType.includes('application/json') || contentType.includes('+json')) {
      return (await response.json()) as T
    }

    if (contentType.startsWith('text/')) {
      return (await response.text()) as T
    }

    return (await response.blob()) as T
  } catch (error) {
    throw new ApiError('Failed to parse API response', {
      status: response.status,
      cause: error,
    })
  }
}

export async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const headers = new Headers(options.headers)

  let response: Response
  try {
    response = await fetch(buildApiUrl(path), {
      ...options,
      headers,
    })
  } catch (error) {
    if (isAbortError(error)) throw error

    throw new ApiError('Network request failed', { cause: error })
  }

  if (!response.ok) {
    throw await parseError(response)
  }

  return parseSuccess<T>(response)
}

export type ErrorType<_ErrorData> = ApiError
export type BodyType<BodyData> = BodyData
