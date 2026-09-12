import type { InstrumentAffordance } from '../instrument/types'
import type { ArcaRealmId, GuidanceMode, RealmGuidance } from './types'

const HISTORICA_SCHOLIA = Object.freeze<Record<InstrumentAffordance, string>>({
  open_arca: 'Open the instrument.',
  focus_bank_i: 'The first bank bears the verified corpus.',
  open_cell_iv: 'Cell IV preserves the operative fragment.',
  deploy_rods: 'Take a virga.',
  place_held_rod: 'Seat the carrier upon the rule.',
  align_rods: 'Bring the first bands into concord.',
  engage_tone_ii: 'Consult the Tone.',
  read_transverse: 'Read across the aligned band.',
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
