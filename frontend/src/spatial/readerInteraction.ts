import { useCallback, useEffect, useRef } from 'react'
import type { Ray, Vector3 } from 'three'
import { useSpatialGrabOwnership } from './grabOwnership'
import { projectRayToLocalDetent } from './interaction'
export interface ReaderProjection {
  ray: Ray
  worldOrigin: Vector3
  worldAxis: Vector3
  minLocal: number
  maxLocal: number
  count: number
}
const OWNER = 'event-reader'

/** Browser event lifetime only; ray projection and canonical event input remain independent. */
export function useReaderDrag(project: (event: PointerEvent) => ReaderProjection | null, onPosition: (position: number) => void) {
  const store = useSpatialGrabOwnership()
  const active = useRef<number | null>(null)
  const latest = useRef({project,onPosition})
  latest.current = {project,onPosition}
  const release = useCallback(() => {
    active.current = null
    store.release(OWNER)
  }, [store])
  const begin = useCallback((event: PointerEvent) => {
    if (active.current !== null || !store.claim(OWNER)) return
    active.current = event.pointerId
  }, [store])
  useEffect(() => {
    const move = (event: PointerEvent) => {
      if (active.current !== event.pointerId) return
      if (event.buttons === 0 || store.ownerRef.current !== OWNER) { release(); return }
      event.preventDefault()
      const projection = latest.current.project(event)
      if (!projection) return
      const {ray,worldOrigin,worldAxis,minLocal,maxLocal,count} = projection
      latest.current.onPosition(projectRayToLocalDetent(ray,worldOrigin,worldAxis,minLocal,maxLocal,count))
    }
    const end = (event: PointerEvent) => {
      if (active.current === event.pointerId) release()
    }
    window.addEventListener('pointermove',move,{passive:false})
    window.addEventListener('pointerup',end)
    window.addEventListener('pointercancel',end)
    window.addEventListener('lostpointercapture',end,true)
    window.addEventListener('blur',release)
    return () => {
      window.removeEventListener('pointermove',move)
      window.removeEventListener('pointerup',end)
      window.removeEventListener('pointercancel',end)
      window.removeEventListener('lostpointercapture',end,true)
      window.removeEventListener('blur',release)
      release()
    }
  },[store,release])
  return begin
}
