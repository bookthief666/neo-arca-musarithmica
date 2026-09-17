import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { expect, it } from 'vitest'
import { AccessibleInstrumentControls } from './AccessibleInstrumentControls'
import { createInitialState, instrumentReducer } from '../instrument/model'
import type { InstrumentAction } from '../instrument/types'
import { manifestFixture } from '../test/fixtures'

function semanticHarness() {
  let state = createInitialState()
  const rerenderRef: { current: ReturnType<typeof render>['rerender'] | null } = { current: null }
  const dispatch = (action: InstrumentAction) => {
    state = instrumentReducer(state, action, manifestFixture)
    rerenderRef.current?.(ui())
  }
  const ui = () => (
    <AccessibleInstrumentControls
      manifest={manifestFixture}
      state={state}
      dispatch={dispatch}
      onExecute={() => dispatch({ type: 'EXECUTE' })}
    />
  )
  const rendered = render(ui())
  rerenderRef.current = rendered.rerender
  return { user: userEvent.setup(), dispatch, getState: () => state }
}

async function seatCarrier(user: ReturnType<typeof userEvent.setup>) {
  await user.click(screen.getByRole('button', { name: 'Instrument controls' }))
  await user.click(screen.getByRole('button', { name: /open the arca/i }))
  await user.click(screen.getByRole('button', { name: /bank i/i }))
  await user.click(screen.getByRole('button', { name: /cell iv/i }))
  await user.click(screen.getByRole('button', { name: /lift.*critical-edition carrier/i }))
  await user.click(screen.getByRole('button', { name: /seat.*event-reading station/i }))
}

it('operates and explains one event without dead choices', async () => {
  const { user, getState } = semanticHarness()
  await seatCarrier(user)

  await user.click(screen.getByRole('button', { name: 'Event 6 of 6' }))
  expect(getState().readingPosition).toBe(5)
  expect(screen.getByRole('status')).toHaveTextContent(
    /event 6 of 6.*C 3 to B-flat.*A 7 to F-sharp.*T 5 to D.*B 3 to B-flat.*semibreve.*2 relative minim/i,
  )

  expect(screen.getByText(/VOCES · VPERM 01 · H0 SOURCE/)).toBeVisible()
  expect(screen.getByText(/NOTAE TEMPORIS · RPERM 03 · H0 SOURCE/)).toBeVisible()
  expect(screen.getByText(/DERIVED RELATIVE-MINIM NORMALIZATION · 1 1 1 1 2 2/)).toBeVisible()
  expect(screen.getByText(/p51.*H0 witness.*H1 fixed operating policy/i)).toBeVisible()
  expect(screen.getByText('8').closest('div')).toHaveTextContent(/8G/)

  expect(screen.queryByRole('slider', { name: /physical band/i })).not.toBeInTheDocument()
  expect(screen.queryByRole('button', { name: /engage tone/i })).not.toBeInTheDocument()
  expect(screen.getByRole('button', { name: /LECTIO/ })).toBeEnabled()
  expect(screen.getByRole('button', { name: /provenance and non-claims/i })).toBeVisible()
})

it('keeps the LECTIO control focused through execution failure and retry', async () => {
  const { user, dispatch, getState } = semanticHarness()
  await seatCarrier(user)

  const lectio = screen.getByRole('button', { name: /LECTIO/ })
  lectio.focus()
  await user.click(lectio)
  expect(getState().phase).toBe('executing')
  expect(screen.getByRole('button', { name: /Reading/ })).toHaveFocus()

  dispatch({ type: 'EXECUTION_ERROR', message: 'Deliberate parity failure.' })
  const retry = screen.getByRole('button', { name: /Retry LECTIO/ })
  expect(retry).toHaveFocus()
  await user.click(retry)
  expect(getState().phase).toBe('executing')
})
