import { render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import App from './App'
import { getRealmGuidance } from './realms/guidance'
import { executionFixture, manifestFixture } from './test/fixtures'

const matchMedia = (matches: boolean) => ({
  matches,
  media: '(prefers-reduced-motion: reduce)',
  onchange: null,
  addEventListener: vi.fn(),
  removeEventListener: vi.fn(),
  addListener: vi.fn(),
  removeListener: vi.fn(),
  dispatchEvent: vi.fn(),
})

function stubKernel() {
  const fetchMock = vi.fn()
    .mockResolvedValueOnce(new Response(JSON.stringify(manifestFixture), { status: 200 }))
    .mockResolvedValue(new Response(JSON.stringify(executionFixture), { status: 200 }))
  vi.stubGlobal('fetch', fetchMock)
  return fetchMock
}

const openToCell = async (user: ReturnType<typeof userEvent.setup>) => {
  await user.click(await screen.findByRole('button', { name: 'Open the Arca' }))
  await user.click(screen.getByRole('button', { name: /DODECAMORIVM/ }))
  await user.click(screen.getByRole('button', { name: 'Open Cell IV, verified Pinax IV family' }))
}

const deployAll = async (user: ReturnType<typeof userEvent.setup>) => {
  for (const template of manifestFixture.rod_templates) {
    await user.click(screen.getByRole('button', { name: `Deploy ${template.label} to the transverse rule` }))
  }
}

describe('M1.1 reliquary presentation', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
    Object.defineProperty(window, 'matchMedia', { writable: true, value: vi.fn(() => matchMedia(false)) })
  })

  it('renders the scholium the realm derives for the current canonical affordance', async () => {
    stubKernel()
    const user = userEvent.setup()
    render(<App />)

    // Dormant: the note beside the closed cabinet is exactly the realm's text.
    const dormant = getRealmGuidance('historica', 'open_arca', 'scholia')
    expect(await screen.findByText(dormant!.text)).toBeInTheDocument()

    await user.click(screen.getByRole('button', { name: 'Open the Arca' }))
    const atBank = getRealmGuidance('historica', 'focus_bank_i', 'scholia')
    expect(screen.getByText(atBank!.text)).toBeInTheDocument()
    expect(screen.queryByText(dormant!.text)).not.toBeInTheDocument()

    // Exactly one scholium is ever on the instrument at a time.
    await user.click(screen.getByRole('button', { name: /DODECAMORIVM/ }))
    const atCell = getRealmGuidance('historica', 'open_cell_iv', 'scholia')
    expect(screen.getAllByText(atCell!.text)).toHaveLength(1)
  })

  it('leaves the empty socket in Cell IV when a carrier is lifted out', async () => {
    stubKernel()
    const user = userEvent.setup()
    render(<App />)
    await openToCell(user)

    const [first] = manifestFixture.rod_templates
    const cell = screen.getByLabelText('Cell IV rod receptacle')
    expect(within(cell).getAllByRole('button', { name: /^Deploy .+ to the transverse rule$/ })).toHaveLength(3)

    await user.click(screen.getByRole('button', { name: `Deploy ${first.label} to the transverse rule` }))

    // The carrier is gone from the cell, but its socket is still there and
    // still says which carrier came out of it.
    expect(
      screen.queryByRole('button', { name: `Deploy ${first.label} to the transverse rule` }),
    ).not.toBeInTheDocument()
    expect(
      within(cell).getByLabelText(`${first.label} has been removed from Cell IV`),
    ).toBeInTheDocument()
    expect(within(cell).getAllByRole('button', { name: /^Deploy .+ to the transverse rule$/ })).toHaveLength(2)
  })

  it('keeps the cell at full size while a carrier is still there to lift', async () => {
    stubKernel()
    const user = userEvent.setup()
    const { container } = render(<App />)
    await openToCell(user)

    const [first, ...rest] = manifestFixture.rod_templates
    await user.click(screen.getByRole('button', { name: `Deploy ${first.label} to the transverse rule` }))
    expect(container.querySelector('.machine-interior')).toHaveAttribute('data-focus', 'near')

    for (const template of rest) {
      await user.click(screen.getByRole('button', { name: `Deploy ${template.label} to the transverse rule` }))
    }
    expect(container.querySelector('.machine-interior')).toHaveAttribute('data-focus', 'receded')
  })

  it('reports an untranscribed band as unavailable and refuses to read across it', async () => {
    stubKernel()
    const user = userEvent.setup()
    render(<App />)
    await openToCell(user)
    await deployAll(user)

    const rods = screen.getAllByRole('slider')
    for (const rod of rods) { rod.focus(); await user.keyboard('{Home}') }
    expect(screen.getByRole('button', { name: 'Engage Tone II Hypodorius' })).toBeEnabled()

    // Move one rod onto a band the sources do not transcribe. The reading must
    // break, and the Tone must refuse to engage on a broken reading.
    rods[0].focus()
    await user.keyboard('{ArrowDown}')
    expect(rods[0]).toHaveAttribute('aria-valuetext', 'Band 2 · sealed')
    expect(screen.getByRole('button', { name: 'Engage Tone II Hypodorius' })).toBeDisabled()
    expect(screen.getByRole('button', { name: 'Read the transverse' })).toBeDisabled()
    expect(screen.getByText(/LECTIO INTERRUPTA/)).toBeInTheDocument()
  })

  it('drives the whole instrument from the keyboard alone', async () => {
    stubKernel()
    const user = userEvent.setup()
    render(<App />)

    const press = async (name: RegExp | string) => {
      const button = screen.getByRole('button', { name })
      button.focus()
      expect(button).toHaveFocus()
      await user.keyboard('{Enter}')
    }

    await screen.findByRole('button', { name: 'Open the Arca' })
    await press('Open the Arca')
    await press(/DODECAMORIVM/)
    await press('Open Cell IV, verified Pinax IV family')
    for (const template of manifestFixture.rod_templates) {
      await press(`Deploy ${template.label} to the transverse rule`)
    }
    for (const rod of screen.getAllByRole('slider')) { rod.focus(); await user.keyboard('{Home}') }
    await press('Engage Tone II Hypodorius')
    await press('Read the transverse')

    expect(await screen.findByText('Four voices manifest')).toBeInTheDocument()
  })

  it('keeps the aligned mechanism on screen while the folio is read', async () => {
    stubKernel()
    const user = userEvent.setup()
    const { container } = render(<App />)
    await openToCell(user)
    await deployAll(user)
    for (const rod of screen.getAllByRole('slider')) { rod.focus(); await user.keyboard('{Home}') }
    await user.click(screen.getByRole('button', { name: 'Engage Tone II Hypodorius' }))
    await user.click(screen.getByRole('button', { name: 'Read the transverse' }))
    await screen.findByText('Four voices manifest')

    // The revelation is printed BY the carriage, so the rods that produced it
    // are still standing on the rule underneath the sheet.
    expect(container.querySelector('[data-view="revelation"]')).toBeInTheDocument()
    expect(screen.getAllByRole('slider')).toHaveLength(3)
    expect(screen.getByLabelText('Transverse reading carriage')).toBeInTheDocument()
    // ...and the carriage heading still belongs only to the working view.
    expect(screen.queryByRole('heading', { name: 'Lectio transversa' })).not.toBeInTheDocument()
  })

  it('sends the same alignment to the kernel however the instrument is presented', async () => {
    const fetchMock = stubKernel()
    const user = userEvent.setup()
    render(<App />)
    await openToCell(user)
    await deployAll(user)
    for (const rod of screen.getAllByRole('slider')) { rod.focus(); await user.keyboard('{Home}') }
    await user.click(screen.getByRole('button', { name: 'Engage Tone II Hypodorius' }))
    await user.click(screen.getByRole('button', { name: 'Read the transverse' }))
    await screen.findByText('Four voices manifest')

    const [url, init] = fetchMock.mock.calls[1]
    expect(url).toBe('/api/historica/execute')
    const body = JSON.parse(String((init as RequestInit).body))
    expect(body.format).toBe('neo-arca-mechanica-alignment/v1')
    expect(body.read_band).toBe(manifestFixture.canonical_read_band)
    expect(body.tone).toEqual({ number: 2, engaged: true })
    expect(body.rod_instances.map((rod: { template_id: string }) => rod.template_id))
      .toEqual(manifestFixture.required_template_ids)
    expect(body.rod_instances.every((rod: { vertical_offset: number }) => rod.vertical_offset === 0)).toBe(true)
    // Nothing the presentation layer added leaks into the historical request.
    expect(Object.keys(body).sort()).toEqual(['format', 'read_band', 'rod_instances', 'tone'])
  })

  it('stays in the Historica realm and exposes no realm switcher', async () => {
    stubKernel()
    const user = userEvent.setup()
    const { container } = render(<App />)
    await user.click(await screen.findByRole('button', { name: 'Open the Arca' }))

    expect(container.querySelector('.instrument-shell')).toHaveAttribute('data-realm', 'historica')
    for (const name of [/neo-arca/i, /haeretic/i, /switch realm/i]) {
      expect(screen.queryByRole('button', { name })).not.toBeInTheDocument()
    }
  })
})
