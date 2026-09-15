import { describe, expect, it } from 'vitest'
import { resolveRenderer } from './renderer'

describe('M1.2 renderer selection', () => {
  it('makes the spatial instrument the default presentation', () => {
    expect(resolveRenderer('')).toBe('spatial')
    expect(resolveRenderer('?foo=bar')).toBe('spatial')
  })

  it('keeps the M1.1 renderer reachable as a rollback path', () => {
    expect(resolveRenderer('?renderer=legacy')).toBe('legacy')
  })

  it('treats any other value as the default rather than failing closed', () => {
    expect(resolveRenderer('?renderer=spatial')).toBe('spatial')
    expect(resolveRenderer('?renderer=nonsense')).toBe('spatial')
  })
})
