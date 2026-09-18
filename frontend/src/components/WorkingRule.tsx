import type { HistoricalManifest, InstrumentState, InstrumentAction } from '../instrument/types'
import { isReadingReady } from '../instrument/model'
import { ColumnRod } from './ColumnRod'

export function WorkingRule({ manifest, state, dispatch, onExecute }: {
  manifest: HistoricalManifest; state: InstrumentState; dispatch: (action: InstrumentAction) => void; onExecute: () => void
}) {
  const instance = state.carriers[0]
  const carrier = manifest.critical_edition_carrier

  return <section className="working-rule" aria-label="Critical-edition reading carriage">
    <h2>Critical-edition reading</h2>
    {instance && <>
      <p className="working-rule__authority">
        {carrier.classification} critical-edition carrier · edition {instance.edition_id}
        {' '}· Vperm 01 and Rperm 03 source content · fixed p.51 Tone II witness
      </p>
      <ColumnRod carrier={carrier} instance={instance} />
    </>}
    {state.heldCarrierId && <button onClick={() => dispatch({type:'PLACE_HELD_CARRIER'})}>Seat the carrier in the carriage</button>}
    {instance?.location === 'workspace' && <label>Event reader
      <input type="range" min={0} max={5} step={1} value={state.readingPosition}
        aria-label="Event reader" aria-valuetext={'Event '+(state.readingPosition+1)+' of 6'}
        onChange={e => dispatch({type:'SET_READING_POSITION',position:Number(e.target.value)})} />
    </label>}
    <button disabled={!isReadingReady(state,manifest)} onClick={onExecute}>
      {state.phase === 'executing' ? 'Reading…' : 'LECTIO · Read the fragment'}
    </button>
  </section>
}
