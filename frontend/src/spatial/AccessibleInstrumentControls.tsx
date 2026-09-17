import { useEffect, useId, useRef, useState } from 'react'
import type { HistoricalManifest, InstrumentState, InstrumentAction } from '../instrument/types'
import { ArcaCabinet } from '../components/ArcaCabinet'
import { ColumnRod } from '../components/ColumnRod'
import { getExecutedReadingFrame, getSourceReadingFrame, type ReadingFrame } from '../instrument/reading'
import { isReadingReady } from '../instrument/model'

const VOICE_ORDER = ['cantus', 'altus', 'tenor', 'bassus'] as const
const VOICE_SHORT = { cantus: 'C', altus: 'A', tenor: 'T', bassus: 'B' } as const

function spokenPitchClass(value: string) {
  return value.replace('b', '-flat').replace('#', '-sharp')
}

function eventAnnouncement(frame: ReadingFrame) {
  const voices = VOICE_ORDER.map((voice) => {
    const value = frame.voices[voice]
    return `${VOICE_SHORT[voice]} ${value.degree} to ${spokenPitchClass(value.pitchClass)}`
  }).join('. ')
  const units = frame.duration.relativeMinimUnits
  return `Event ${frame.eventNumber} of 6. ${voices}. ${frame.duration.glyph}, ${units} relative minim ${units === 1 ? 'unit' : 'units'}.`
}

/**
 * Keyboard/screen-reader peer for the spatial instrument.
 * It dispatches only canonical actions and derives every musical statement from
 * the validated source/execution frame boundary.
 */
export function AccessibleInstrumentControls({ manifest, state, dispatch, onExecute }: {
  manifest: HistoricalManifest
  state: InstrumentState
  dispatch: (action: InstrumentAction) => void
  onExecute: () => void
}) {
  const [open,setOpen] = useState(false)
  const panelId = useId()
  const lectioRef = useRef<HTMLButtonElement>(null)
  const previousPhase = useRef(state.phase)
  const instance = state.carriers[0]
  const seated = instance?.location === 'workspace'
  const frame = seated
    ? state.execution
      ? getExecutedReadingFrame(manifest, state.execution, state.readingPosition)
      : getSourceReadingFrame(manifest, state.readingPosition)
    : null

  // Preserve the operator's place across the same LECTIO control changing its
  // label/availability through executing → error/retry.
  useEffect(() => {
    const previous = previousPhase.current
    if (
      (previous === 'carrier_seated' && state.phase === 'executing') ||
      (previous === 'executing' && state.phase === 'error') ||
      (previous === 'error' && state.phase === 'executing')
    ) {
      lectioRef.current?.focus()
    }
    previousPhase.current = state.phase
  }, [state.phase])

  const canRead = isReadingReady(state, manifest)
  const lectioLabel = state.phase === 'executing'
    ? 'Reading…'
    : state.phase === 'error'
      ? 'Retry LECTIO · Read the fragment'
      : 'LECTIO · Read the fragment'

  return <div className="spatial-controls" data-open={open}>
    <button
      className="spatial-controls__toggle"
      aria-expanded={open}
      aria-controls={panelId}
      onClick={() => setOpen(!open)}
    >Instrument controls</button>

    <div id={panelId} className="spatial-controls__panel" hidden={!open}>
      <p>These controls operate the same canonical instrument.</p>
      <ArcaCabinet manifest={manifest} state={state} dispatch={dispatch} />

      {instance && <section aria-label="Critical-edition semantic reading">
        <p>Carrier location: {instance.location}.</p>
        <ColumnRod carrier={manifest.critical_edition_carrier} instance={instance} />

        {state.heldCarrierId && <button
          onClick={() => dispatch({type:'PLACE_HELD_CARRIER'})}
        >Seat the carrier at the event-reading station</button>}

        {seated && <>
          <fieldset>
            <legend>Event reader · canonical positions 1–6</legend>
            {Array.from({length:6},(_,position) => (
              <button
                key={position}
                type="button"
                aria-pressed={state.readingPosition === position}
                onClick={() => dispatch({type:'SET_READING_POSITION',position})}
              >Event {position+1} of 6</button>
            ))}
          </fieldset>
          {frame && <p role="status" aria-live="polite" aria-atomic="true">
            {eventAnnouncement(frame)}
          </p>}
        </>}

        <button
          ref={lectioRef}
          disabled={state.phase === 'executing' || !canRead}
          onClick={onExecute}
        >{lectioLabel}</button>

        {state.phase === 'revealed' && <button
          onClick={() => dispatch({type:'RETURN_TO_WORKING'})}
        >Return to the carrier</button>}
      </section>}

      <section aria-label="Historical limits">
        <h3>Historical non-claims</h3>
        <ul>{manifest.limits.map(limit => <li key={limit}>{limit}</li>)}</ul>
        <button type="button" onClick={() => dispatch({type:'TOGGLE_PROVENANCE'})}>
          Inspect provenance and non-claims
        </button>
      </section>

      <p>
        p51 (printed p.51) Tone-II witness · H0 witness; H1 fixed operating policy.
      </p>
    </div>
  </div>
}
