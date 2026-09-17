import type { InstrumentAffordance } from '../instrument/types'
import type { ArcaRealmId, GuidanceMode, RealmGuidance } from './types'

const HISTORICA_SCHOLIA = Object.freeze<Record<InstrumentAffordance, string>>({
  open_arca: 'The cabinet carries a critical edition of one Pinax-IV computation.',
  focus_bank_i: 'Bank I contains the simple-style material used by this edition.',
  open_cell_iv: 'Cell IV holds the verified Pinax-IV extract.',
  retrieve_carrier: 'This H1 carrier joins separately verified pitch degrees and mensural identities.',
  place_held_carrier: 'The same carrier supplies four voice rows and a shared rhythm to the reading station.',
  inspect_event: 'Each event combines four scale degrees with one mensural duration.',
  read_fragment: 'LECTIO consolidates six events using the fixed Tone-II witness map.',
  await_execution: 'The historical kernel resolves the seated edition.',
  inspect_revelation: 'The folio preserves the source-to-result trace.',
  recover: 'The carrier remains seated. Retry the reading; its source data and inspection position are preserved.',
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
