import type { HistoricalManifest, InstrumentState } from '../instrument/types'
import { ColumnRod } from './ColumnRod'

interface WorkingRuleProps {
  manifest: HistoricalManifest
  state: InstrumentState
  alignmentReady: boolean
  executionReady: boolean
  onPlaceHeld: () => void
  onMoveRod: (instanceId: string, offset: number) => void
  onExecute: () => void
}

export function WorkingRule({
  manifest,
  state,
  alignmentReady,
  executionReady,
  onPlaceHeld,
  onMoveRod,
  onExecute,
}: WorkingRuleProps) {
  const sources = new Map(manifest.source_columns.map((source) => [source.id, source]))
  const workspaceRods = state.rods.filter((rod) => rod.location === 'workspace')
  const allPlaced = workspaceRods.length === manifest.required_template_ids.length

  return (
    <section className="working-rule" aria-labelledby="working-rule-title">
      <header className="working-rule__heading">
        <div>
          <p className="eyebrow">PALIMPSESTVS OPERATIVVS · M1.0</p>
          <h2 id="working-rule-title">Transverse reading rule</h2>
        </div>
        <p className={`rule-status ${alignmentReady ? 'is-ready' : ''}`} role="status">
          {alignmentReady ? 'BAND 01 · H0 VERIFIED' : 'ALIGN THREE CARRIERS TO BAND 01'}
        </p>
      </header>

      <div className="rule-bed">
        <div className="read-band" aria-hidden="true">
          <span>LECTIO TRANSVERSA</span>
        </div>

        {state.heldRodId ? (
          <button type="button" className="placement-field" onClick={onPlaceHeld}>
            <span className="placement-field__rod" aria-hidden="true" />
            Lay the lifted rod beside the rule
          </button>
        ) : workspaceRods.length === 0 ? (
          <div className="empty-rule">
            <span aria-hidden="true">Ⅰ · Ⅱ · Ⅲ</span>
            <p>Open Cell IV and retrieve its individual carriers.</p>
          </div>
        ) : (
          <div className="rod-array" aria-label="Retrieved column-rods arranged side-by-side">
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
        <p>
          {!allPlaced
            ? `${workspaceRods.length}/3 carriers placed. Repeated Vperm copies remain separate physical instances.`
            : alignmentReady
              ? 'The only transcribed band crosses all three rods. Consult Tone II in the lid.'
              : 'A sealed position crosses the rule. No HISTORICA computation is authorised.'}
        </p>
        <button
          type="button"
          className="read-lever"
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
