import { fireEvent, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { expect, it } from 'vitest'
import { AccessibleInstrumentControls } from './AccessibleInstrumentControls'
import { createInitialState, instrumentReducer } from '../instrument/model'
import type { InstrumentAction } from '../instrument/types'
import { manifestFixture } from '../test/fixtures'
it('operates the same reducer through distinct retrieval, placement and inspection',async () => {
  let state=createInitialState()
  const dispatch=(action:InstrumentAction) => { state=instrumentReducer(state,action,manifestFixture);rerender(ui()) }
  const ui=() => <AccessibleInstrumentControls manifest={manifestFixture} state={state} dispatch={dispatch} onExecute={() => dispatch({type:'EXECUTE'})} />
  const {rerender}=render(ui())
  const user=userEvent.setup()
  expect(screen.getByRole('button',{name:'Instrument controls'})).toHaveAttribute('aria-expanded','false')
  await user.click(screen.getByRole('button',{name:'Instrument controls'}))
  for(const name of ['Open the Arca',/DODECAMORIVM/,/Open Cell IV/,/Lift.*critical-edition carrier/i]) await user.click(screen.getByRole('button',{name}))
  const id=state.heldCarrierId
  expect(state.carriers).toHaveLength(1)
  expect(state.carriers[0].location).toBe('hand')
  expect(screen.getByRole('button',{name:/LECTIO/})).toBeDisabled()
  await user.click(screen.getByRole('button',{name:/Seat the carrier/i}))
  expect(state.carriers[0].instance_id).toBe(id)
  fireEvent.change(screen.getByRole('slider'),{target:{value:'5'}})
  expect(state.readingPosition).toBe(5)
  expect(screen.getByRole('slider')).toHaveAttribute('aria-valuetext','Event 6 of 6')
  expect(screen.queryByRole('button',{name:/engage tone/i})).not.toBeInTheDocument()
  await user.click(screen.getByRole('button',{name:/LECTIO/}))
  expect(state.phase).toBe('executing')
  expect(Object.keys(state)).not.toContain('camera')
})
