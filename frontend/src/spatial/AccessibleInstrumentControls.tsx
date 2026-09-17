import { useId, useState } from 'react'
import type { HistoricalManifest, InstrumentState, InstrumentAction } from '../instrument/types'
import { ArcaCabinet } from '../components/ArcaCabinet'
import { WorkingRule } from '../components/WorkingRule'
export function AccessibleInstrumentControls({ manifest, state, dispatch, onExecute }: {
  manifest: HistoricalManifest; state: InstrumentState; dispatch: (action: InstrumentAction) => void; onExecute: () => void
}) {
  const [open,setOpen] = useState(false)
  const panelId = useId()
  return <div className="spatial-controls" data-open={open}>
    <button className="spatial-controls__toggle" aria-expanded={open} aria-controls={panelId} onClick={() => setOpen(!open)}>Instrument controls</button>
    <div id={panelId} className="spatial-controls__panel" hidden={!open}>
      <p>These controls operate the same canonical instrument.</p>
      <ArcaCabinet manifest={manifest} state={state} dispatch={dispatch} />
      {state.carriers.length > 0 && <WorkingRule manifest={manifest} state={state} dispatch={dispatch} onExecute={onExecute} />}
      {state.phase === 'revealed' && <button onClick={() => dispatch({type:'RETURN_TO_WORKING'})}>Return to the carrier</button>}
    </div>
  </div>
}
