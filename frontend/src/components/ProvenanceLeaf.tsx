import type { HistoricalExecution, HistoricalManifest } from '../instrument/types'

interface ProvenanceLeafProps {
  manifest: HistoricalManifest
  execution: HistoricalExecution | null
  open: boolean
  onToggle: () => void
}

export function ProvenanceLeaf({ manifest, execution, open, onToggle }: ProvenanceLeafProps) {
  return (
    <aside className={`provenance-leaf ${open ? 'is-open' : ''}`}>
      <button type="button" className="provenance-tab" aria-expanded={open} onClick={onToggle}>
        <span>H0</span> Inspect witnesses
      </button>
      {open && (
        <div className="provenance-copy">
          <header>
            <p>APPARATVS FONTIVM</p>
            <span>{manifest.cell.cell_label} · printed p. {manifest.cell.printed_page}</span>
          </header>
          <dl>
            <div><dt>Pitch record</dt><dd>{manifest.source_columns[0].record}</dd></div>
            <div><dt>Rhythm record</dt><dd>{manifest.source_columns[1].record}</dd></div>
            <div><dt>Tone witness</dt><dd>{manifest.tone.witness}</dd></div>
            <div><dt>Carrier body</dt><dd>H1 restrained reconstruction</dd></div>
            {execution && <div><dt>Request seal</dt><dd>{execution.request_fingerprint.slice(0, 16)}…</dd></div>}
          </dl>
          {execution ? (
            <ul>
              {execution.fragment.provenance.witnesses.map((witness) => (
                <li key={witness.id}><b>{witness.institution}</b><span>{witness.independence_key}</span></li>
              ))}
            </ul>
          ) : (
            <p>Execute the verified alignment to reveal the exact witnesses carried into the result.</p>
          )}
        </div>
      )}
    </aside>
  )
}
