import type { HistoricalManifest, HistoricalReadingRequest, InstrumentAction, InstrumentAffordance, InstrumentState, InstrumentView } from './types'

export function createInitialState(reducedMotion = false): InstrumentState {
  return { phase: 'dormant', focusedBank: null, focusedCell: null, carriers: [],
    heldCarrierId: null, readingPosition: 0, execution: null, error: null,
    provenanceOpen: false, reducedMotion }
}

export function isReadingReady(state: InstrumentState, manifest?: HistoricalManifest): boolean {
  if (!manifest || !['carrier_seated', 'error'].includes(state.phase) ||
      state.carriers.length !== 1 || state.heldCarrierId !== null) return false
  const c = state.carriers[0], edition = manifest.critical_edition_carrier
  return c.location === 'workspace' && Boolean(c.instance_id.trim()) &&
    c.carrier_id === edition.carrier_id && c.edition_id === edition.edition_id
}

export function createReadingRequest(state: InstrumentState, manifest: HistoricalManifest): HistoricalReadingRequest {
  if (!isReadingReady(state, manifest)) throw new Error('Seat the critical-edition carrier before reading.')
  return { format: 'neo-arca-mechanica-reading/v2', manifest_id: manifest.manifest_id,
    content_digest: manifest.content_digest, carrier_instance: { ...state.carriers[0], location: 'workspace' } }
}

export function instrumentReducer(state: InstrumentState, action: InstrumentAction, manifest?: HistoricalManifest): InstrumentState {
  switch (action.type) {
    case 'OPEN_ARCA': return state.phase === 'dormant' ? { ...state, phase: 'open' } : state
    case 'CLOSE_ARCA': return createInitialState(state.reducedMotion)
    case 'FOCUS_BANK':
      return state.phase === 'open' && action.bank === 1
        ? { ...state, phase: 'bank_focus', focusedBank: 1 } : state
    case 'FOCUS_CELL':
      return state.phase === 'bank_focus' && action.cell === manifest?.cell.pinax
        ? { ...state, phase: 'cell_focus', focusedCell: action.cell } : state
    case 'RETRIEVE_CARRIER': {
      if (!manifest || state.phase !== 'cell_focus' || state.carriers.length || state.heldCarrierId) return state
      const { carrier_id, edition_id } = manifest.critical_edition_carrier
      const instance_id = 'carrier-pinax04-fragment-1'
      return { ...state, phase: 'carrier_held', heldCarrierId: instance_id,
        carriers: [{ instance_id, carrier_id, edition_id, location: 'hand' }] }
    }
    case 'PLACE_HELD_CARRIER':
      if (state.phase !== 'carrier_held' || state.carriers.length !== 1 ||
          state.carriers[0].instance_id !== state.heldCarrierId || state.carriers[0].location !== 'hand') return state
      return { ...state, phase: 'carrier_seated', heldCarrierId: null,
        carriers: [{ ...state.carriers[0], location: 'workspace' }] }
    case 'SET_READING_POSITION':
      if (!Number.isFinite(action.position) || state.carriers[0]?.location !== 'workspace') return state
      return { ...state, readingPosition: Math.max(0, Math.min(5, Math.round(action.position))) }
    case 'EXECUTE':
      return isReadingReady(state, manifest) ? { ...state, phase: 'executing', error: null } : state
    case 'EXECUTION_SUCCESS': {
      if (state.phase !== 'executing' || !manifest) return state
      const r = action.execution.reading, c = state.carriers[0]
      if (!c || r.manifest_id !== manifest.manifest_id || r.content_digest !== manifest.content_digest ||
          r.carrier_instance.instance_id !== c.instance_id || r.carrier_instance.carrier_id !== c.carrier_id ||
          r.carrier_instance.edition_id !== c.edition_id) {
        return { ...state, phase: 'error', error: 'The returned reading does not match this edition.' }
      }
      return { ...state, phase: 'revealed', execution: action.execution, error: null }
    }
    case 'EXECUTION_ERROR':
      return state.phase === 'executing' ? { ...state, phase: 'error', error: action.message } : state
    case 'RETURN_TO_WORKING':
      return ['revealed', 'error'].includes(state.phase)
        ? { ...state, phase: 'carrier_seated', execution: null, error: null } : state
    case 'TOGGLE_PROVENANCE': return { ...state, provenanceOpen: !state.provenanceOpen }
    case 'SET_REDUCED_MOTION': return { ...state, reducedMotion: action.value }
  }
}
export function deriveInstrumentView(state: InstrumentState): InstrumentView {
  if (state.phase === 'dormant') return 'arca'
  if (state.phase === 'revealed') return 'revelation'
  if (state.carriers.length) return 'working'
  if (state.focusedCell) return 'cell'
  return 'cabinet'
}
export function getNextAffordance(state: InstrumentState, manifest?: HistoricalManifest): InstrumentAffordance {
  switch (state.phase) {
    case 'dormant': return 'open_arca'
    case 'open': return 'focus_bank_i'
    case 'bank_focus': return 'open_cell_iv'
    case 'cell_focus': return 'retrieve_carrier'
    case 'carrier_held': return 'place_held_carrier'
    case 'carrier_seated': return isReadingReady(state, manifest) ? 'read_fragment' : 'inspect_event'
    case 'executing': return 'await_execution'
    case 'revealed': return 'inspect_revelation'
    case 'error': return 'recover'
  }
}
