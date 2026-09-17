import type { HistoricalReadingRequest } from './types'
import { decodeHistoricalExecution, decodeHistoricalManifest } from './contracts'

async function payload(response: Response): Promise<unknown> {
  const value: unknown = await response.json()
  if (!response.ok) {
    const message = value && typeof value === 'object' && 'message' in value && typeof value.message === 'string'
      ? value.message : 'The historical kernel rejected the reading.'
    throw new Error(message)
  }
  return value
}
export async function loadHistoricalManifest(signal?: AbortSignal) {
  return decodeHistoricalManifest(await payload(await fetch('/api/historica/manifest', { signal, headers: { Accept: 'application/json' } })))
}
export async function executeHistoricalReading(request: HistoricalReadingRequest, signal?: AbortSignal) {
  return decodeHistoricalExecution(await payload(await fetch('/api/historica/execute', {
    method: 'POST', signal, headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
    body: JSON.stringify(request),
  })))
}
