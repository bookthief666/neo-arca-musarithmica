import type { HistoricalManifest, InstrumentState, InstrumentAction } from '../instrument/types'
import { ColumnRod } from './ColumnRod'
export function ArcaCabinet({ manifest, state, dispatch }: {
  manifest: HistoricalManifest; state: InstrumentState; dispatch: (action: InstrumentAction) => void
}) {
  const open = state.phase !== 'dormant'
  return <section className="arca-cabinet" aria-label="The cabinet">
    <button className="lid-latch" onClick={() => dispatch({type: open ? 'CLOSE_ARCA' : 'OPEN_ARCA'})}>
      {open ? 'Close the Arca' : 'Open the Arca'}
    </button>
    {open && <div className="machine-interior" data-focus={state.carriers.length ? 'receded' : 'near'}>
      <div className="mensa-tonographica" aria-label="Fixed Tone witness">
        <h2>Tone {manifest.tone.number} · {manifest.tone.name}</h2>
        <p>{manifest.tone.witness} · fixed edition policy</p>
        <dl>{Object.entries(manifest.tone.degree_to_pitch_class).map(([degree,pitch]) =>
          <div key={degree}><dt>{degree}</dt><dd>{pitch}</dd></div>)}</dl>
      </div>
      <button className="bank-plate" disabled={state.phase !== 'open'} onClick={() => dispatch({type:'FOCUS_BANK',bank:1})}>Bank I, DODECAMORIVM</button>
      {state.focusedBank === 1 && <button className="socket" disabled={state.phase !== 'bank_focus'}
        onClick={() => dispatch({type:'FOCUS_CELL',cell:manifest.cell.pinax})}>Open Cell IV, verified Pinax IV family</button>}
      {state.focusedCell === manifest.cell.pinax && <section className="carrier-receptacle" aria-label="Cell IV carrier receptacle">
        {state.carriers.length === 0 ? <>
          <ColumnRod carrier={manifest.critical_edition_carrier} />
          <button onClick={() => dispatch({type:'RETRIEVE_CARRIER'})}>Lift the critical-edition carrier</button>
        </> : <p className="carrier-slot__void" aria-label="Critical-edition carrier removed from Cell IV">Empty socket</p>}
      </section>}
    </div>}
  </section>
}
