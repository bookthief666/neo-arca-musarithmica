import { expect, it } from 'vitest'
import { getSourceReadingFrame, getExecutedReadingFrame, getReadingFrames, assertExecutionMatchesManifest } from './reading'
import { manifestFixture as manifest, executionFixture as execution } from '../test/fixtures'
import type { HistoricalExecution, HistoricalManifest, VoiceName } from './types'

it('derives exact first and sixth source frames without execution provenance',() => {
  expect(getSourceReadingFrame(manifest,0)).toEqual({
    authority:'source',position:0,eventNumber:1,duration:{glyph:'minim',relativeMinimUnits:1},
    voices:{cantus:{degree:5,pitchClass:'D'},altus:{degree:8,pitchClass:'G'},
      tenor:{degree:3,pitchClass:'Bb'},bassus:{degree:8,pitchClass:'G'}},
  })
  expect(getSourceReadingFrame(manifest,5)).toEqual({
    authority:'source',position:5,eventNumber:6,duration:{glyph:'semibreve',relativeMinimUnits:2},
    voices:{cantus:{degree:3,pitchClass:'Bb'},altus:{degree:7,pitchClass:'F#'},
      tenor:{degree:5,pitchClass:'D'},bassus:{degree:3,pitchClass:'Bb'}},
  })
  expect(getSourceReadingFrame(manifest,0)).not.toHaveProperty('provenance')
})
it.each([-1,6,0.5,NaN,Infinity])('fails closed for impossible position %s',position => {
  expect(() => getSourceReadingFrame(manifest,position)).toThrow(/position/)
  expect(() => getExecutedReadingFrame(manifest,execution,position)).toThrow(/position/)
})
it('uses exact M0.9 events after execution and leaves inputs untouched',() => {
  const before=JSON.stringify({manifest,execution})
  const frames=getReadingFrames(manifest,execution)
  expect(frames).toHaveLength(6)
  for(let i=0;i<6;i++) {
    const frame=getExecutedReadingFrame(manifest,execution,i)
    expect(frame.authority).toBe('execution')
    expect(frame.provenance).toBe(execution.fragment.events[i])
    expect(frame.voices.cantus.degree).toBe(execution.fragment.events[i].voices.cantus.degree)
    expect(frame.duration.relativeMinimUnits).toBe(execution.fragment.events[i].duration_minim_units)
  }
  expect(JSON.stringify({manifest,execution})).toBe(before)
  expect(getReadingFrames(manifest).every(f => f.authority==='source')).toBe(true)
})
const manifestMutations: Array<[string,(m:HistoricalManifest)=>void]> = [
  ...(['cantus','altus','tenor','bassus'] as VoiceName[]).map(voice => [
    voice+' length',(m:HistoricalManifest) => { m.critical_edition_carrier.pitch_source.content.rows[voice].pop() },
  ] as [string,(m:HistoricalManifest)=>void]),
  ['glyph length',m => {m.critical_edition_carrier.rhythm_source.content.glyphs.pop()}],
  ['normalization length',m => {m.critical_edition_carrier.rhythm_source.content.relative_minim_units.pop()}],
  ['missing Tone degree',m => {delete m.tone.degree_to_pitch_class['5']}],
  ['invalid degree',m => {m.critical_edition_carrier.pitch_source.content.rows.cantus[0]=9}],
  ['invalid normalization',m => {m.critical_edition_carrier.rhythm_source.content.relative_minim_units[0]=NaN}],
]
it.each(manifestMutations)('rejects source %s before any frame',(_,mutate) => {
  const m=structuredClone(manifest);mutate(m)
  expect(() => getSourceReadingFrame(m,0)).toThrow()
  expect(() => getExecutedReadingFrame(m,execution,0)).toThrow()
})
const resultMutations: Array<[string,(e:HistoricalExecution)=>void]> = [
  ['manifest identity',e => {e.reading.manifest_id='stale'}],
  ['content identity',e => {e.reading.content_digest='0'.repeat(64)}],
  ['carrier identity',e => {e.reading.carrier_instance.carrier_id='stale'}],
  ['edition identity',e => {e.reading.carrier_instance.edition_id='stale'}],
  ['six-event count',e => {e.fragment.events.pop()}],
  ['late event degree',e => {e.fragment.events[5].voices.bassus.degree=4}],
  ['pitch class',e => {e.fragment.events[0].voices.altus.pitch_class='D'}],
  ['duration ratio',e => {e.fragment.events[0].duration_minim_units=2}],
  ['duration identity',e => {e.fragment.events[0].duration_symbol='semibreve'}],
  ['total duration',e => {e.fragment.total_duration_minim_units=9}],
  ['offset',e => {e.fragment.events[4].offset_minim_units=3}],
  ['event order',e => {e.fragment.events.reverse()}],
  ['fixed witness',e => {e.reading.tone.witness='engraving';e.fragment.selection.tone_witness='engraving'}],
  ['tone number',e => {e.reading.tone.number=3;e.fragment.selection.tone=3}],
  ['selection',e => {e.fragment.selection.rperm=1}],
  ['source record',e => {e.fragment.provenance.components.pitch_permutation.record='other'}],
  ['source cell',e => {e.fragment.events[0].voices.cantus.provenance.vperm_cell='other'}],
  ['rhythm cell',e => {e.fragment.events[0].rhythm_provenance.cell='other'}],
]
it.each(resultMutations)('rejects %s even when inspecting another event',(_,mutate) => {
  const e=structuredClone(execution);mutate(e)
  expect(() => getExecutedReadingFrame(manifest,e,0)).toThrow()
  expect(() => assertExecutionMatchesManifest(manifest,e)).toThrow()
})
it('names stale content identity explicitly',() => {
  const e=structuredClone(execution);e.reading.content_digest='0'.repeat(64)
  expect(() => getExecutedReadingFrame(manifest,e,0)).toThrow(/content identity/)
})
