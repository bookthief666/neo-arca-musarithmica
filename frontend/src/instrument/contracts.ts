import type { HistoricalExecution, HistoricalManifest } from './types'

type Check = (value: unknown, path: string) => void
const fail = (path: string): never => { throw new Error('Historical v2 contract error at ' + path) }
const string: Check = (v, p) => { if (typeof v !== 'string' || !v.trim()) fail(p) }
const positive: Check = (v, p) => { if (typeof v !== 'number' || !Number.isFinite(v) || v <= 0) fail(p) }
const integer: Check = (v, p) => { positive(v, p); if (!Number.isInteger(v)) fail(p) }
const nonnegative: Check = (v, p) => { if (typeof v !== 'number' || !Number.isFinite(v) || v < 0) fail(p) }
const literal = (expected: string | boolean): Check => (v, p) => { if (v !== expected) fail(p + ' (expected ' + expected + ')') }
const object = (v: unknown, p: string): Record<string, unknown> => {
  if (!v || typeof v !== 'object' || Array.isArray(v)) return fail(p)
  return v as Record<string, unknown>
}
const shape = (fields: Record<string, Check>, optional: string[] = []): Check => (v, p) => {
  const obj = object(v, p)
  if (Object.keys(obj).some(k => !(k in fields))) fail(p + ': unexpected fields')
  for (const [key, check] of Object.entries(fields)) {
    if (optional.includes(key) && !(key in obj)) continue
    check(obj[key], p + '.' + key)
  }
}
const array = (item: Check, count?: number): Check => (v, p) => {
  if (!Array.isArray(v) || (count !== undefined && v.length !== count)) return fail(p)
  v.forEach((x, i) => item(x, p + '[' + i + ']'))
}
const digest: Check = (v, p) => { string(v, p); if (!/^[a-f0-9]{64}$/.test(v as string)) fail(p) }
const degree: Check = (v,p) => { integer(v,p); if ((v as number) > 8) fail(p) }
const voices = (check: Check) => shape({ cantus: check, altus: check, tenor: check, bassus: check })
const source = (content: Check) => shape({
  source_column_id: string, immutable_record: string, provenance_paths: array(string), content,
})
const instance = shape({ instance_id: string, carrier_id: string, edition_id: string, location: literal('workspace') })
const manifestCheck = shape({
  format: literal('neo-arca-mechanica-manifest/v2'), manifest_id: string, content_digest: digest, title: string,
  cell: shape({ syntagma: integer, bank_label: string, pinax: integer, cell_label: string, printed_page: string }),
  critical_edition_carrier: shape({
    carrier_id: string, edition_id: string, label: string, classification: literal('H1'),
    editorial_pairing: shape({ classification: literal('H1'), note: string }),
    pitch_source: source(shape({ rows: voices(array(degree, 6)) })),
    rhythm_source: source(shape({
      glyphs: array(string, 6), glyphs_classification: literal('H0'),
      relative_minim_units: array(positive, 6),
      relative_minim_units_classification: literal('derived project normalization'),
    })),
  }),
  tone: shape({
    number: integer, name: string, system: string, witness: string,
    degree_to_pitch_class: shape(Object.fromEntries(Array.from({length:8}, (_,i) => [String(i+1), string]))),
    record: string, provenance_class: string, witness_classification: literal('H0'),
    operating_policy_classification: literal('H1'), known_conflict: string,
  }),
  physical_reconstruction: shape({ classification: literal('H1'), note: string }),
  limits: array(string),
})
const component = shape({ record: string, witness_ids: array(string) })
const executionCheck = shape({
  format: literal('neo-arca-mechanica-execution/v2'), request_fingerprint: digest,
  reading: shape({
    manifest_id: string, content_digest: digest, carrier_instance: instance,
    tone: shape({ number: integer, witness: string }),
    classification: literal('H0-backed content through H1 critical-edition carrier'),
  }),
  fragment: shape({
    format: literal('neo-arca-historica-symbolic/v1'), canonical: literal(true),
    status: literal('verified-historical-fragment'), edition_policy: literal('PRINT_1650'),
    description: string,
    selection: shape({ syntagma: integer, pinax: integer, stropha: integer, vperm: integer,
      rperm: integer, tone: integer, tone_name: string, system: string, tone_witness: string }),
    time_unit: literal('relative minim'), total_duration_minim_units: positive,
    events: array(shape({
      index: integer, offset_minim_units: nonnegative, duration_minim_units: positive,
      duration_symbol: string, rhythm_provenance: shape({ cell: string }),
      voices: voices(shape({ degree, pitch_class: string,
        provenance: shape({ vperm_cell: string, tone_cell: string }) })),
    }), 6),
    provenance: shape({
      transcription_protocol: string,
      components: shape({ pitch_permutation: component, rhythm: component, tone_lookup: component }),
      witnesses: array(shape({ id: string, independence_key: string, institution: string, record: string }, ['institution','record'])),
    }),
    explicitly_not_claimed: array(string),
  }),
})
export function decodeHistoricalManifest(value: unknown): HistoricalManifest {
  manifestCheck(value, 'manifest/v2')
  // The recursive check above covers every contract-owned field before this narrowing.
  return value as HistoricalManifest
}
export function decodeHistoricalExecution(value: unknown): HistoricalExecution {
  executionCheck(value, 'execution/v2')
  const execution = value as HistoricalExecution
  if (execution.reading.tone.number !== execution.fragment.selection.tone ||
      execution.reading.tone.witness !== execution.fragment.selection.tone_witness) fail('execution selection')
  return execution
}
