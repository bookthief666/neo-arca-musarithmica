import { useEffect, useMemo, useReducer, useState } from 'react'
import { ArcaCabinet } from './components/ArcaCabinet'
import { ProvenanceLeaf } from './components/ProvenanceLeaf'
import { VoiceManifestation } from './components/VoiceManifestation'
import { WorkingRule } from './components/WorkingRule'
import { executeHistoricalAlignment, loadHistoricalManifest } from './instrument/client'
import {
  createAlignmentRequest,
  createInitialState,
  instrumentReducer,
  isAlignmentReady,
} from './instrument/model'
import type { HistoricalManifest, InstrumentAction, InstrumentState } from './instrument/types'

export default function App() {
  const [manifest, setManifest] = useState<HistoricalManifest | null>(null)
  const [manifestError, setManifestError] = useState<string | null>(null)
  const [state, dispatch] = useReducer(
    (current: InstrumentState, action: InstrumentAction) =>
      instrumentReducer(current, action, manifest ?? undefined),
    undefined,
    () => createInitialState(false),
  )

  useEffect(() => {
    let live = true
    loadHistoricalManifest()
      .then((value) => { if (live) setManifest(value) })
      .catch((error: unknown) => {
        if (live) setManifestError(error instanceof Error ? error.message : 'Historical manifest unavailable.')
      })
    return () => { live = false }
  }, [])

  useEffect(() => {
    const query = window.matchMedia('(prefers-reduced-motion: reduce)')
    const sync = () => dispatch({ type: 'SET_REDUCED_MOTION', value: query.matches })
    sync()
    query.addEventListener('change', sync)
    return () => query.removeEventListener('change', sync)
  }, [])

  const alignmentReady = useMemo(
    () => isAlignmentReady(state, manifest ?? undefined),
    [manifest, state],
  )

  const execute = async () => {
    if (!manifest || !alignmentReady || !state.toneEngaged) return
    dispatch({ type: 'EXECUTE' })
    const request = createAlignmentRequest(state, manifest)
    try {
      const execution = await executeHistoricalAlignment(request)
      dispatch({ type: 'EXECUTION_SUCCESS', execution })
    } catch (error) {
      dispatch({
        type: 'EXECUTION_ERROR',
        message: error instanceof Error ? error.message : 'The historical alignment was rejected.',
      })
    }
  }

  if (manifestError) {
    return (
      <main className="loading-folio loading-folio--error">
        <p>ARCA HISTORICA could not open its source ledger.</p>
        <pre>{manifestError}</pre>
      </main>
    )
  }

  if (!manifest) {
    return <main className="loading-folio" aria-live="polite">Opening the source ledger…</main>
  }

  return (
    <main className="instrument-shell" data-phase={state.phase} data-reduced-motion={state.reducedMotion}>
      <header className="instrument-masthead">
        <div>
          <p>ARCA MECHANICA · PRIMVM INSTRVMENTVM</p>
          <h1>Neo-Arca Musarithmica</h1>
        </div>
        <div className="authority-mark" aria-label="Historical authority status">
          <span>H0</span>
          <p>Pinax IV fragment<br /><small>PRINT_1650 · VERIFIED</small></p>
        </div>
      </header>

      <ArcaCabinet
        manifest={manifest}
        state={state}
        onOpen={() => dispatch({ type: 'OPEN_ARCA' })}
        onClose={() => dispatch({ type: 'CLOSE_ARCA' })}
        onFocusBank={(bank) => dispatch({ type: 'FOCUS_BANK', bank })}
        onFocusCell={(cell) => dispatch({ type: 'FOCUS_CELL', cell })}
        onRetrieveRod={(template) => dispatch({ type: 'RETRIEVE_ROD', template })}
        onEngageTone={() => dispatch({ type: 'ENGAGE_TONE' })}
      />

      {state.phase !== 'dormant' && (
        <WorkingRule
          manifest={manifest}
          state={state}
          alignmentReady={alignmentReady}
          executionReady={alignmentReady && state.toneEngaged}
          onPlaceHeld={() => dispatch({ type: 'PLACE_HELD_ROD' })}
          onMoveRod={(instanceId, offset) => dispatch({ type: 'MOVE_ROD', instanceId, offset })}
          onExecute={execute}
        />
      )}

      {state.error && <p className="instrument-error" role="alert">{state.error}</p>}
      {state.execution && <VoiceManifestation execution={state.execution} />}

      <ProvenanceLeaf
        manifest={manifest}
        execution={state.execution}
        open={state.provenanceOpen}
        onToggle={() => dispatch({ type: 'TOGGLE_PROVENANCE' })}
      />

      <footer className="instrument-footer">
        <p>HISTORICA DATA · H0</p>
        <p>PHYSICAL BODY · H1</p>
        <p>COMPUTATION · M0.9 KERNEL</p>
      </footer>
    </main>
  )
}
