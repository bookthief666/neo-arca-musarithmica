import type { InstrumentAffordance } from '../instrument/types'
import type { ArcaRealmId, GuidanceMode, RealmGuidance } from './types'

/**
 * The Scholium is the THIRD teacher, after geometry and restrained emphasis.
 * It never substitutes for a missing affordance, but when it speaks it must
 * name the part and the act.
 *
 * The M1.2 lines were accurate and taught nothing. "Take a virga" and "Bring
 * the first bands into concord" assume the reader already knows what a virga
 * is, where it is kept, what a band is and which one matters — which is
 * precisely what a first-time reader does not know.
 */
const HISTORICA_SCHOLIA = Object.freeze<Record<InstrumentAffordance, string>>({
  open_arca: 'Open the instrument.',
  focus_bank_i: 'Open Bank I.',
  open_cell_iv: 'Open Cell IV; the verified virgae are stored within.',
  deploy_rods: 'Lift a virga from its socket.',
  place_held_rod: 'Seat the lifted virga in the illuminated channel.',
  align_rods: 'Slide each virga until band I lies beneath the reader.',
  engage_tone_ii: 'The rule is concordant. Engage Tone II.',
  read_transverse: 'Tone II is set. Operate LECTIO.',
  await_execution: 'The Arca is reading.',
  inspect_revelation: 'Four voices are disclosed.',
  recover: 'The disposition is preserved; restore the reading.',
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
