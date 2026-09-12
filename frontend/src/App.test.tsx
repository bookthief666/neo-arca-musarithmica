import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import App from './App'
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

describe('Arca Mechanica interaction', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
    Object.defineProperty(window, 'matchMedia', { writable: true, value: vi.fn(() => matchMedia(false)) })
  })

  it('progressively reveals cabinet → cell → rods → Tone II → kernel without a two-step placement ritual', async () => {
    const fetchMock = vi.fn()
      .mockResolvedValueOnce(new Response(JSON.stringify(manifestFixture), { status: 200 }))
      .mockResolvedValueOnce(new Response(JSON.stringify(executionFixture), { status: 200 }))
    vi.stubGlobal('fetch', fetchMock)
    const user = userEvent.setup()
    const { container } = render(<App />)

    await user.click(await screen.findByRole('button', { name: 'Open the Arca' }))
    expect(container.querySelector('[data-view="cabinet"]')).toBeInTheDocument()
    expect(screen.queryByRole('heading', { name: 'Lectio transversa' })).not.toBeInTheDocument()

    await user.click(screen.getByRole('button', { name: /DODECAMORIVM/ }))
    await user.click(screen.getByRole('button', { name: 'Open Cell IV, verified Pinax IV family' }))
    expect(container.querySelector('[data-view="cell"]')).toBeInTheDocument()

    for (const template of manifestFixture.rod_templates) {
      await user.click(screen.getByRole('button', { name: `Deploy ${template.label} to the transverse rule` }))
    }

    expect(container.querySelector('[data-view="working"]')).toBeInTheDocument()
    const rods = screen.getAllByRole('slider', { name: /Use up and down arrow keys or drag vertically/ })
    expect(rods).toHaveLength(3)
    for (const rod of rods) {
      rod.focus()
      await user.keyboard('{Home}')
    }

    expect(container.querySelector('[data-view="tone"]')).toBeInTheDocument()
    expect(screen.queryByRole('heading', { name: 'Lectio transversa' })).not.toBeInTheDocument()
    await user.click(screen.getByRole('button', { name: 'Engage Tone II Hypodorius' }))

    expect(container.querySelector('[data-view="working"]')).toBeInTheDocument()
    const read = screen.getByRole('button', { name: 'Read the transverse' })
    expect(read).toBeEnabled()
    await user.click(read)

    expect(await screen.findByText('Four voices manifest')).toBeInTheDocument()
    expect(container.querySelector('[data-view="revelation"]')).toBeInTheDocument()
    expect(screen.queryByRole('heading', { name: 'Lectio transversa' })).not.toBeInTheDocument()
    expect(screen.getByRole('table', { name: 'Symbolic historical four-voice result' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Return to the rods' })).toBeInTheDocument()
    expect(fetchMock).toHaveBeenCalledTimes(2)
    const submitted = JSON.parse(String(fetchMock.mock.calls[1][1]?.body))
    expect(submitted.rod_instances.every((rod: { vertical_offset: number }) => rod.vertical_offset === 0)).toBe(true)
    expect(submitted.tone).toEqual({ number: 2, engaged: true })
  })

  it('returns from revelation to the same aligned mechanism without another kernel call', async () => {
    const fetchMock = vi.fn()
      .mockResolvedValueOnce(new Response(JSON.stringify(manifestFixture), { status: 200 }))
      .mockResolvedValueOnce(new Response(JSON.stringify(executionFixture), { status: 200 }))
    vi.stubGlobal('fetch', fetchMock)
    const user = userEvent.setup()
    render(<App />)

    await user.click(await screen.findByRole('button', { name: 'Open the Arca' }))
    await user.click(screen.getByRole('button', { name: /DODECAMORIVM/ }))
    await user.click(screen.getByRole('button', { name: 'Open Cell IV, verified Pinax IV family' }))
    for (const template of manifestFixture.rod_templates) {
      await user.click(screen.getByRole('button', { name: `Deploy ${template.label} to the transverse rule` }))
    }
    for (const rod of screen.getAllByRole('slider', { name: /Use up and down arrow keys or drag vertically/ })) {
      rod.focus()
      await user.keyboard('{Home}')
    }
    await user.click(screen.getByRole('button', { name: 'Engage Tone II Hypodorius' }))
    await user.click(screen.getByRole('button', { name: 'Read the transverse' }))
    await user.click(await screen.findByRole('button', { name: 'Return to the rods' }))

    expect(screen.getByRole('heading', { name: 'Lectio transversa' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Read the transverse' })).toBeEnabled()
    expect(fetchMock).toHaveBeenCalledTimes(2)
  })

  it('exposes Historica and derived scholia only at the presentation boundary', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response(JSON.stringify(manifestFixture), { status: 200 })))
    const user = userEvent.setup()
    const { container } = render(<App />)

    await screen.findByRole('button', { name: 'Open the Arca' })
    const shell = container.querySelector('.instrument-shell')
    expect(shell).toHaveAttribute('data-realm', 'historica')
    expect(shell).toHaveAttribute('data-guidance-mode', 'scholia')
    expect(shell).toHaveAttribute('data-realm-guidance', 'open_arca')

    await user.click(screen.getByRole('button', { name: 'Open the Arca' }))
    expect(shell).toHaveAttribute('data-realm-guidance', 'focus_bank_i')
  })

  it('propagates reduced-motion preference into the instrument surface', async () => {
    Object.defineProperty(window, 'matchMedia', { writable: true, value: vi.fn(() => matchMedia(true)) })
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response(JSON.stringify(manifestFixture), { status: 200 })))
    const { container } = render(<App />)
    await screen.findByRole('button', { name: 'Open the Arca' })
    expect(container.querySelector('[data-reduced-motion="true"]')).toBeInTheDocument()
  })
})
