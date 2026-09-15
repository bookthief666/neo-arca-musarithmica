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
  /** Lift a stored virga into the hand. Dispatches canonical RETRIEVE_ROD. */
  onRetrieveRod: (templateId: string) => void
  /** Seat the held virga. Dispatches canonical PLACE_HELD_ROD. */
  onPlaceHeldRod: () => void
  onMoveRod: (instanceId: string, offset: number) => void
  onEngageTone: () => void
  onExecute: () => void
  onReturn: () => void
}

export function AccessibleInstrumentControls({
  manifest, state, nextAffordance, alignmentReady, executionReady,
  onOpen, onClose, onFocusBank, onFocusCell, onRetrieveRod, onPlaceHeldRod, onMoveRod,
  onEngageTone, onExecute, onReturn,
}: AccessibleControlsProps) {
  const [open, setOpen] = useState(false)
  const panelId = useId()

  const isOpen = state.phase !== 'dormant'
  const sources = new Map(manifest.source_columns.map((source) => [source.id, source]))
  const held = state.heldRodId
    ? state.rods.find((rod) => rod.instance_id === state.heldRodId) ?? null
    : null
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

        {/* The SAME two-stage grammar the object performs: a virga is lifted
            into the hand, and then seated. Skipping the held state here would
            leave a screen-reader user operating a different machine from the
            one the scene is showing. */}
        <section aria-label="The virgae">
          {manifest.rod_templates.map((template) => {
            const rod = state.rods.find((candidate) => candidate.template_id === template.template_id)
            const isHeld = rod !== undefined && rod.instance_id === state.heldRodId

            if (isHeld) {
              return (
                <button
                  key={template.template_id}
                  type="button"
                  data-cued={nextAffordance === 'place_held_rod'}
                  onClick={onPlaceHeldRod}
                >
                  Seat held virga, {template.label}, in the transverse carriage
                </button>
              )
            }

            if (rod) {
              return (
                <p key={template.template_id} className="spatial-controls__done">
                  {template.label} — seated in the transverse carriage
                </p>
              )
            }

            return (
              <button
                key={template.template_id}
                type="button"
                // One hand, one carrier: while a virga is held, the only rod
                // action available is seating it.
                disabled={state.focusedCell !== 4 || held !== null}
                data-cued={nextAffordance === 'deploy_rods'}
                onClick={() => onRetrieveRod(template.template_id)}
              >
                Lift {template.label} from Cell IV
              </button>
            )
          })}
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
