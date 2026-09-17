import { decodeHistoricalExecution, decodeHistoricalManifest } from './contracts'
import type { HistoricalEvent, HistoricalExecution, HistoricalManifest, VoiceName } from './types'

const VOICES: VoiceName[] = ['cantus', 'altus', 'tenor', 'bassus']
export interface ReadingFrame {
  position: number
  eventNumber: number
  duration: { glyph: string; relativeMinimUnits: number }
  voices: Record<VoiceName, { degree: number; pitchClass: string }>
}
export type SourceReadingFrame = ReadingFrame & { authority: 'source' }
export type ExecutedReadingFrame = ReadingFrame & { authority: 'execution'; provenance: HistoricalEvent }

function requireMatch(condition: boolean, message: string): asserts condition {
  if (!condition) throw new Error('Historical reading rejected: ' + message)
}
function assertEventPosition(position: number) {
  requireMatch(Number.isInteger(position) && position >= 0 && position < 6, 'impossible event position')
}

/** Display lookup only: no register, musical repair, or new musical result. */
function sourceFrame(manifest: HistoricalManifest, position: number): SourceReadingFrame {
  const carrier = manifest.critical_edition_carrier
  const rhythm = carrier.rhythm_source.content
  const voices = Object.fromEntries(VOICES.map(voice => {
    const degree = carrier.pitch_source.content.rows[voice][position]
    const pitchClass = manifest.tone.degree_to_pitch_class[String(degree)]
    requireMatch(typeof pitchClass === 'string' && pitchClass.length > 0, 'missing Tone degree')
    return [voice, { degree, pitchClass }]
  })) as ReadingFrame['voices']
  return { authority: 'source', position, eventNumber: position + 1,
    duration: { glyph: rhythm.glyphs[position], relativeMinimUnits: rhythm.relative_minim_units[position] }, voices }
}

export function getSourceReadingFrame(manifest: HistoricalManifest, position: number): SourceReadingFrame {
  assertEventPosition(position)
  decodeHistoricalManifest(manifest) // All four rows and both rhythm arrays must have six valid entries.
  return sourceFrame(manifest, position)
}

/** Validate the whole result before allowing even one event to carry its provenance. */
export function assertExecutionMatchesManifest(manifest: HistoricalManifest, execution: HistoricalExecution): void {
  decodeHistoricalManifest(manifest)
  decodeHistoricalExecution(execution)
  const carrier = manifest.critical_edition_carrier
  const reading = execution.reading
  requireMatch(reading.manifest_id === manifest.manifest_id, 'manifest identity')
  requireMatch(reading.content_digest === manifest.content_digest, 'content identity')
  requireMatch(reading.carrier_instance.carrier_id === carrier.carrier_id, 'carrier identity')
  requireMatch(reading.carrier_instance.edition_id === carrier.edition_id, 'edition identity')
  requireMatch(reading.tone.number === manifest.tone.number && reading.tone.witness === manifest.tone.witness, 'fixed Tone witness identity')

  const fragment = execution.fragment, selected = fragment.selection
  requireMatch(selected.syntagma === manifest.cell.syntagma && selected.pinax === manifest.cell.pinax &&
    selected.tone === manifest.tone.number && selected.tone_name === manifest.tone.name &&
    selected.system === manifest.tone.system && selected.tone_witness === manifest.tone.witness, 'selection identity')
  // These strings identify existing verified source records, never synthesize musical content.
  const pitchId = 'S'+selected.syntagma+'.P'+selected.pinax+'.STROPHA'+selected.stropha+'.VPERM'+String(selected.vperm).padStart(2,'0')
  const rhythmId = 'S'+selected.syntagma+'.P'+selected.pinax+'.NOTAE_TEMPORIS.DUPLE.RPERM'+String(selected.rperm).padStart(2,'0')
  requireMatch(pitchId === carrier.pitch_source.source_column_id && rhythmId === carrier.rhythm_source.source_column_id, 'source selection identity')
  const components = fragment.provenance.components
  requireMatch(components.pitch_permutation.record === carrier.pitch_source.immutable_record &&
    components.rhythm.record === carrier.rhythm_source.immutable_record &&
    components.tone_lookup.record === manifest.tone.record, 'source record identity')
  const witnesses = new Set(fragment.provenance.witnesses.map(w => w.id))
  requireMatch(witnesses.size === fragment.provenance.witnesses.length &&
    Object.values(components).every(c => c.witness_ids.length > 0 && c.witness_ids.every(id => witnesses.has(id))), 'witness envelope')

  let offset = 0
  for (let position = 0; position < 6; position++) {
    const source = sourceFrame(manifest, position), event = fragment.events[position]
    requireMatch(event.index === source.eventNumber && event.offset_minim_units === offset, 'event order or offset parity')
    requireMatch(event.duration_symbol === source.duration.glyph &&
      event.duration_minim_units === source.duration.relativeMinimUnits, 'duration parity')
    requireMatch(event.rhythm_provenance.cell === carrier.rhythm_source.provenance_paths[position], 'rhythm cell provenance')
    for (const voice of VOICES) {
      requireMatch(event.voices[voice].degree === source.voices[voice].degree, 'degree parity')
      requireMatch(event.voices[voice].pitch_class === source.voices[voice].pitchClass, 'pitch-class parity')
      const path = pitchId+'.'+voice.toUpperCase()+'.N'+String(position+1).padStart(2,'0')
      requireMatch(carrier.pitch_source.provenance_paths.includes(path) &&
        event.voices[voice].provenance.vperm_cell === path, 'pitch cell provenance')
    }
    offset += source.duration.relativeMinimUnits
  }
  requireMatch(fragment.total_duration_minim_units === offset, 'total duration parity')
}

function executedFrame(execution: HistoricalExecution, position: number): ExecutedReadingFrame {
  const event = execution.fragment.events[position]
  // Values now come from M0.9 itself, not a recomputed substitute.
  return {
    authority: 'execution', position, eventNumber: event.index, provenance: event,
    duration: { glyph: event.duration_symbol, relativeMinimUnits: event.duration_minim_units },
    voices: Object.fromEntries(VOICES.map(voice => [voice, {
      degree: event.voices[voice].degree, pitchClass: event.voices[voice].pitch_class,
    }])) as ReadingFrame['voices'],
  }
}

export function getExecutedReadingFrame(manifest: HistoricalManifest, execution: HistoricalExecution, position: number): ExecutedReadingFrame {
  assertEventPosition(position)
  assertExecutionMatchesManifest(manifest, execution)
  return executedFrame(execution, position)
}

export function getReadingFrames(manifest: HistoricalManifest, execution?: HistoricalExecution | null): Array<SourceReadingFrame | ExecutedReadingFrame> {
  if (execution) {
    assertExecutionMatchesManifest(manifest, execution)
    return Array.from({ length: 6 }, (_, position) => executedFrame(execution, position))
  }
  decodeHistoricalManifest(manifest)
  return Array.from({ length: 6 }, (_, position) => sourceFrame(manifest, position))
}
