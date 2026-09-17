import type { InstrumentAffordance } from '../instrument/types'
import type { ArcaRealmId, GuidanceMode, RealmGuidance } from './types'

const HISTORICA_SCHOLIA = Object.freeze<Record<InstrumentAffordance, string>>({
  open_arca: 'Open the instrument.',
  focus_bank_i: 'The first bank bears the verified corpus.',
  open_cell_iv: 'Cell IV preserves the operative fragment.',
  retrieve_carrier: 'Lift the critical-edition carrier.',
  place_held_carrier: 'Seat the carrier upon the rule.',
  inspect_event: 'Inspect an event.',
  read_fragment: 'Read the selected fragment.',
  await_execution: 'The Arca is reading.',
  inspect_revelation: 'Four voices are disclosed.',
  recover: 'Restore the verified disposition.',
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
