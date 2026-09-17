import type { CriticalEditionCarrier, VoiceName } from '../instrument/types'

/** Shared inscriptions for the semantic face and the canvas texture; no musical computation. */
export function carrierInscription(carrier: CriticalEditionCarrier) {
  const voices: VoiceName[] = ['cantus','altus','tenor','bassus']
  return {
    title: 'EXCERPTVM CRITICVM · PINAX IV · H1 CARRIER',
    pitch: 'VOCES · VPERM 01 · H0 SOURCE',
    rows: voices.map(voice => voice[0].toUpperCase()+' '+carrier.pitch_source.content.rows[voice].join(' ')),
    rhythm: 'NOTAE TEMPORIS · RPERM 03 · H0 SOURCE',
    glyphs: carrier.rhythm_source.content.glyphs.join(' '),
    normalization: 'DERIVED RELATIVE-MINIM NORMALIZATION · '+carrier.rhythm_source.content.relative_minim_units.join(' '),
    pairing: 'EDITORIAL PAIRING · H1',
  }
}
