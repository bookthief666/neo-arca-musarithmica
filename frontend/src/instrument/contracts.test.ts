import { describe, expect, it } from 'vitest'
import { decodeHistoricalManifest, decodeHistoricalExecution } from './contracts'
import { manifestFixture, executionFixture } from '../test/fixtures'
describe('runtime v2 boundary', () => {
  it('accepts actual bridge manifest and kernel execution', () => {
    expect(decodeHistoricalManifest(manifestFixture)).toEqual(manifestFixture)
    expect(decodeHistoricalExecution(executionFixture)).toEqual(executionFixture)
  })
  it.each([null, [], {}, { format: 'neo-arca-mechanica-manifest/v1' }])('rejects stale/malformed %j', value => {
    expect(() => decodeHistoricalManifest(value)).toThrow()
  })
  it('rejects unknown fields, malformed values and missing voice events', () => {
    const extra = structuredClone(manifestFixture)
    Object.assign(extra.critical_edition_carrier.pitch_source.content, { octave: 4 })
    expect(() => decodeHistoricalManifest(extra)).toThrow()
    const wrong = structuredClone(manifestFixture)
    wrong.critical_edition_carrier.rhythm_source.content.relative_minim_units[0] = NaN
    expect(() => decodeHistoricalManifest(wrong)).toThrow()
    const missing = structuredClone(manifestFixture)
    missing.critical_edition_carrier.pitch_source.content.rows.altus.pop()
    expect(() => decodeHistoricalManifest(missing)).toThrow()
  })
  it('rejects stale executions and unknown nested event fields', () => {
    expect(() => decodeHistoricalExecution({ ...executionFixture, format: 'neo-arca-mechanica-execution/v1' })).toThrow()
    const wrong = structuredClone(executionFixture)
    Object.assign(wrong.fragment.events[0].voices.cantus, { midi: 60 })
    expect(() => decodeHistoricalExecution(wrong)).toThrow()
    const missing = structuredClone(executionFixture)
    missing.fragment.events.pop()
    expect(() => decodeHistoricalExecution(missing)).toThrow()
  })
})
