import type { HistoricalExecution, HistoricalManifest } from '../instrument/types'

export const manifestFixture: HistoricalManifest = {
  format: 'neo-arca-mechanica-manifest/v1',
  title: 'PINAX IV. Iambica Euripedaea penultima longa.',
  cell: { syntagma: 1, bank_label: 'Dodecamorium', pinax: 4, cell_label: 'Cell IV', printed_page: '83' },
  source_columns: [
    {
      id: 'S1.P4.STROPHA1.VPERM01',
      kind: 'pitch',
      label: 'Columna musarithmica · Vperm 01',
      record: 'pitch-record',
      provenance_class: 'H0-V',
      bands: [
        {
          index: 1,
          status: 'verified',
          classification: 'H0',
          label: 'Stropha I · Vperm 01',
          content: {
            rows: {
              cantus: [5, 5, 3, 2, 3, 3],
              altus: [8, 7, 5, 7, 7, 7],
              tenor: [3, 2, 3, 4, 5, 5],
              bassus: [8, 5, 8, 7, 3, 3],
            },
          },
        },
        ...Array.from({ length: 9 }, (_, index) => ({
          index: index + 2,
          status: 'untranscribed' as const,
          classification: 'UNKNOWN' as const,
          label: `Band ${index + 2} · sealed`,
          content: null,
        })),
      ],
    },
    {
      id: 'S1.P4.NOTAE_TEMPORIS.DUPLE.RPERM03',
      kind: 'rhythm',
      label: 'Notae Temporis · Rperm 03',
      record: 'rhythm-record',
      provenance_class: 'H0-V',
      bands: [
        {
          index: 1,
          status: 'verified',
          classification: 'H0',
          label: 'Notae Temporis · Rperm 03',
          content: { glyphs: ['minim', 'minim', 'minim', 'minim', 'semibreve', 'semibreve'], relative_minim_units: [1, 1, 1, 1, 2, 2] },
        },
        ...Array.from({ length: 9 }, (_, index) => ({
          index: index + 2,
          status: 'untranscribed' as const,
          classification: 'UNKNOWN' as const,
          label: `Band ${index + 2} · sealed`,
          content: null,
        })),
      ],
    },
  ],
  rod_templates: [
    { template_id: 'pinax04-vperm-copy-1', source_column_id: 'S1.P4.STROPHA1.VPERM01', copy_index: 1, label: 'Vperm exemplar 1' },
    { template_id: 'pinax04-vperm-copy-2', source_column_id: 'S1.P4.STROPHA1.VPERM01', copy_index: 2, label: 'Vperm exemplar 2' },
    { template_id: 'pinax04-rperm03-copy-1', source_column_id: 'S1.P4.NOTAE_TEMPORIS.DUPLE.RPERM03', copy_index: 1, label: 'Rperm exemplar 1' },
  ],
  required_template_ids: ['pinax04-vperm-copy-1', 'pinax04-vperm-copy-2', 'pinax04-rperm03-copy-1'],
  canonical_read_band: 1,
  tone: {
    number: 2,
    name: 'Hypodorius',
    system: 'mollis',
    witness: 'printed p.51 Mensa Tonographica',
    degree_to_pitch_class: { '1': 'G', '2': 'A', '3': 'Bb', '4': 'C', '5': 'D', '6': 'Eb', '7': 'F#', '8': 'G' },
    record: 'tone-record',
    provenance_class: 'H0-V',
  },
  physical_reconstruction: { classification: 'H1', note: 'test reconstruction' },
  limits: [],
}

export const executionFixture = {
  format: 'neo-arca-mechanica-execution/v1',
  request_fingerprint: '0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef',
  arrangement: { read_band: 1, rod_instances: [], classification: 'H0 data through H1 physical reconstruction' },
  fragment: {
    format: 'neo-arca-historica-symbolic/v1',
    canonical: true,
    status: 'verified-historical-fragment',
    edition_policy: 'PRINT_1650',
    description: 'Pinax-IV historical fragment',
    selection: { syntagma: 1, pinax: 4, stropha: 1, vperm: 1, rperm: 3, tone: 2, tone_name: 'Hypodorius', system: 'mollis', tone_witness: 'printed p.51 Mensa Tonographica' },
    time_unit: 'relative minim',
    total_duration_minim_units: 8,
    events: Array.from({ length: 6 }, (_, index) => ({
      index: index + 1,
      offset_minim_units: index,
      duration_minim_units: index > 3 ? 2 : 1,
      duration_symbol: index > 3 ? 'semibreve' : 'minim',
      rhythm_provenance: { cell: `R${index + 1}` },
      voices: {
        cantus: { degree: 5, pitch_class: 'D', provenance: { vperm_cell: `C${index + 1}`, tone_cell: 'T5' } },
        altus: { degree: 8, pitch_class: 'G', provenance: { vperm_cell: `A${index + 1}`, tone_cell: 'T8' } },
        tenor: { degree: 3, pitch_class: 'Bb', provenance: { vperm_cell: `T${index + 1}`, tone_cell: 'T3' } },
        bassus: { degree: 8, pitch_class: 'G', provenance: { vperm_cell: `B${index + 1}`, tone_cell: 'T8' } },
      },
    })),
    provenance: {
      transcription_protocol: 'docs/HISTORICAL_DATA_TRANSCRIPTION_SPEC.md',
      components: {},
      witnesses: [{ id: 'W1', independence_key: 'ONE', institution: 'Witness Library' }],
    },
    explicitly_not_claimed: ['absolute octave/register placement'],
  },
} satisfies HistoricalExecution
