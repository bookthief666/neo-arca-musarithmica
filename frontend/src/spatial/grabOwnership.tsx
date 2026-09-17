import { createContext, useContext, useEffect, type ReactNode } from 'react'

export interface SpatialGrabStore {
  ownerRef: { current: string | null }
  claim: (owner: string) => boolean
  release: (owner: string) => void
  clear: () => void
}

// Deliberately co-located: this module is the scene's presentation-only seam.
// eslint-disable-next-line react-refresh/only-export-components
export function createSpatialGrabStore(): SpatialGrabStore {
  const ownerRef: SpatialGrabStore['ownerRef'] = { current: null }
  return {
    ownerRef,
    claim(owner) {
      if (ownerRef.current !== null && ownerRef.current !== owner) return false
      ownerRef.current = owner
      return true
    },
    release(owner) {
      if (ownerRef.current === owner) ownerRef.current = null
    },
    clear() { ownerRef.current = null },
  }
}

const GrabContext = createContext<SpatialGrabStore | null>(null)

export function SpatialGrabProvider({ store, children }: {
  store: SpatialGrabStore
  children: ReactNode
}) {
  useEffect(() => () => store.clear(), [store])
  return <GrabContext.Provider value={store}>{children}</GrabContext.Provider>
}

// eslint-disable-next-line react-refresh/only-export-components
export function useSpatialGrabOwnership(): SpatialGrabStore {
  const store = useContext(GrabContext)
  if (!store) throw new Error('Spatial grab ownership requires a SpatialGrabProvider')
  return store
}
