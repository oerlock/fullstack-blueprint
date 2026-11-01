import { afterEach, describe, expect, test, vi } from 'vitest'
import type { RuntimeConfig } from './index'

async function loadConfig(runtimeConfig?: RuntimeConfig) {
  window.__APP_CONFIG__ = runtimeConfig
  vi.resetModules()
  return (await import('./index')).config
}

afterEach(() => {
  window.__APP_CONFIG__ = undefined
  vi.unstubAllEnvs()
  vi.resetModules()
})

describe('配置优先级', () => {
  test('runtime 配置覆盖构建时 VITE_ 变量', async () => {
    vi.stubEnv('VITE_APP_NAME', 'build-time')

    const config = await loadConfig({ APP_NAME: 'runtime' })

    expect(config.appName).toBe('runtime')
  })

  test('runtime 未配置时回退到构建时 VITE_ 变量', async () => {
    vi.stubEnv('VITE_APP_NAME', 'build-time')

    const config = await loadConfig()

    expect(config.appName).toBe('build-time')
  })

  test('都没有配置时使用代码默认值', async () => {
    vi.stubEnv('VITE_APP_NAME', '')

    const config = await loadConfig()

    expect(config.appName).toBe('全栈模板')
  })

  test('apiBaseUrl 默认为空字符串', async () => {
    vi.stubEnv('VITE_API_BASE_URL', '')

    const config = await loadConfig()

    expect(config.apiBaseUrl).toBe('')
  })
})
