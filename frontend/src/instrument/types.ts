export type InstrumentPhase =
  | 'dormant'
  | 'open'
  | 'bank_focus'
  | 'cell_focus'
  | 'rod_retrieval'
  | 'aligning'
  | 'historical_alignment_ready'
  | 'tonal_resolution'
  | 'executing'
  | 'revealed'
  | 'error'

export type RodLocation = 'cell' | 'hand' | 'workspace'

export type VoiceName = 'cantus' | 'altus' | 'tenor' | 'bassus'

export interface PitchBandContent {
  rows: Record<VoiceName, number[]>
}

export interface RhythmBandContent {
  glyphs: string[]
  relative_minim_units: number[]
}

export interface HistoricalBand {
  index: number
  status: 'verified' | 'untranscribed'
  classification: 'H0' | 'UNKNOWN'
  label: string
  content: PitchBandContent | RhythmBandContent | null
  provenance_paths?: string[]
}

export interface HistoricalSourceColumn {
  id: string
  kind: 'pitch' | 'rhythm'
  label: string
  bands: HistoricalBand[]
  record: string
  provenance_class: string
}

export interface RodTemplate {
  template_id: string
  source_column_id: string
  copy_index: number
  label: string
}

export interface HistoricalManifest {
  format: 'neo-arca-mechanica-manifest/v1'
  title: string
  cell: {
    syntagma: number
    bank_label: string
    pinax: number
    cell_label: string
    printed_page: string
  }
  source_columns: HistoricalSourceColumn[]
  rod_templates: RodTemplate[]
  required_template_ids: string[]
  canonical_read_band: number
  tone: {
    number: number
    name: string
    system: string
    witness: string
    degree_to_pitch_class: Record<string, string>
    record: string
    provenance_class: string
  }
  physical_reconstruction: {
    classification: 'H1'
    note: string
  }
  limits: string[]
}

export interface ColumnRodInstance {
  instance_id: string
  template_id: string
  source_column_id: string
  copy_index: number
  location: RodLocation
  vertical_offset: number
  order: number
}

export interface HistoricalVoiceEvent {
  degree: number
  pitch_class: string
  provenance: { vperm_cell: string; tone_cell: string }
}

export interface HistoricalEvent {
  index: number
  offset_minim_units: number
  duration_minim_units: number
  duration_symbol: string
  rhythm_provenance: { cell: string }
  voices: Record<VoiceName, HistoricalVoiceEvent>
}

export interface HistoricalFragment {
  format: 'neo-arca-historica-symbolic/v1'
  canonical: true
  status: 'verified-historical-fragment'
  edition_policy: 'PRINT_1650'
  description: string
  selection: {
    syntagma: number
    pinax: number
    stropha: number
    vperm: number
    rperm: number
    tone: number
    tone_name: string
    system: string
    tone_witness: string
  }
  time_unit: 'relative minim'
  total_duration_minim_units: number
  events: HistoricalEvent[]
  provenance: {
    transcription_protocol: string
    components: Record<string, { record: string; witness_ids: string[] }>
    witnesses: Array<{
      id: string
      independence_key: string
      institution?: string
      record?: string
    }>
  }
  explicitly_not_claimed: string[]
}

export interface HistoricalExecution {
  format: 'neo-arca-mechanica-execution/v1'
  request_fingerprint: string
  arrangement: {
    read_band: number
    rod_instances: ColumnRodInstance[]
    classification: string
  }
  fragment: HistoricalFragment
}

export interface InstrumentState {
  phase: InstrumentPhase
  focusedBank: 1 | 2 | 3 | null
  focusedCell: number | null
  rods: ColumnRodInstance[]
  heldRodId: string | null
  toneEngaged: boolean
  execution: HistoricalExecution | null
  error: string | null
  provenanceOpen: boolean
  reducedMotion: boolean
}

export type InstrumentAction =
  | { type: 'OPEN_ARCA' }
  | { type: 'CLOSE_ARCA' }
  | { type: 'FOCUS_BANK'; bank: 1 | 2 | 3 }
  | { type: 'FOCUS_CELL'; cell: number }
  | { type: 'RETRIEVE_ROD'; template: RodTemplate }
  | { type: 'PLACE_HELD_ROD' }
  | { type: 'MOVE_ROD'; instanceId: string; offset: number }
  | { type: 'ENGAGE_TONE' }
  | { type: 'EXECUTE' }
  | { type: 'EXECUTION_SUCCESS'; execution: HistoricalExecution }
  | { type: 'EXECUTION_ERROR'; message: string }
  | { type: 'TOGGLE_PROVENANCE' }
  | { type: 'SET_REDUCED_MOTION'; value: boolean }

export interface AlignmentRequest {
  format: 'neo-arca-mechanica-alignment/v1'
  read_band: number
  tone: { number: number; engaged: boolean }
  rod_instances: ColumnRodInstance[]
}
