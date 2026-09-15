import { render, screen } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import App from './App'
import { manifestFixture } from './test/fixtures'

const matchMedia = (matches: boolean) => ({
  matches, media: '(prefers-reduced-motion: reduce)', onchange: null,
  addEventListener: vi.fn(), removeEventListener: vi.fn(),
  addListener: vi.fn(), removeListener: vi.fn(), dispatchEvent: vi.fn(),
})

/**
 * jsdom has no WebGL, so App falls back to the M1.1 renderer here. That IS the
 * fallback contract: the instrument must still be fully operable anywhere the
 * spatial renderer cannot present, which is also why the whole M1.1 behaviour
 * suite continues to pass unchanged.
 */
describe('M1.2 renderer fallback', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
    Object.defineProperty(window, 'matchMedia', { writable: true, value: vi.fn(() => matchMedia(false)) })
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(
      new Response(JSON.stringify(manifestFixture), { status: 200 }),
    ))
  })

  it('falls back to the M1.1 renderer where WebGL cannot be presented', async () => {
    const { container } = render(<App />)
    await screen.findByRole('button', { name: 'Open the Arca' })
    expect(container.querySelector('.instrument-shell')).toHaveAttribute('data-renderer', 'legacy')
  })

  it('keeps the instrument fully operable in the fallback', async () => {
    render(<App />)
    // The canonical first affordance is reachable and the realm is unchanged.
    expect(await screen.findByRole('button', { name: 'Open the Arca' })).toBeEnabled()
    expect(document.querySelector('.instrument-shell')).toHaveAttribute('data-realm', 'historica')
  })

  it('exposes no renderer switcher to the reader', async () => {
    render(<App />)
    await screen.findByRole('button', { name: 'Open the Arca' })
    for (const name of [/renderer/i, /3d/i, /spatial/i, /legacy/i]) {
      expect(screen.queryByRole('button', { name })).not.toBeInTheDocument()
    }
  })
})
