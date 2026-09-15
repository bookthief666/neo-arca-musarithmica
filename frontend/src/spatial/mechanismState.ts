import type { InstrumentPhase } from '../instrument/types'

/**
 * WHAT THE TWO FINAL MECHANISMS ARE DOING.
 *
 * Tone II and LECTIO are persistent hardware. They are present from the moment
 * the instrument is open and they change state; they are not conjured at the
 * moment they become useful. A control that appears from nowhere cannot be the
 * thing that taught you the step was coming, and M1.2 created its reading
 * lever only once execution was already possible — so the last act of the
 * operation was performed on a control the reader had never seen before.
 *
 * Both mappings are pure and take canonical readiness. Neither decides
 * anything: the reducer has already decided, and these say how it looks.
 */
export type MechanismState = 'dormant' | 'available' | 'engaged' | 'busy' | 'fault'

export function toneMechanismState(alignmentReady: boolean, toneEngaged: boolean): MechanismState {
  if (toneEngaged) return 'engaged'
  return alignmentReady ? 'available' : 'dormant'
}

export function lectioMechanismState(
  executionReady: boolean,
  phase: InstrumentPhase,
  error: string | null,
): MechanismState {
  // A failed reading that left the disposition intact is a RETRY, not a reset:
  // the rods, the bands and the Tone are all still where the reader put them.
  if (error && executionReady) return 'fault'
  if (phase === 'executing') return 'busy'
  return executionReady ? 'available' : 'dormant'
}
