import type { HistoricalManifest, InstrumentAffordance, InstrumentState } from '../instrument/types'
import { ColumnRod } from './ColumnRod'

interface WorkingRuleProps {
  manifest: HistoricalManifest
  state: InstrumentState
  alignmentReady: boolean
  executionReady: boolean
  nextAffordance: InstrumentAffordance
  onPlaceHeld: () => void
  onMoveRod: (instanceId: string, offset: number) => void
  onExecute: () => void
}

export function WorkingRule({
  manifest,
  state,
  alignmentReady,
  executionReady,
  nextAffordance,
  onPlaceHeld,
  onMoveRod,
  onExecute,
}: WorkingRuleProps) {
  const sources = new Map(manifest.source_columns.map((source) => [source.id, source]))
  const workspaceRods = state.rods.filter((rod) => rod.location === 'workspace')
  const allPlaced = workspaceRods.length === manifest.required_template_ids.length
  const alignmentCued = nextAffordance === 'align_rods'
  const readCued = nextAffordance === 'read_transverse'

  const status = !allPlaced
    ? `CELL IV · ${workspaceRods.length}/3 SEATED`
    : alignmentReady
      ? state.toneEngaged ? 'TONE II · READY TO READ' : 'LECTIO CONCORDAT · H0'
      : 'LECTIO INTERRUPTA'

  const footer = !allPlaced
    ? 'The deployed carriers remain physically distinct; Cell IV still contains the missing copies.'
    : alignmentReady
      ? state.toneEngaged
        ? 'Tone II now resolves the verified transverse degrees.'
        : 'The verified band is continuous. The Mensa Tonographica is now active.'
      : 'A sealed band breaks the transverse line; HISTORICA remains unavailable.'

  return (
    <section className={`working-rule ${alignmentCued ? 'is-aligning' : ''}`} aria-labelledby="working-rule-title">
      <header className="working-rule__heading">
        <div>
          <p className="eyebrow">PALIMPSESTVS OPERATIVVS · M1.0.1A</p>
          <h2 id="working-rule-title">Lectio transversa</h2>
        </div>
        <p className={`rule-status ${alignmentReady ? 'is-ready' : ''}`} role="status">{status}</p>
      </header>

      <div className="rule-bed">
        <div className={`read-band ${alignmentReady ? 'is-complete' : ''} ${alignmentCued ? 'is-cued' : ''}`} aria-hidden="true">
          <span>LECTIO TRANSVERSA</span>
        </div>

        {state.heldRodId ? (
          <button type="button" className="placement-field is-cued" onClick={onPlaceHeld}>
            <span className="placement-field__rod" aria-hidden="true" />
            Seat the lifted rod in the transverse rail
          </button>
        ) : workspaceRods.length === 0 ? (
          <div className="empty-rule">
            <span aria-hidden="true">Ⅰ · Ⅱ · Ⅲ</span>
            <p>The transverse rail is empty.</p>
          </div>
        ) : (
          <div
            className={`rod-array ${alignmentReady ? 'is-concordant' : 'is-broken'}`}
            aria-label="Retrieved column-rods arranged side-by-side"
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
          </div>
        )}
      </div>

      <footer className="working-rule__footer">
        <p>{footer}</p>
        <button
          type="button"
          className={`read-lever ${readCued ? 'is-cued' : ''}`}
          disabled={!executionReady || state.phase === 'executing'}
          onClick={onExecute}
        >
          <span aria-hidden="true">Ⅲ</span>
          {state.phase === 'executing' ? 'Reading…' : 'Read the transverse'}
        </button>
      </footer>
    </section>
  )
}
