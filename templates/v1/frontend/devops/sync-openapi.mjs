import { mkdir, rename, rm, writeFile } from 'node:fs/promises'

const openapiUrl = process.env.OPENAPI_URL ?? 'http://localhost:8000/openapi.json'
const outputPath = 'openapi/api.json'
const temporaryPath = `${outputPath}.tmp`

try {
  const response = await fetch(openapiUrl, {
    signal: AbortSignal.timeout(15_000),
  })

  if (!response.ok) {
    throw new Error(
      `Failed to download OpenAPI: ${response.status} ${response.statusText}`,
    )
  }

  const document = await response.json()
  if (
    typeof document !== 'object' ||
    document === null ||
    typeof document.openapi !== 'string' ||
    typeof document.paths !== 'object' ||
    document.paths === null ||
    Array.isArray(document.paths)
  ) {
    throw new Error('The response is not a valid OpenAPI document')
  }

  await mkdir('openapi', { recursive: true })
  await writeFile(temporaryPath, `${JSON.stringify(document, null, 2)}\n`)
  await rename(temporaryPath, outputPath)

  console.log(`OpenAPI synced from ${openapiUrl} to ${outputPath}`)
} finally {
  await rm(temporaryPath, { force: true })
}
