import { lazy, Suspense, useEffect, useReducer, useRef, useState } from 'react'
import { ArcaCabinet } from './components/ArcaCabinet'
import { WorkingRule } from './components/WorkingRule'
import { VoiceManifestation } from './components/VoiceManifestation'
import { ProvenanceLeaf } from './components/ProvenanceLeaf'
import { Scholium } from './components/Scholium'
import { AccessibleInstrumentControls } from './spatial/AccessibleInstrumentControls'
import { executeHistoricalReading, loadHistoricalManifest } from './instrument/client'
import { createInitialState, createReadingRequest, deriveInstrumentView, getNextAffordance, instrumentReducer, isReadingReady } from './instrument/model'
import type { HistoricalManifest, InstrumentAction, InstrumentState } from './instrument/types'
import { resolveRenderer, supportsWebGL } from './renderer'
import { getRealmGuidance } from './realms/guidance'
import { DEFAULT_REALM_ID, getRealmDefinition } from './realms/registry'
const SpatialArca = lazy(() => import('./spatial/SpatialArca').then(m => ({default:m.SpatialArca})))

export default function App() {
  const [manifest,setManifest] = useState<HistoricalManifest>()
  const [manifestError,setManifestError] = useState<string>()
  const [renderer] = useState(() => supportsWebGL() ? resolveRenderer() : 'legacy')
  const [state,dispatch] = useReducer((s:InstrumentState,a:InstrumentAction) => instrumentReducer(s,a,manifest),undefined,() => createInitialState())
  const pending = useRef<AbortController | null>(null)
  useEffect(() => {
    const controller = new AbortController()
    loadHistoricalManifest(controller.signal).then(m => { if(!controller.signal.aborted) setManifest(m) })
      .catch((e:unknown) => { if(!controller.signal.aborted) setManifestError(e instanceof Error ? e.message : 'Source ledger unavailable.') })
    return () => { controller.abort(); pending.current?.abort() }
  },[])
  useEffect(() => {
    const query = window.matchMedia('(prefers-reduced-motion: reduce)')
    const sync = () => dispatch({type:'SET_REDUCED_MOTION',value:query.matches})
    sync(); query.addEventListener('change',sync)
    return () => query.removeEventListener('change',sync)
  },[])
  const act = (action:InstrumentAction) => {
    if(action.type === 'CLOSE_ARCA') { pending.current?.abort(); pending.current=null }
    dispatch(action)
  }
  const execute = async () => {
    if (!manifest || !isReadingReady(state,manifest) || pending.current) return
    const controller=new AbortController()
    pending.current=controller
    const request=createReadingRequest(state,manifest)
    dispatch({type:'EXECUTE'})
    try {
      const execution=await executeHistoricalReading(request,controller.signal)
      if(!controller.signal.aborted) dispatch({type:'EXECUTION_SUCCESS',execution})
    } catch(e) {
      if(!controller.signal.aborted) dispatch({type:'EXECUTION_ERROR',message:e instanceof Error ? e.message : 'Reading rejected.'})
    } finally { if(pending.current===controller) pending.current=null }
  }
  if(manifestError) return <main className="loading-folio" role="alert">{manifestError}</main>
  if(!manifest) return <main className="loading-folio" aria-live="polite">Opening the source ledger…</main>
  const view=deriveInstrumentView(state), nextAffordance=getNextAffordance(state,manifest)
  const realm=getRealmDefinition(DEFAULT_REALM_ID)
  const guidance=getRealmGuidance(realm.id,nextAffordance,'scholia')
  return <main className={'instrument-shell'+(renderer==='spatial'?' instrument-shell--spatial':'')}
    data-renderer={renderer} data-realm={realm.id} data-phase={state.phase} data-view={view}
    data-next-affordance={nextAffordance} data-guidance-mode="scholia" data-realm-guidance={guidance?.affordance}
    data-reduced-motion={state.reducedMotion}>
    {renderer==='spatial' ? <>
      <Suspense fallback={<p>Setting the instrument on the desk…</p>}>
        <SpatialArca manifest={manifest} state={state} view={view} nextAffordance={nextAffordance}
          executionReady={isReadingReady(state,manifest)}
          onOpen={() => act({type:'OPEN_ARCA'})} onClose={() => act({type:'CLOSE_ARCA'})}
          onFocusBank={bank => act({type:'FOCUS_BANK',bank})} onFocusCell={cell => act({type:'FOCUS_CELL',cell})}
          onRetrieveCarrier={() => act({type:'RETRIEVE_CARRIER'})} onPlaceCarrier={() => act({type:'PLACE_HELD_CARRIER'})}
          onReadingPosition={position => act({type:'SET_READING_POSITION',position})} onExecute={execute} />
      </Suspense>
      <AccessibleInstrumentControls manifest={manifest} state={state} dispatch={act} onExecute={execute} />
    </> : <div className="arca-machine" data-view={view} data-phase={state.phase}>
      <span className="carcass-stile carcass-stile--left" aria-hidden="true" />
      <span className="carcass-stile carcass-stile--right" aria-hidden="true" />
      <header className="instrument-masthead"><h1>Neo-Arca Musarithmica</h1></header>
      <div className="arca-machine__column">
        <ArcaCabinet manifest={manifest} state={state} dispatch={act} />
        {state.carriers.length > 0 && <WorkingRule manifest={manifest} state={state} dispatch={act} onExecute={execute} />}
        {state.phase==='revealed' && state.execution && <VoiceManifestation execution={state.execution} onReturn={() => act({type:'RETURN_TO_WORKING'})} />}
      </div>
    </div>}
    <Scholium text={guidance?.text ?? null} place="cornice" />
    {state.error && <p className="instrument-error" role="alert">{state.error}</p>}
    <ProvenanceLeaf manifest={manifest} execution={state.execution} open={state.provenanceOpen} onToggle={() => act({type:'TOGGLE_PROVENANCE'})} />
  </main>
}
