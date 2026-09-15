import { useId, useState } from 'react'
import { MAX_VERTICAL_OFFSET } from '../instrument/model'
import type {
  HistoricalManifest,
  InstrumentAffordance,
  InstrumentState,
} from '../instrument/types'

/**
 * THE SEMANTIC INSTRUMENT.
 *
 * A canvas is opaque to assistive technology: a screen reader meets one node
 * called "canvas" and there is nothing inside it to operate. So every action
 * the spatial instrument affords is ALSO offered here as a real button, with a
 * real name, in the real tab order.
 *
 * This is not a second instrument. It holds no state of its own and computes
 * nothing about music: it dispatches exactly the canonical actions the 3D scene
 * dispatches, so the two surfaces can never disagree about what the machine is
 * doing. It is deliberately discreet — collapsed by default, out of the way of
 * the object — but it is always present and always reachable by keyboard.
 */

export interface AccessibleControlsProps {
  manifest: HistoricalManifest
  state: InstrumentState
  nextAffordance: InstrumentAffordance
  alignmentReady: boolean
  executionReady: boolean
  onOpen: () => void
  onClose: () => void
  onFocusBank: (bank: 1 | 2 | 3) => void
  onFocusCell: (cell: number) => void
  onDeployRod: (templateId: string) => void
  onMoveRod: (instanceId: string, offset: number) => void
  onEngageTone: () => void
  onExecute: () => void
  onReturn: () => void
}

export function AccessibleInstrumentControls({
  manifest, state, nextAffordance, alignmentReady, executionReady,
  onOpen, onClose, onFocusBank, onFocusCell, onDeployRod, onMoveRod,
  onEngageTone, onExecute, onReturn,
}: AccessibleControlsProps) {
  const [open, setOpen] = useState(false)
  const panelId = useId()

  const isOpen = state.phase !== 'dormant'
  const taken = new Set(state.rods.map((rod) => rod.template_id))
  const sources = new Map(manifest.source_columns.map((source) => [source.id, source]))
  const workspaceRods = state.rods.filter((rod) => rod.location === 'workspace')

  return (
    <div className="spatial-controls" data-open={open}>
      <button
        type="button"
        className="spatial-controls__toggle"
        aria-expanded={open}
        aria-controls={panelId}
        onClick={() => setOpen((value) => !value)}
      >
        Instrument controls
      </button>

      <div id={panelId} className="spatial-controls__panel" hidden={!open}>
        <p className="spatial-controls__note">
          Every control here operates the same mechanism as the instrument itself.
        </p>

        <section aria-label="The cabinet">
          {isOpen ? (
            <button type="button" onClick={onClose}>Close the Arca</button>
          ) : (
            <button type="button" data-cued={nextAffordance === 'open_arca'} onClick={onOpen}>
              Open the Arca
            </button>
          )}
          <button
            type="button"
            aria-pressed={state.focusedBank === 1}
            disabled={!isOpen}
            data-cued={nextAffordance === 'focus_bank_i'}
            onClick={() => onFocusBank(1)}
          >
            Bank I, DODECAMORIVM
          </button>
          <button
            type="button"
            aria-pressed={state.focusedCell === 4}
            disabled={state.focusedBank !== 1}
            data-cued={nextAffordance === 'open_cell_iv'}
            onClick={() => onFocusCell(4)}
          >
            Open Cell IV, verified Pinax IV family
          </button>
        </section>

        <section aria-label="The virgae">
          {manifest.rod_templates.map((template) => (
            taken.has(template.template_id) ? (
              <p key={template.template_id} className="spatial-controls__done">
                {template.label} — lifted out of Cell IV
              </p>
            ) : (
              <button
                key={template.template_id}
                type="button"
                disabled={state.focusedCell !== 4}
                data-cued={nextAffordance === 'deploy_rods'}
                onClick={() => onDeployRod(template.template_id)}
              >
                Deploy {template.label} to the transverse rule
              </button>
            )
          ))}
        </section>

        {workspaceRods.length > 0 && (
          <section aria-label="Band alignment">
            {workspaceRods.map((rod) => {
              const source = sources.get(rod.source_column_id)
              if (!source) return null
              const band = source.bands[rod.vertical_offset]
              const clamp = (value: number) => Math.max(0, Math.min(MAX_VERTICAL_OFFSET, value))
              return (
                <div className="spatial-controls__rod" key={rod.instance_id}>
                  <button
                    type="button"
                    role="slider"
                    aria-label={`${source.label}, copy ${rod.copy_index}. Active ${band.label}. Use up and down arrow keys or drag vertically.`}
                    aria-valuemin={1}
                    aria-valuemax={MAX_VERTICAL_OFFSET + 1}
                    aria-valuenow={rod.vertical_offset + 1}
                    aria-valuetext={band.label}
                    onKeyDown={(event) => {
                      if (event.key === 'ArrowUp') { event.preventDefault(); onMoveRod(rod.instance_id, clamp(rod.vertical_offset - 1)) }
                      else if (event.key === 'ArrowDown') { event.preventDefault(); onMoveRod(rod.instance_id, clamp(rod.vertical_offset + 1)) }
                      else if (event.key === 'Home') { event.preventDefault(); onMoveRod(rod.instance_id, 0) }
                      else if (event.key === 'End') { event.preventDefault(); onMoveRod(rod.instance_id, MAX_VERTICAL_OFFSET) }
                    }}
                  >
                    Band {rod.vertical_offset + 1} of {MAX_VERTICAL_OFFSET + 1}
                  </button>
                  <span>{band.status === 'verified' ? 'verified' : 'not transcribed'}</span>
                </div>
              )
            })}
          </section>
        )}

        <section aria-label="The Tone and the reading">
          <button
            type="button"
            aria-pressed={state.toneEngaged}
            disabled={!alignmentReady && !state.toneEngaged}
            data-cued={nextAffordance === 'engage_tone_ii'}
            onClick={onEngageTone}
          >
            Engage Tone II {manifest.tone.name}
          </button>
          <button
            type="button"
            disabled={!executionReady || state.phase === 'executing'}
            data-cued={nextAffordance === 'read_transverse'}
            onClick={onExecute}
          >
            {state.phase === 'executing' ? 'Reading…' : 'Read the transverse'}
          </button>
          {state.execution && state.phase === 'revealed' && (
            <button type="button" onClick={onReturn}>Return to the rods</button>
          )}
        </section>
      </div>
    </div>
  )
}
