import type {
  ColumnRodInstance, HistoricalManifest, InstrumentState,
} from '../instrument/types'

/**
 * PRESENTATION READS OF CANONICAL STATE.
 *
 * Every function here is pure and takes the instrument's own state. None of
 * them decides anything about the instrument: they answer questions the scene
 * needs in order to draw, and the answers are already implied by the reducer.
 *
 * This is the whole reason M1.2.1 needs no second state machine. "Is a carrier
 * in the hand", "which channel is it going to", "should the drawer be out" and
 * "what is in each channel" are all facts about state.rods and state.heldRodId.
 */

/** The carrier currently in the hand, if any. */
export function heldRod(state: InstrumentState): ColumnRodInstance | null {
  if (!state.heldRodId) return null
  return state.rods.find((rod) => rod.instance_id === state.heldRodId) ?? null
}

/**
 * The one channel that should wake while a carrier is held.
 *
 * A virga belongs in the channel matching its position in the manifest, so
 * there is never a choice to offer and never a wrong place to put it. Exactly
 * one receiver lights, which is what makes the destination readable without
 * any instruction.
 */
export function targetLane(
  manifest: HistoricalManifest,
  state: InstrumentState,
): -1 | 0 | 1 | null {
  const held = heldRod(state)
  if (!held) return null
  const index = manifest.rod_templates.findIndex(
    (template) => template.template_id === held.template_id,
  )
  return index >= 0 && index < 3 ? ((index - 1) as -1 | 0 | 1) : null
}

/**
 * Whether the drawer should be out.
 *
 * It opens as soon as a carrier is LIFTED, not once one has landed, so the
 * reader sees where the thing in their hand is going before they commit to
 * putting it there. It stays out thereafter: nobody should have to reopen the
 * drawer they are working at.
 */
export function shouldExtendCarriage(state: InstrumentState): boolean {
  return Boolean(state.heldRodId) || state.rods.some((rod) => rod.location === 'workspace')
}

/** The canonical band presented in each channel, or null where none is seated. */
export function workspaceOffsets(
  manifest: HistoricalManifest,
  state: InstrumentState,
): [number | null, number | null, number | null] {
  return manifest.rod_templates.slice(0, 3).map((template) => {
    const rod = state.rods.find(
      (candidate) => candidate.template_id === template.template_id
        && candidate.location === 'workspace',
    )
    return rod ? rod.vertical_offset : null
  }) as [number | null, number | null, number | null]
}
