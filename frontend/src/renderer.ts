/**
 * RENDERER SELECTION.
 *
 * M1.2 makes the spatial instrument the default. The M1.1 DOM renderer is kept
 * as a rollback, a visual reference and a fallback for anything that cannot
 * present WebGL, reachable at `?renderer=legacy`.
 *
 * This is deliberately not a product feature: there is no switcher in the
 * interface, because the reader is not meant to choose a rendering technology.
 */
export type RendererId = 'spatial' | 'legacy'

export function resolveRenderer(search?: string): RendererId {
  const query = search ?? (typeof window === 'undefined' ? '' : window.location.search)
  const requested = new URLSearchParams(query).get('renderer')
  if (requested === 'legacy') return 'legacy'
  if (requested === 'spatial') return 'spatial'
  return 'spatial'
}

/** True when this browser can actually present the spatial renderer. */
export function supportsWebGL(): boolean {
  if (typeof document === 'undefined') return false
  // Cheap negative first. Environments without WebGL — jsdom among them — have
  // no WebGLRenderingContext at all, and asking such a canvas for a context
  // logs a noisy "not implemented" before returning null anyway.
  if (typeof WebGLRenderingContext === 'undefined') return false
  try {
    const probe = document.createElement('canvas')
    return Boolean(probe.getContext('webgl2') ?? probe.getContext('webgl'))
  } catch {
    return false
  }
}
