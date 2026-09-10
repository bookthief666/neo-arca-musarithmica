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

  it('completes the essential cabinet → rods → Tone II → kernel path with keyboard rod alignment', async () => {
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
      await user.click(screen.getByRole('button', { name: `Retrieve ${template.label}` }))
      await user.click(screen.getByRole('button', { name: 'Lay the lifted rod beside the rule' }))
    }

    const rods = screen.getAllByRole('slider', { name: /Use up and down arrow keys or drag vertically/ })
    expect(rods).toHaveLength(3)
    for (const rod of rods) {
      rod.focus()
      await user.keyboard('{Home}')
    }

    expect(screen.getByRole('status')).toHaveTextContent('BAND 01 · H0 VERIFIED')
    await user.click(screen.getByRole('button', { name: 'Engage Tone II Hypodorius' }))
    await user.click(screen.getByRole('button', { name: 'Read the transverse' }))

    expect(await screen.findByText('Four voices manifest')).toBeInTheDocument()
    expect(screen.getByRole('table', { name: 'Symbolic historical four-voice result' })).toBeInTheDocument()
    expect(fetchMock).toHaveBeenCalledTimes(2)
    const submitted = JSON.parse(String(fetchMock.mock.calls[1][1]?.body))
    expect(submitted.rod_instances.every((rod: { vertical_offset: number }) => rod.vertical_offset === 0)).toBe(true)
    expect(submitted.tone).toEqual({ number: 2, engaged: true })
  })

  it('propagates reduced-motion preference into the instrument surface', async () => {
    Object.defineProperty(window, 'matchMedia', { writable: true, value: vi.fn(() => matchMedia(true)) })
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response(JSON.stringify(manifestFixture), { status: 200 })))
    const { container } = render(<App />)
    await screen.findByRole('button', { name: 'Open the Arca' })
    expect(container.querySelector('[data-reduced-motion="true"]')).toBeInTheDocument()
  })
})
