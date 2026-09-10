import type {
  AlignmentRequest,
  HistoricalManifest,
  InstrumentAction,
  InstrumentPhase,
  InstrumentState,
} from './types'

export const MAX_VERTICAL_OFFSET = 9

export function createInitialState(reducedMotion = false): InstrumentState {
  return {
    phase: 'dormant',
    focusedBank: null,
    focusedCell: null,
    rods: [],
    heldRodId: null,
    toneEngaged: false,
    execution: null,
    error: null,
    provenanceOpen: false,
    reducedMotion,
  }
}

function alignmentPhase(state: InstrumentState, manifest?: HistoricalManifest): InstrumentPhase {
  if (!manifest || state.rods.some((rod) => rod.location === 'hand')) return 'rod_retrieval'
  const placed = state.rods.filter((rod) => rod.location === 'workspace')
  const required = new Set(manifest.required_template_ids)
  const allPlaced = placed.length === required.size && placed.every((rod) => required.has(rod.template_id))
  if (!allPlaced) return 'aligning'
  const ready = placed.every((rod) => rod.vertical_offset === 0)
  if (!ready) return 'aligning'
  return state.toneEngaged ? 'tonal_resolution' : 'historical_alignment_ready'
}

export function instrumentReducer(
  state: InstrumentState,
  action: InstrumentAction,
  manifest?: HistoricalManifest,
): InstrumentState {
  switch (action.type) {
    case 'OPEN_ARCA':
      return { ...state, phase: 'open', error: null }
    case 'CLOSE_ARCA':
      return createInitialState(state.reducedMotion)
    case 'FOCUS_BANK':
      return { ...state, focusedBank: action.bank, phase: 'bank_focus', error: null }
    case 'FOCUS_CELL':
      if (state.focusedBank !== 1 || action.cell !== 4) return state
      return { ...state, focusedCell: action.cell, phase: 'cell_focus', error: null }
    case 'RETRIEVE_ROD': {
      if (state.focusedCell !== 4 || state.rods.some((rod) => rod.template_id === action.template.template_id)) {
        return state
      }
      const rod = {
        instance_id: `rod-${action.template.template_id}`,
        template_id: action.template.template_id,
        source_column_id: action.template.source_column_id,
        copy_index: action.template.copy_index,
        location: 'hand' as const,
        vertical_offset: Math.min(action.template.copy_index + 1, MAX_VERTICAL_OFFSET),
        order: state.rods.length,
      }
      return {
        ...state,
        rods: [...state.rods, rod],
        heldRodId: rod.instance_id,
        phase: 'rod_retrieval',
        execution: null,
        toneEngaged: false,
      }
    }
    case 'PLACE_HELD_ROD': {
      if (!state.heldRodId) return state
      const rods = state.rods.map((rod) =>
        rod.instance_id === state.heldRodId ? { ...rod, location: 'workspace' as const } : rod,
      )
      const next = { ...state, rods, heldRodId: null, execution: null }
      return { ...next, phase: alignmentPhase(next, manifest) }
    }
    case 'MOVE_ROD': {
      const offset = Math.max(0, Math.min(MAX_VERTICAL_OFFSET, Math.round(action.offset)))
      const rods = state.rods.map((rod) =>
        rod.instance_id === action.instanceId && rod.location === 'workspace'
          ? { ...rod, vertical_offset: offset }
          : rod,
      )
      const next = { ...state, rods, execution: null, error: null, toneEngaged: false }
      return { ...next, phase: alignmentPhase(next, manifest) }
    }
    case 'ENGAGE_TONE': {
      if (alignmentPhase({ ...state, toneEngaged: false }, manifest) !== 'historical_alignment_ready') return state
      return { ...state, toneEngaged: true, phase: 'tonal_resolution', error: null }
    }
    case 'EXECUTE':
      if (!isExecutionReady(state, manifest)) return state
      return { ...state, phase: 'executing', error: null }
    case 'EXECUTION_SUCCESS':
      return { ...state, execution: action.execution, phase: 'revealed', error: null }
    case 'EXECUTION_ERROR':
      return { ...state, execution: null, phase: 'error', error: action.message }
    case 'TOGGLE_PROVENANCE':
      return { ...state, provenanceOpen: !state.provenanceOpen }
    case 'SET_REDUCED_MOTION':
      return { ...state, reducedMotion: action.value }
  }
}

export function isAlignmentReady(state: InstrumentState, manifest?: HistoricalManifest): boolean {
  return alignmentPhase({ ...state, toneEngaged: false }, manifest) === 'historical_alignment_ready'
}

export function isExecutionReady(state: InstrumentState, manifest?: HistoricalManifest): boolean {
  return Boolean(manifest && state.toneEngaged && isAlignmentReady(state, manifest))
}

export function createAlignmentRequest(
  state: InstrumentState,
  manifest: HistoricalManifest,
): AlignmentRequest {
  if (!isExecutionReady(state, manifest)) throw new Error('The physical alignment is not ready.')
  return {
    format: 'neo-arca-mechanica-alignment/v1',
    read_band: manifest.canonical_read_band,
    tone: { number: manifest.tone.number, engaged: state.toneEngaged },
    rod_instances: state.rods
      .filter((rod) => rod.location === 'workspace')
      .map((rod) => ({ ...rod })),
  }
}
