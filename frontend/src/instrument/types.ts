export type InstrumentPhase =
  | 'dormant' | 'open' | 'bank_focus' | 'cell_focus' | 'carrier_held'
  | 'carrier_seated' | 'executing' | 'revealed' | 'error'
export type InstrumentView = 'arca' | 'cabinet' | 'cell' | 'working' | 'tone' | 'revelation'
export type InstrumentAffordance =
  | 'open_arca' | 'focus_bank_i' | 'open_cell_iv' | 'retrieve_carrier' | 'place_held_carrier'
  | 'inspect_event' | 'read_fragment' | 'await_execution' | 'inspect_revelation' | 'recover'
export type VoiceName = 'cantus' | 'altus' | 'tenor' | 'bassus'
export interface CriticalEditionCarrier {
  carrier_id: string
  edition_id: string
  label: string
  classification: 'H1'
  editorial_pairing: { classification: 'H1'; note: string }
  pitch_source: {
    source_column_id: string
    immutable_record: string
    provenance_paths: string[]
    content: { rows: Record<VoiceName, number[]> }
  }
  rhythm_source: {
    source_column_id: string
    immutable_record: string
    provenance_paths: string[]
    content: {
      glyphs: string[]
      glyphs_classification: 'H0'
      relative_minim_units: number[]
      relative_minim_units_classification: 'derived project normalization'
    }
  }
}
export interface HistoricalManifest {
  format: 'neo-arca-mechanica-manifest/v2'
  manifest_id: string
  content_digest: string
  title: string
  cell: { syntagma: number; bank_label: string; pinax: number; cell_label: string; printed_page: string }
  critical_edition_carrier: CriticalEditionCarrier
  tone: {
    number: number; name: string; system: string; witness: string
    degree_to_pitch_class: Record<string, string>
    record: string; provenance_class: string
    witness_classification: 'H0'; operating_policy_classification: 'H1'; known_conflict: string
  }
  physical_reconstruction: { classification: 'H1'; note: string }
  limits: string[]
}
export interface CarrierInstance {
  instance_id: string
  carrier_id: string
  edition_id: string
  location: 'cell' | 'hand' | 'workspace'
}
export interface HistoricalReadingRequest {
  format: 'neo-arca-mechanica-reading/v2'
  manifest_id: string
  content_digest: string
  carrier_instance: CarrierInstance & { location: 'workspace' }
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
  format: 'neo-arca-mechanica-execution/v2'
  request_fingerprint: string
  reading: {
    manifest_id: string
    content_digest: string
    carrier_instance: CarrierInstance & { location: 'workspace' }
    tone: { number: number; witness: string }
    classification: 'H0-backed content through H1 critical-edition carrier'
  }
  fragment: HistoricalFragment
}
export interface InstrumentState {
  phase: InstrumentPhase
  focusedBank: 1 | 2 | 3 | null
  focusedCell: number | null
  carriers: CarrierInstance[]
  heldCarrierId: string | null
  readingPosition: number
  execution: HistoricalExecution | null
  error: string | null
  provenanceOpen: boolean
  reducedMotion: boolean
}
export type InstrumentAction =
  | { type: 'OPEN_ARCA' } | { type: 'CLOSE_ARCA' }
  | { type: 'FOCUS_BANK'; bank: 1 | 2 | 3 }
  | { type: 'FOCUS_CELL'; cell: number }
  | { type: 'RETRIEVE_CARRIER' } | { type: 'PLACE_HELD_CARRIER' }
  | { type: 'SET_READING_POSITION'; position: number }
  | { type: 'EXECUTE' }
  | { type: 'EXECUTION_SUCCESS'; execution: HistoricalExecution }
  | { type: 'EXECUTION_ERROR'; message: string }
  | { type: 'RETURN_TO_WORKING' }
  | { type: 'TOGGLE_PROVENANCE' }
  | { type: 'SET_REDUCED_MOTION'; value: boolean }
