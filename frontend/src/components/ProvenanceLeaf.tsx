import { useEffect, useRef } from 'react'
import type { HistoricalExecution, HistoricalManifest } from '../instrument/types'

interface ProvenanceLeafProps {
  manifest: HistoricalManifest
  execution: HistoricalExecution | null
  open: boolean
  onToggle: () => void
}

const RESEARCH_LEDGER =
  'https://github.com/bookthief666/neo-arca-musarithmica/blob/feature/m1.2.1r-historical-computation-rescue/docs/HISTORICAL_RESEARCH.md'

/**
 * Provenance stays complete but visually quiet: a small wax seal set into the
 * machine's own frame, which opens a scholarly folio sheet over the instrument
 * instead of standing beside it as a competing panel.
 */
export function ProvenanceLeaf({ manifest, execution, open, onToggle }: ProvenanceLeafProps) {
  const folio = useRef<HTMLDivElement>(null)
  const carrier = manifest.critical_edition_carrier
  const rhythm = carrier.rhythm_source.content

  // The apparatus is a sheet laid over the instrument: Escape puts it back, and
  // opening it moves focus onto the sheet so a keyboard reader is not left
  // behind on the machine underneath.
  useEffect(() => {
    if (!open) return
    folio.current?.focus()
    const onKey = (event: KeyboardEvent) => {
      if (event.key === 'Escape') { event.preventDefault(); onToggle() }
    }
    document.addEventListener('keydown', onKey)
    return () => document.removeEventListener('keydown', onKey)
  }, [open, onToggle])

  return (
    <aside className={`provenance-leaf ${open ? 'is-open' : ''}`}>
      <button type="button" className="provenance-seal" aria-expanded={open} onClick={onToggle}>
        <span className="provenance-seal__wax" aria-hidden="true">H0</span>
        <span className="provenance-seal__label">Inspect witnesses</span>
      </button>

      {open && (
        <>
          <div className="provenance-scrim" onClick={onToggle} aria-hidden="true" />
          <div
            className="provenance-copy"
            role="dialog"
            aria-modal="true"
            tabIndex={-1}
            ref={folio}
            aria-label="Apparatus fontium, source witnesses"
          >
            <header>
              <p>APPARATVS FONTIVM</p>
              <span>{manifest.cell.cell_label} · printed p. {manifest.cell.printed_page}</span>
            </header>

            <dl>
              <div>
                <dt>Vperm 01 · H0 source</dt>
                <dd>{carrier.pitch_source.source_column_id} · {carrier.pitch_source.immutable_record}</dd>
              </div>
              <div>
                <dt>Rperm 03 · H0 source</dt>
                <dd>
                  {carrier.rhythm_source.source_column_id} · {carrier.rhythm_source.immutable_record}.
                  {' '}Mensural identities · {rhythm.glyphs_classification}: {rhythm.glyphs.join(' · ')}.
                </dd>
              </div>
              <div>
                <dt>Derived rhythm normalization</dt>
                <dd>{rhythm.relative_minim_units.join(' ')} · {rhythm.relative_minim_units_classification}</dd>
              </div>
              <div>
                <dt>p.51 Tone II · H0 witness transcription</dt>
                <dd>{manifest.tone.witness} · {manifest.tone.record}</dd>
              </div>
              <div>
                <dt>Tone operation · H1 fixed operating policy</dt>
                <dd>{manifest.tone.known_conflict}</dd>
              </div>
              <div>
                <dt>Pairing · H1 editorial</dt>
                <dd>{carrier.editorial_pairing.note}</dd>
              </div>
              <div>
                <dt>Carrier mechanics · H1 reconstruction</dt>
                <dd>{manifest.physical_reconstruction.note}</dd>
              </div>
              <div>
                <dt>Schema · modern representation</dt>
                <dd>
                  {manifest.format} · manifest {manifest.manifest_id} · edition {carrier.edition_id}
                  {' '}· content digest {manifest.content_digest}
                </dd>
              </div>
              <div>
                <dt>Kernel non-claims</dt>
                <dd>{manifest.limits.join(' ')}</dd>
              </div>
              {execution && (
                <>
                  <div>
                    <dt>Executed reading identity</dt>
                    <dd>
                      {execution.reading.classification} · carrier {execution.reading.carrier_instance.instance_id}
                    </dd>
                  </div>
                  <div><dt>Request seal</dt><dd>{execution.request_fingerprint.slice(0, 16)}…</dd></div>
                </>
              )}
            </dl>

            {execution ? (
              <ul>
                {execution.fragment.provenance.witnesses.map((witness) => (
                  <li key={witness.id}><b>{witness.institution ?? witness.id}</b><span>{witness.independence_key}</span></li>
                ))}
              </ul>
            ) : (
              <p className="provenance-copy__note">Read the critical edition to reveal the exact witnesses carried into the result.</p>
            )}

            <p className="provenance-copy__note">
              Source-variant history not carried by this manifest remains in the project research ledger.
              {' '}<a href={RESEARCH_LEDGER} target="_blank" rel="noreferrer">Open the research ledger.</a>
            </p>
            <button type="button" className="provenance-close" onClick={onToggle}>Close the apparatus</button>
          </div>
        </>
      )}
    </aside>
  )
}
