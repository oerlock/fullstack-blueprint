import { MutationCache, QueryCache, QueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'
import { ApiError } from './error'

export const DEFAULT_STALE_TIME = 30_000
export const API_ERROR_TOAST_ID = 'api-service-error'

export function shouldRetryQuery(failureCount: number, error: unknown): boolean {
  if (failureCount >= 2 || !(error instanceof ApiError)) return false
  return error.status === undefined || error.status >= 500
}

export function notifyApiError(error: unknown): void {
  if (!(error instanceof ApiError)) return

  // 4xx 由业务自行处理，不弹全局提示
  if (error.status !== undefined && error.status < 500) return

  const isNetworkError = error.status === undefined
  toast.error(isNetworkError ? '网络异常' : '服务异常', {
    id: API_ERROR_TOAST_ID,
    description: isNetworkError
      ? '请求发送失败，请检查网络后重试'
      : error.message || '服务器开小差了，请稍后重试',
  })
}

export function createQueryClient(): QueryClient {
  return new QueryClient({
    queryCache: new QueryCache({ onError: notifyApiError }),
    mutationCache: new MutationCache({ onError: notifyApiError }),
    defaultOptions: {
      queries: {
        staleTime: DEFAULT_STALE_TIME,
        retry: shouldRetryQuery,
      },
      mutations: {
        retry: false,
      },
    },
  })
}

export const queryClient = createQueryClient()
