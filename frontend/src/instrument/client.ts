import type { AlignmentRequest, HistoricalExecution, HistoricalManifest } from './types'

async function decode<T>(response: Response): Promise<T> {
  const payload = await response.json() as T & { message?: string }
  if (!response.ok) throw new Error(payload.message ?? 'The historical kernel rejected the operation.')
  return payload
}

export async function loadHistoricalManifest(signal?: AbortSignal): Promise<HistoricalManifest> {
  const response = await fetch('/api/historica/manifest', { signal, headers: { Accept: 'application/json' } })
  return decode<HistoricalManifest>(response)
}

export async function executeHistoricalAlignment(request: AlignmentRequest): Promise<HistoricalExecution> {
  const response = await fetch('/api/historica/execute', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
    body: JSON.stringify(request),
  })
  return decode<HistoricalExecution>(response)
}
