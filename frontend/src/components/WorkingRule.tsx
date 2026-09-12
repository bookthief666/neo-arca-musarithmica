import { forwardRef } from 'react'
import { Scholium } from './Scholium'
import type {
  HistoricalManifest,
  InstrumentAffordance,
  InstrumentState,
  InstrumentView,
} from '../instrument/types'
import { ColumnRod } from './ColumnRod'
import { StarMedallion } from './Ornament'

interface WorkingRuleProps {
  manifest: HistoricalManifest
  state: InstrumentState
  view: InstrumentView
  alignmentReady: boolean
  executionReady: boolean
  nextAffordance: InstrumentAffordance
  scholium: string | null
  onPlaceHeld: () => void
  onMoveRod: (instanceId: string, offset: number) => void
  onExecute: () => void
}

/**
 * The transverse carriage. This is not a separate surface: it is the drawer the
 * Arca pushes out of its own front, running on the cabinet's rails and carrying
 * the brass rule the rods are read against. It remains mounted while the Mensa
 * takes semantic focus so the rods the reader just aligned never vanish at the
 * moment they succeed.
 */
export const WorkingRule = forwardRef<HTMLDivElement, WorkingRuleProps>(function WorkingRule({
  manifest,
  state,
  view,
  alignmentReady,
  executionReady,
  nextAffordance,
  scholium,
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

  const carriageScholium =
    nextAffordance === 'place_held_rod' ||
    nextAffordance === 'align_rods' ||
    nextAffordance === 'read_transverse' ||
    nextAffordance === 'await_execution'
      ? scholium
      : null

  return (
    <section
      className={`machine-carriage ${alignmentCued ? 'is-aligning' : ''} ${alignmentReady ? 'is-concordant' : ''} ${deferred ? 'is-deferred' : ''}`}
      aria-label="Transverse reading carriage"
      data-rods={workspaceRods.length}
    >
      {/* Rails and lip: the joinery that proves this drawer runs in the cabinet. */}
      <div className="carriage__mouth" aria-hidden="true">
        <span className="carriage__reveal" />
        <span className="carriage__runner carriage__runner--left" />
        <span className="carriage__runner carriage__runner--right" />
      </div>

      <div className="carriage__box">
        <header className="carriage__plate">
          {view === 'working' ? (
            <h2 id="working-rule-title">Lectio transversa</h2>
          ) : (
            <p className="carriage__plate-title" aria-hidden="true">Lectio transversa</p>
          )}
          <p className={`rule-status ${alignmentReady ? 'is-ready' : ''}`} role="status">{status}</p>
        </header>

        <div className="carriage__bed" ref={railRef}>
          {/* The rails the carriage runs on, screwed down each side. */}
          <span className="carriage__siderail carriage__siderail--left" aria-hidden="true">
            <i /><i /><i />
          </span>
          <span className="carriage__siderail carriage__siderail--right" aria-hidden="true">
            <i /><i /><i />
          </span>
          {/* The brass transverse rule. It is drawn ACROSS the whole bed at the
              reading height; each rod then either continues the channel through
              itself or interrupts it. Continuity is geometry, not colour. */}
          <div
            className={`transverse-rule ${alignmentReady ? 'is-continuous' : ''} ${alignmentCued ? 'is-cued' : ''}`}
            aria-hidden="true"
          >
            <span className="transverse-rule__cap transverse-rule__cap--left" />
            <span className="transverse-rule__channel" />
            <span className="transverse-rule__cap transverse-rule__cap--right" />

          </div>

          {/* The reading medallion rides the rule and marks where it reads. It is
              a sibling of the rod array, not a child of the rule, so it paints
              in front of the carriers the rule passes behind. */}
          <span
            className={`reading-medallion ${alignmentReady ? 'is-continuous' : ''}`}
            aria-hidden="true"
          >
            <StarMedallion className="reading-medallion__star" />
          </span>

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
            <div
              className={`rod-array ${alignmentReady ? 'is-concordant' : 'is-broken'}`}
              aria-label="Column-rods standing side by side on the rule"
            >
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
          {/* The drawer front: an engraved brass plate and a turned knob pull,
              which is what tells the eye this whole surface pulls out. */}
          <span className="carriage__motto" aria-hidden="true">MOTVS GENERAT HARMONIAM</span>
          <span className="carriage__knob" aria-hidden="true" />
          <Scholium text={carriageScholium} place="bed" />
          <button
            type="button"
            className={`read-lever ${readCued ? 'is-cued' : ''}`}
            disabled={!executionReady || state.phase === 'executing'}
            onClick={onExecute}
          >
            <span className="read-lever__pull" aria-hidden="true" />
            <span className="read-lever__text">
              {state.phase === 'executing' ? 'Reading…' : 'Read the transverse'}
            </span>
          </button>
        </footer>
      </div>
    </section>
  )
})
