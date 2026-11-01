export type RuntimeConfig = {
  APP_NAME?: string
  API_BASE_URL?: string
}

declare global {
  interface Window {
    __APP_CONFIG__?: RuntimeConfig
  }
}

const runtimeConfig = typeof window !== 'undefined' ? (window.__APP_CONFIG__ ?? {}) : {}

function firstDefined(...values: Array<string | undefined>): string | undefined {
  return values.find((value) => value !== undefined && value !== '')
}

/**
 * 应用配置。
 * 优先级：runtime-config.js（window.__APP_CONFIG__）> VITE_* 构建时变量 > 默认值。
 * 业务代码只从此对象读取，不要直接访问 import.meta.env 或 window.__APP_CONFIG__。
 */
export const config = {
  appName: firstDefined(
    runtimeConfig.APP_NAME,
    import.meta.env.VITE_APP_NAME,
  ) ?? '全栈模板',
  apiBaseUrl: firstDefined(
    runtimeConfig.API_BASE_URL,
    import.meta.env.VITE_API_BASE_URL,
  ) ?? '',
} as const
