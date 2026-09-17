import { useCallback, useEffect, useRef } from 'react'
import { dollyBy, orbitBy, type OrbitState } from './camera'
import { useSpatialGrabOwnership } from './grabOwnership'

export function useOrbitInput(orbit: React.RefObject<OrbitState>) {
  const store = useSpatialGrabOwnership()
  const drag = useRef<{id:number;x:number;y:number}|null>(null)
  const pinch = useRef<number|null>(null)
  const points = useRef(new Map<number,{x:number;y:number}>())
  const clear = useCallback(() => { drag.current=null;pinch.current=null;points.current.clear() },[])
  const onPointerDown = useCallback((event:React.PointerEvent) => {
    if(store.ownerRef.current) { clear(); return }
    points.current.set(event.pointerId,{x:event.clientX,y:event.clientY})
    if(points.current.size===2) {
      const [a,b]=[...points.current.values()]
      pinch.current=Math.hypot(a.x-b.x,a.y-b.y);drag.current=null;return
    }
    drag.current={id:event.pointerId,x:event.clientX,y:event.clientY}
  },[store,clear])
  const onPointerMove = useCallback((event:React.PointerEvent) => {
    if(store.ownerRef.current || event.buttons===0) {clear();return}
    if(points.current.has(event.pointerId)) points.current.set(event.pointerId,{x:event.clientX,y:event.clientY})
    if(pinch.current!==null && points.current.size===2) {
      const [a,b]=[...points.current.values()]
      const distance=Math.hypot(a.x-b.x,a.y-b.y)
      if(distance>0 && pinch.current>0) dollyBy(orbit.current,pinch.current/distance)
      pinch.current=distance;return
    }
    const active=drag.current
    if(!active || active.id!==event.pointerId) return
    orbitBy(orbit.current,(event.clientX-active.x)*-0.0085,(event.clientY-active.y)*0.0065)
    active.x=event.clientX;active.y=event.clientY
  },[store,orbit,clear])
  const end = useCallback((event:{pointerId:number}) => {
    points.current.delete(event.pointerId)
    if(points.current.size<2) pinch.current=null
    if(drag.current?.id===event.pointerId) drag.current=null
  },[])
  useEffect(() => {
    window.addEventListener('pointerup',end)
    window.addEventListener('pointercancel',end)
    window.addEventListener('lostpointercapture',end,true)
    window.addEventListener('blur',clear)
    return () => {
      window.removeEventListener('pointerup',end)
      window.removeEventListener('pointercancel',end)
      window.removeEventListener('lostpointercapture',end,true)
      window.removeEventListener('blur',clear)
      clear()
    }
  },[end,clear])
  const onWheel = useCallback((event:React.WheelEvent) => {
    if(!store.ownerRef.current) dollyBy(orbit.current,event.deltaY>0?1.08:1/1.08)
  },[store,orbit])
  return {onPointerDown,onPointerMove,onPointerUp:end,onPointerCancel:end,onWheel}
}
