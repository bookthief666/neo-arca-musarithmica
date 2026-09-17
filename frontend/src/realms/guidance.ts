import type { InstrumentAffordance } from '../instrument/types'
import type { ArcaRealmId, GuidanceMode, RealmGuidance } from './types'

const EVENT_READING = 'One event joins four degrees, the fixed Tone-II lookup, and one historical duration.'

const HISTORICA_SCHOLIA = Object.freeze<Record<InstrumentAffordance, string>>({
  open_arca: 'The cabinet carries a critical edition of one Pinax-IV computation.',
  focus_bank_i: 'Bank I contains the simple-style material used by this edition.',
  open_cell_iv: 'Cell IV holds the verified Pinax-IV extract.',
  retrieve_carrier: 'This H1 carrier joins separately verified pitch degrees and mensural identities.',
  place_held_carrier: 'The same carrier supplies four voice rows and a shared rhythm to the reading station.',
  inspect_event: EVENT_READING,
  read_fragment: `${EVENT_READING} LECTIO remains available as the six-event kernel record whenever you choose.`,
  await_execution: 'The historical kernel is checking the seated edition against the same source and Tone witness.',
  inspect_revelation: 'The folio preserves the six executed source-to-result events after parity validation.',
  recover: 'The carrier remains seated. Its source data and inspection position are preserved; retry when you choose.',
})

export function getRealmGuidance(
  realm: ArcaRealmId,
  affordance: InstrumentAffordance,
  mode: GuidanceMode,
): RealmGuidance | null {
  if (mode === 'quiet' || realm !== 'historica') return null
  return Object.freeze({
    affordance,
    text: HISTORICA_SCHOLIA[affordance],
  })
}
