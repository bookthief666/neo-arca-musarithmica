import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, expect, it, vi } from 'vitest'
import App from './App'
import { getRealmGuidance } from './realms/guidance'
import { executionFixture, manifestFixture } from './test/fixtures'
beforeEach(() => {
  window.history.replaceState({}, '', '?renderer=legacy')
  vi.stubGlobal('matchMedia',vi.fn(() => ({matches:false,addEventListener:vi.fn(),removeEventListener:vi.fn()})))
  vi.stubGlobal('fetch',vi.fn().mockResolvedValueOnce(new Response(JSON.stringify(manifestFixture)))
    .mockResolvedValueOnce(new Response(JSON.stringify(executionFixture))))
})
it('derives one scholium and retains the empty socket and seated carrier',async () => {
  const user=userEvent.setup()
  const {container}=render(<App />)
  expect(await screen.findByText(getRealmGuidance('historica','open_arca','scholia')!.text)).toBeVisible()
  for (const name of ['Open the Arca',/DODECAMORIVM/,/Open Cell IV/,/Lift.*critical-edition carrier/i]) {
    const button=screen.getByRole('button',{name}); button.focus(); await user.keyboard('{Enter}')
  }
  expect(screen.getByLabelText('Critical-edition carrier removed from Cell IV')).toBeVisible()
  expect(container.querySelectorAll('.scholium')).toHaveLength(1)
  for(const name of [/Seat the carrier/i,/LECTIO/]) {
    screen.getByRole('button',{name}).focus(); await user.keyboard('{Enter}')
  }
  await screen.findByText('Four voices manifest')
  expect(screen.getByLabelText('Critical-edition reading carriage')).toBeVisible()
  expect(screen.getAllByRole('slider')).toHaveLength(1)
  expect(screen.queryByRole('button',{name:/engage tone/i})).not.toBeInTheDocument()
  expect(screen.queryByRole('slider',{name:/band/i})).not.toBeInTheDocument()
})
it('opens source witnesses without changing the mechanism',async () => {
  const user=userEvent.setup();render(<App />)
  await user.click(await screen.findByRole('button',{name:'Inspect witnesses'}))
  expect(screen.getByRole('dialog')).toHaveTextContent(manifestFixture.critical_edition_carrier.pitch_source.immutable_record)
  await user.keyboard('{Escape}')
  expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
})
