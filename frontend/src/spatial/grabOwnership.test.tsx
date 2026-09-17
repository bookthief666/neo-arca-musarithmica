import { useEffect } from 'react'
import { act, render } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import {
  createSpatialGrabStore,
  SpatialGrabProvider,
  useSpatialGrabOwnership,
  type SpatialGrabStore,
} from './grabOwnership'

function GrabProbe({ onStore }: { onStore: (store: SpatialGrabStore) => void }) {
  const store = useSpatialGrabOwnership()
  useEffect(() => onStore(store), [onStore, store])
  return null
}

describe('spatial grab ownership', () => {
  it('allows one presentation gesture owner at a time', () => {
    const store = createSpatialGrabStore()

    expect(store.claim('event-reader')).toBe(true)
    expect(store.ownerRef.current).toBe('event-reader')
    expect(store.claim('carrier')).toBe(false)
    expect(store.ownerRef.current).toBe('event-reader')

    store.release('carrier')
    expect(store.ownerRef.current).toBe('event-reader')

    store.release('event-reader')
    expect(store.ownerRef.current).toBeNull()
    expect(store.claim('carrier')).toBe(true)
    expect(store.ownerRef.current).toBe('carrier')
  })

  it('lets the current owner re-claim without losing ownership', () => {
    const store = createSpatialGrabStore()
    expect(store.claim('event-reader')).toBe(true)
    expect(store.claim('event-reader')).toBe(true)
    expect(store.ownerRef.current).toBe('event-reader')
  })

  it('exposes the same store through context and clears ownership on provider unmount', () => {
    const store = createSpatialGrabStore()
    const observed = vi.fn<(value: SpatialGrabStore) => void>()
    const { unmount } = render(
      <SpatialGrabProvider store={store}>
        <GrabProbe onStore={observed} />
      </SpatialGrabProvider>,
    )

    expect(observed).toHaveBeenCalledWith(store)
    act(() => {
      expect(store.claim('event-reader')).toBe(true)
    })
    expect(store.ownerRef.current).toBe('event-reader')

    unmount()
    expect(store.ownerRef.current).toBeNull()
  })

  it('supports explicit cleanup for pointer-cancel and lost-release paths', () => {
    const store = createSpatialGrabStore()
    store.claim('event-reader')
    store.clear()
    expect(store.ownerRef.current).toBeNull()
  })
})
