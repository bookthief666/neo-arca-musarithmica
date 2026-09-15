import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { AccessibleInstrumentControls } from './AccessibleInstrumentControls'
import {
  createInitialState, getNextAffordance, instrumentReducer, isAlignmentReady,
  MAX_VERTICAL_OFFSET,
} from '../instrument/model'
import type { InstrumentAction, InstrumentState } from '../instrument/types'
import { manifestFixture } from '../test/fixtures'

/**
 * The semantic layer is the instrument for anyone who cannot use a canvas. It
 * must therefore drive the SAME machine — not a parallel one — so these tests
 * check that its controls produce canonical actions and that replaying those
 * actions through the real reducer moves the real instrument.
 */
function harness(state: InstrumentState, dispatch: (action: InstrumentAction) => void) {
  const alignmentReady = isAlignmentReady(state, manifestFixture)
  return (
    <AccessibleInstrumentControls
      manifest={manifestFixture}
      state={state}
      nextAffordance={getNextAffordance(state, manifestFixture)}
      alignmentReady={alignmentReady}
      executionReady={alignmentReady && state.toneEngaged}
      onOpen={() => dispatch({ type: 'OPEN_ARCA' })}
      onClose={() => dispatch({ type: 'CLOSE_ARCA' })}
      onFocusBank={(bank) => dispatch({ type: 'FOCUS_BANK', bank })}
      onFocusCell={(cell) => dispatch({ type: 'FOCUS_CELL', cell })}
      onRetrieveRod={(id) => {
        const template = manifestFixture.rod_templates.find((t) => t.template_id === id)
        if (template) dispatch({ type: 'RETRIEVE_ROD', template })
      }}
      onPlaceHeldRod={() => dispatch({ type: 'PLACE_HELD_ROD' })}
      onMoveRod={(instanceId, offset) => dispatch({ type: 'MOVE_ROD', instanceId, offset })}
      onEngageTone={() => dispatch({ type: 'ENGAGE_TONE' })}
      onExecute={() => dispatch({ type: 'EXECUTE' })}
      onReturn={() => dispatch({ type: 'RETURN_TO_WORKING' })}
    />
  )
}

const open = async (user: ReturnType<typeof userEvent.setup>) =>
  user.click(screen.getByRole('button', { name: 'Instrument controls' }))

describe('the semantic instrument', () => {
  it('is present and discreet, and opens into the tab order', async () => {
    const user = userEvent.setup()
    render(harness(createInitialState(), vi.fn()))
    const toggle = screen.getByRole('button', { name: 'Instrument controls' })
    expect(toggle).toHaveAttribute('aria-expanded', 'false')
    await open(user)
    expect(toggle).toHaveAttribute('aria-expanded', 'true')
    expect(screen.getByRole('button', { name: 'Open the Arca' })).toBeInTheDocument()
  })

  it('dispatches the canonical OPEN_ARCA action, not a renderer-local one', async () => {
    const user = userEvent.setup()
    const dispatch = vi.fn()
    render(harness(createInitialState(), dispatch))
    await open(user)
    await user.click(screen.getByRole('button', { name: 'Open the Arca' }))
    expect(dispatch).toHaveBeenCalledWith({ type: 'OPEN_ARCA' })
  })

  it('drives the real reducer all the way to a ready alignment', async () => {
    const user = userEvent.setup()
    let state = createInitialState()
    const dispatch = (action: InstrumentAction) => {
      state = instrumentReducer(state, action, manifestFixture)
      rerender(harness(state, dispatch))
    }
    const { rerender } = render(harness(state, dispatch))

    await open(user)
    await user.click(screen.getByRole('button', { name: 'Open the Arca' }))
    expect(state.phase).toBe('open')
    await user.click(screen.getByRole('button', { name: 'Bank I, DODECAMORIVM' }))
    await user.click(screen.getByRole('button', { name: /Open Cell IV/ }))
    expect(state.focusedCell).toBe(4)

    for (const template of manifestFixture.rod_templates) {
      await user.click(screen.getByRole('button', { name: `Lift ${template.label} from Cell IV` }))
      // The carrier is in the hand, not yet on the rule: the semantic surface
      // must say so, and must not offer another lift while it is held.
      expect(state.heldRodId).toBe(`rod-${template.template_id}`)
      expect(state.rods.find((rod) => rod.template_id === template.template_id)?.location).toBe('hand')
      for (const other of manifestFixture.rod_templates) {
        const lift = screen.queryByRole('button', { name: `Lift ${other.label} from Cell IV` })
        if (lift) expect(lift).toBeDisabled()
      }
      await user.click(screen.getByRole('button', { name: new RegExp(`Seat held virga, ${template.label}`) }))
      expect(state.heldRodId).toBeNull()
    }
    // Exactly three carriers exist, each once: a transfer must not clone.
    expect(state.rods).toHaveLength(3)
    expect(new Set(state.rods.map((r) => r.instance_id)).size).toBe(3)
    expect(state.rods.every((rod) => rod.location === 'workspace')).toBe(true)

    for (const slider of screen.getAllByRole('slider')) {
      slider.focus()
      await user.keyboard('{Home}')
    }
    expect(state.rods.every((rod) => rod.vertical_offset === 0)).toBe(true)
    expect(isAlignmentReady(state, manifestFixture)).toBe(true)

    await user.click(screen.getByRole('button', { name: /^Engage Tone II/ }))
    expect(state.toneEngaged).toBe(true)
  })

  it('never lets a band offset leave the canonical range', async () => {
    const user = userEvent.setup()
    let state = createInitialState()
    const dispatch = (action: InstrumentAction) => {
      state = instrumentReducer(state, action, manifestFixture)
      rerender(harness(state, dispatch))
    }
    const { rerender } = render(harness(state, dispatch))
    await open(user)
    await user.click(screen.getByRole('button', { name: 'Open the Arca' }))
    await user.click(screen.getByRole('button', { name: 'Bank I, DODECAMORIVM' }))
    await user.click(screen.getByRole('button', { name: /Open Cell IV/ }))
    await user.click(screen.getByRole('button', {
      name: `Lift ${manifestFixture.rod_templates[0].label} from Cell IV`,
    }))
    await user.click(screen.getByRole('button', {
      name: new RegExp(`Seat held virga, ${manifestFixture.rod_templates[0].label}`),
    }))

    const slider = screen.getAllByRole('slider')[0]
    slider.focus()
    for (let i = 0; i < 25; i++) await user.keyboard('{ArrowDown}')
    expect(state.rods[0].vertical_offset).toBe(MAX_VERTICAL_OFFSET)
    for (let i = 0; i < 25; i++) await user.keyboard('{ArrowUp}')
    expect(state.rods[0].vertical_offset).toBe(0)
  })

  it('keeps no musical state of its own and adds no realm to the instrument', async () => {
    const user = userEvent.setup()
    let state = createInitialState()
    const dispatch = (action: InstrumentAction) => {
      state = instrumentReducer(state, action, manifestFixture)
      rerender(harness(state, dispatch))
    }
    const { rerender } = render(harness(state, dispatch))
    await open(user)
    await user.click(screen.getByRole('button', { name: 'Open the Arca' }))

    expect(Object.keys(state).sort()).toEqual([
      'error', 'execution', 'focusedBank', 'focusedCell', 'heldRodId',
      'phase', 'provenanceOpen', 'reducedMotion', 'rods', 'toneEngaged',
    ])
    expect(JSON.stringify(state)).not.toMatch(/historica|realm|camera|spatial/i)
  })

  it('reports each band as verified or not transcribed for a screen reader', async () => {
    const user = userEvent.setup()
    let state = createInitialState()
    const dispatch = (action: InstrumentAction) => {
      state = instrumentReducer(state, action, manifestFixture)
      rerender(harness(state, dispatch))
    }
    const { rerender } = render(harness(state, dispatch))
    await open(user)
    await user.click(screen.getByRole('button', { name: 'Open the Arca' }))
    await user.click(screen.getByRole('button', { name: 'Bank I, DODECAMORIVM' }))
    await user.click(screen.getByRole('button', { name: /Open Cell IV/ }))
    await user.click(screen.getByRole('button', {
      name: `Lift ${manifestFixture.rod_templates[0].label} from Cell IV`,
    }))
    await user.click(screen.getByRole('button', {
      name: new RegExp(`Seat held virga, ${manifestFixture.rod_templates[0].label}`),
    }))

    const slider = screen.getAllByRole('slider')[0]
    slider.focus()
    await user.keyboard('{Home}')
    expect(slider).toHaveAttribute('aria-valuetext', 'Stropha I · Vperm 01')
    expect(screen.getByText('verified')).toBeInTheDocument()
    await user.keyboard('{ArrowDown}')
    expect(slider).toHaveAttribute('aria-valuetext', 'Band 2 · sealed')
    expect(screen.getByText('not transcribed')).toBeInTheDocument()
  })
})
