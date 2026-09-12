import { useCallback, useEffect, useLayoutEffect, useMemo, useReducer, useRef, useState } from 'react'
import { ArcaCabinet } from './components/ArcaCabinet'
import { ProvenanceLeaf } from './components/ProvenanceLeaf'
import { VoiceManifestation } from './components/VoiceManifestation'
import { WorkingRule } from './components/WorkingRule'
import { executeHistoricalAlignment, loadHistoricalManifest } from './instrument/client'
import {
  createAlignmentRequest,
  createInitialState,
  deriveInstrumentView,
  getNextAffordance,
  instrumentReducer,
  isAlignmentReady,
} from './instrument/model'
import type {
  HistoricalManifest,
  InstrumentAction,
  InstrumentState,
  RodTemplate,
} from './instrument/types'
import { getRealmGuidance } from './realms/guidance'
import { DEFAULT_REALM_ID, getRealmDefinition } from './realms/registry'
import type { GuidanceMode } from './realms/types'

const GUIDANCE_MODE: GuidanceMode = 'scholia'

interface RodTransfer {
  origin: { top: number; left: number; width: number; height: number }
  kind: 'pitch' | 'rhythm'
  copy: number
  key: number
}

/**
 * The flying carrier: a short, literal statement that THIS rod came OUT of
 * Cell IV and travelled to the rule. It carries no state and never blocks the
 * reducer — the rod is already seated in the rail behind it.
 */
function TransferGhost({ transfer, railRef, onDone }: {
  transfer: RodTransfer
  railRef: React.RefObject<HTMLDivElement | null>
  onDone: () => void
}) {
  const ghostRef = useRef<HTMLDivElement>(null)

  useLayoutEffect(() => {
    const node = ghostRef.current
    const rail = railRef.current
    if (!node) { onDone(); return }
    if (!rail || typeof node.animate !== 'function') { onDone(); return }
    const target = rail.getBoundingClientRect()
    const dx = target.left + target.width / 2 - (transfer.origin.left + transfer.origin.width / 2)
    const dy = target.top + target.height * 0.42 - (transfer.origin.top + transfer.origin.height / 2)
    const animation = node.animate(
      [
        { transform: 'translate3d(0,0,0) rotate(0deg)', opacity: 1 },
        { transform: `translate3d(${dx * 0.45}px, ${dy * 0.28 - 46}px, 0) rotate(-5deg)`, opacity: 1, offset: 0.45 },
        { transform: `translate3d(${dx}px, ${dy}px, 0) rotate(0deg)`, opacity: 0.12 },
      ],
      { duration: 430, easing: 'cubic-bezier(0.32, 0.08, 0.24, 1)', fill: 'forwards' },
    )
    const finish = () => onDone()
    animation.addEventListener('finish', finish)
    animation.addEventListener('cancel', finish)
    return () => {
      animation.removeEventListener('finish', finish)
      animation.removeEventListener('cancel', finish)
      animation.cancel()
    }
  }, [transfer, railRef, onDone])

  return (
    <div
      ref={ghostRef}
      className="transfer-ghost"
      data-kind={transfer.kind}
      aria-hidden="true"
      style={{
        top: transfer.origin.top,
        left: transfer.origin.left,
        width: transfer.origin.width,
        height: transfer.origin.height,
      }}
    >
      <span className="transfer-ghost__head" />
      <span className="transfer-ghost__shaft" />
    </div>
  )
}

export default function App() {
  const [manifest, setManifest] = useState<HistoricalManifest | null>(null)
  const [manifestError, setManifestError] = useState<string | null>(null)
  const [transfer, setTransfer] = useState<RodTransfer | null>(null)
  const railRef = useRef<HTMLDivElement>(null)
  const transferKey = useRef(0)

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
  const view = deriveInstrumentView(state)
  const nextAffordance = getNextAffordance(state, manifest ?? undefined)
  const realm = getRealmDefinition(DEFAULT_REALM_ID)
  const realmGuidance = getRealmGuidance(realm.id, nextAffordance, GUIDANCE_MODE)

  const deployRod = useCallback((template: RodTemplate, origin: DOMRect | null) => {
    if (origin && !state.reducedMotion) {
      transferKey.current += 1
      setTransfer({
        origin: { top: origin.top, left: origin.left, width: origin.width, height: origin.height },
        kind: template.source_column_id.includes('RPERM') ? 'rhythm' : 'pitch',
        copy: template.copy_index,
        key: transferKey.current,
      })
    }
    dispatch({ type: 'DEPLOY_ROD', template })
  }, [state.reducedMotion])

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

  // The carriage stays present once rods exist: semantic focus moves to the
  // Mensa, but the mechanism the reader just aligned must not be erased.
  const carriageMounted = view === 'working' || view === 'tone'

  return (
    <main
      className="instrument-shell"
      data-phase={state.phase}
      data-view={view}
      data-next-affordance={nextAffordance}
      data-reduced-motion={state.reducedMotion}
      data-realm={realm.id}
      data-guidance-mode={GUIDANCE_MODE}
      data-realm-guidance={realmGuidance?.affordance ?? 'none'}
    >
      <header className="instrument-masthead">
        <p className="instrument-masthead__line">
          <span className="instrument-masthead__title">Neo-Arca Musarithmica</span>
          <span className="instrument-masthead__sub">ARCA MECHANICA · PRIMVM INSTRVMENTVM</span>
        </p>
        <span className="authority-mark" aria-label="Historical authority: Pinax IV fragment, PRINT_1650, verified">
          <b>H0</b>
          <small>PINAX IV<br />PRINT_1650</small>
        </span>
      </header>

      <p className="visually-hidden" aria-live="polite">
        Current instrument state: {nextAffordance.replaceAll('_', ' ')}.
      </p>

      <div className="arca-machine" data-view={view} data-phase={state.phase}>
        <ArcaCabinet
          manifest={manifest}
          state={state}
          view={view}
          nextAffordance={nextAffordance}
          onOpen={() => dispatch({ type: 'OPEN_ARCA' })}
          onClose={() => dispatch({ type: 'CLOSE_ARCA' })}
          onFocusBank={(bank) => dispatch({ type: 'FOCUS_BANK', bank })}
          onFocusCell={(cell) => dispatch({ type: 'FOCUS_CELL', cell })}
          onDeployRod={deployRod}
          onEngageTone={() => dispatch({ type: 'ENGAGE_TONE' })}
        />

        {carriageMounted && (
          <WorkingRule
            ref={railRef}
            manifest={manifest}
            state={state}
            view={view}
            alignmentReady={alignmentReady}
            executionReady={alignmentReady && state.toneEngaged}
            nextAffordance={nextAffordance}
            onPlaceHeld={() => dispatch({ type: 'PLACE_HELD_ROD' })}
            onMoveRod={(instanceId, offset) => dispatch({ type: 'MOVE_ROD', instanceId, offset })}
            onExecute={execute}
          />
        )}

        {state.error && <p className="instrument-error" role="alert">{state.error}</p>}

        {view === 'revelation' && state.execution && (
          <VoiceManifestation
            execution={state.execution}
            onReturn={() => dispatch({ type: 'RETURN_TO_WORKING' })}
          />
        )}

        <ProvenanceLeaf
          manifest={manifest}
          execution={state.execution}
          open={state.provenanceOpen}
          onToggle={() => dispatch({ type: 'TOGGLE_PROVENANCE' })}
        />
      </div>

      {transfer && (
        <TransferGhost
          key={transfer.key}
          transfer={transfer}
          railRef={railRef}
          onDone={() => setTransfer(null)}
        />
      )}
    </main>
  )
}
