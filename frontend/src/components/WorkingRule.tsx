import { forwardRef } from 'react'
import type {
  HistoricalManifest,
  InstrumentAffordance,
  InstrumentState,
  InstrumentView,
} from '../instrument/types'
import { ColumnRod } from './ColumnRod'

interface WorkingRuleProps {
  manifest: HistoricalManifest
  state: InstrumentState
  view: InstrumentView
  alignmentReady: boolean
  executionReady: boolean
  nextAffordance: InstrumentAffordance
  onPlaceHeld: () => void
  onMoveRod: (instanceId: string, offset: number) => void
  onExecute: () => void
}

/**
 * The transverse carriage. This is not a separate surface: it is the drawer the
 * Arca pushes out of its own front, carrying the brass rule the rods are read
 * against. It remains mounted while the Mensa takes semantic focus so the rods
 * the reader just aligned never vanish at the moment they succeed.
 */
export const WorkingRule = forwardRef<HTMLDivElement, WorkingRuleProps>(function WorkingRule({
  manifest,
  state,
  view,
  alignmentReady,
  executionReady,
  nextAffordance,
  onPlaceHeld,
  onMoveRod,
  onExecute,
}, railRef) {
  const sources = new Map(manifest.source_columns.map((source) => [source.id, source]))
  const workspaceRods = state.rods.filter((rod) => rod.location === 'workspace')
  const required = manifest.required_template_ids.length
  const allPlaced = workspaceRods.length === required
  const alignmentCued = nextAffordance === 'align_rods'
  const readCued = nextAffordance === 'read_transverse'
  const deferred = view === 'tone'
  const brokenCount = workspaceRods.filter((rod) => {
    const source = sources.get(rod.source_column_id)
    return source ? source.bands[rod.vertical_offset].status !== 'verified' : false
  }).length

  const status = !allPlaced
    ? `${workspaceRods.length}/${required} CARRIERS SEATED`
    : alignmentReady
      ? state.toneEngaged ? 'TONE II · READY TO READ' : 'LECTIO CONCORDAT · H0'
      : `LECTIO INTERRUPTA · ${brokenCount} SEALED`

  return (
    <section
      className={`machine-carriage ${alignmentCued ? 'is-aligning' : ''} ${alignmentReady ? 'is-concordant' : ''} ${deferred ? 'is-deferred' : ''}`}
      aria-label="Transverse reading carriage"
      data-rods={workspaceRods.length}
    >
      <div className="carriage__runners" aria-hidden="true"><i /><i /></div>

      <header className="carriage__plate">
        {view === 'working' ? (
          <h2 id="working-rule-title">Lectio transversa</h2>
        ) : (
          <p className="carriage__plate-title" aria-hidden="true">Lectio transversa</p>
        )}
        <p className={`rule-status ${alignmentReady ? 'is-ready' : ''}`} role="status">{status}</p>
      </header>

      <div className="carriage__bed" ref={railRef}>
        {/* The brass transverse rule: spans exactly the rods it reads. */}
        <div className={`transverse-rule ${alignmentReady ? 'is-continuous' : ''} ${alignmentCued ? 'is-cued' : ''}`} aria-hidden="true">
          <span className="transverse-rule__cap transverse-rule__cap--left" />
          <span className="transverse-rule__bar" />
          <span className="transverse-rule__cap transverse-rule__cap--right" />
          <span className="transverse-rule__legend">LECTIO TRANSVERSA</span>
        </div>

        {state.heldRodId ? (
          <button type="button" className="placement-field is-cued" onClick={onPlaceHeld}>
            <span className="placement-field__rod" aria-hidden="true" />
            Seat the lifted rod in the transverse rail
          </button>
        ) : workspaceRods.length === 0 ? (
          <div className="empty-rail">
            <span className="empty-rail__slots" aria-hidden="true"><i /><i /><i /></span>
            <p>The rail is empty. Lift the carriers out of Cell IV.</p>
          </div>
        ) : (
          <div className={`rod-array ${alignmentReady ? 'is-concordant' : 'is-broken'}`} aria-label="Column-rods standing side by side on the rule">
            {workspaceRods.map((rod) => {
              const source = sources.get(rod.source_column_id)
              if (!source) return null
              return (
                <ColumnRod
                  key={rod.instance_id}
                  rod={rod}
                  source={source}
                  onMove={(offset) => onMoveRod(rod.instance_id, offset)}
                />
              )
            })}
            {Array.from({ length: Math.max(0, required - workspaceRods.length) }, (_, index) => (
              <div className="rod-gap" key={`gap-${index}`} aria-hidden="true"><span /></div>
            ))}
          </div>
        )}
      </div>

      <footer className="carriage__apron">
        <button
          type="button"
          className={`read-lever ${readCued ? 'is-cued' : ''}`}
          disabled={!executionReady || state.phase === 'executing'}
          onClick={onExecute}
        >
          <span className="read-lever__pull" aria-hidden="true" />
          {state.phase === 'executing' ? 'Reading…' : 'Read the transverse'}
        </button>
      </footer>
    </section>
  )
})
