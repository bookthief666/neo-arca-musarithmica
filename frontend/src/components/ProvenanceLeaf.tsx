import type { HistoricalExecution, HistoricalManifest } from '../instrument/types'

interface ProvenanceLeafProps {
  manifest: HistoricalManifest
  execution: HistoricalExecution | null
  open: boolean
  onToggle: () => void
}

/**
 * Provenance stays complete but visually quiet: a small wax seal set into the
 * machine's own frame, which opens a scholarly folio sheet over the instrument
 * instead of standing beside it as a competing panel.
 */
export function ProvenanceLeaf({ manifest, execution, open, onToggle }: ProvenanceLeafProps) {
  return (
    <aside className={`provenance-leaf ${open ? 'is-open' : ''}`}>
      <button type="button" className="provenance-seal" aria-expanded={open} onClick={onToggle}>
        <span className="provenance-seal__wax" aria-hidden="true">H0</span>
        <span className="provenance-seal__label">Inspect witnesses</span>
      </button>

      {open && (
        <>
          <div className="provenance-scrim" onClick={onToggle} aria-hidden="true" />
          <div className="provenance-copy" role="dialog" aria-label="Apparatus fontium, source witnesses">
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
                  <li key={witness.id}><b>{witness.institution ?? witness.id}</b><span>{witness.independence_key}</span></li>
                ))}
              </ul>
            ) : (
              <p className="provenance-copy__note">Execute the verified alignment to reveal the exact witnesses carried into the result.</p>
            )}
            <button type="button" className="provenance-close" onClick={onToggle}>Close the apparatus</button>
          </div>
        </>
      )}
    </aside>
  )
}
