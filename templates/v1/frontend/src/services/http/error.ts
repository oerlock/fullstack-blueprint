export type ApiErrorOptions = {
  status?: number
  code?: number
  message?: string
  metadata?: unknown
  cause?: unknown
}

export class ApiError extends Error {
  status?: number
  code?: number
  metadata?: unknown

  constructor(message: string, options: ApiErrorOptions = {}) {
    super(message, { cause: options.cause })
    this.name = 'ApiError'
    this.status = options.status
    this.code = options.code
    this.metadata = options.metadata
  }
}
