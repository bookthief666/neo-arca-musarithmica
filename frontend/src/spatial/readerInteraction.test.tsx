import { act, fireEvent, render, screen } from '@testing-library/react'
import { expect, it, vi } from 'vitest'
import * as THREE from 'three'
import { createSpatialGrabStore, SpatialGrabProvider } from './grabOwnership'
import { useReaderDrag } from './readerInteraction'
import { useOrbitInput } from './orbitInput'
import type { OrbitState } from './camera'

function pointer(target: Element | Window, type: string, id=1, x=0, buttons=1) {
  const event = new Event(type,{bubbles:true,cancelable:true})
  Object.assign(event,{pointerId:id,clientX:x,clientY:20,buttons})
  fireEvent(target,event)
}
const orbit = () => ({current:{azimuth:0,elevation:0.5,distance:0.6,target:new THREE.Vector3(),userDriven:false} satisfies OrbitState})
function Harness({travel=0,onPosition,show=true,orbitRef}:{travel?:number;onPosition:(n:number)=>void;show?:boolean;orbitRef:ReturnType<typeof orbit>}) {
  const input=useOrbitInput(orbitRef)
  return <div data-testid="orbit" {...input}>{show && <Reader travel={travel} onPosition={onPosition}/>}</div>
}
function Reader({travel,onPosition}:{travel:number;onPosition:(n:number)=>void}) {
  const begin=useReaderDrag(() => ({
    ray:new THREE.Ray(new THREE.Vector3(0.1,0.2,0.021+travel),new THREE.Vector3(-0.4,-0.8,0).normalize()),
    worldOrigin:new THREE.Vector3(0,0,travel),worldAxis:new THREE.Vector3(0,0,1),
    minLocal:-0.04,maxLocal:0.04,count:6,
  }),onPosition)
  return <button data-testid="reader" onPointerDown={e => {e.stopPropagation();begin(e.nativeEvent)}}>Reader</button>
}
it.each([0,0.07,0.14,0.21])('uses translated local detents in the live hook at %f',travel => {
  const store=createSpatialGrabStore(), onPosition=vi.fn()
  render(<SpatialGrabProvider store={store}><Harness travel={travel} onPosition={onPosition} orbitRef={orbit()}/></SpatialGrabProvider>)
  pointer(screen.getByTestId('reader'),'pointerdown')
  pointer(window,'pointermove')
  expect(onPosition).toHaveBeenLastCalledWith(4)
  pointer(window,'pointerup')
  expect(store.ownerRef.current).toBeNull()
})
it.each(['pointerup','pointercancel','lostpointercapture','blur'])('releases on %s and orbit resumes',type => {
  const store=createSpatialGrabStore(), ref=orbit()
  render(<SpatialGrabProvider store={store}><Harness onPosition={vi.fn()} orbitRef={ref}/></SpatialGrabProvider>)
  pointer(screen.getByTestId('reader'),'pointerdown')
  pointer(screen.getByTestId('orbit'),'pointerdown',2)
  pointer(screen.getByTestId('orbit'),'pointermove',2,50)
  fireEvent.wheel(screen.getByTestId('orbit'),{deltaY:20})
  expect(ref.current.azimuth).toBe(0)
  expect(ref.current.distance).toBe(0.6)
  pointer(window,type)
  expect(store.ownerRef.current).toBeNull()
  pointer(screen.getByTestId('orbit'),'pointerdown',3)
  pointer(screen.getByTestId('orbit'),'pointermove',3,50)
  expect(ref.current.azimuth).not.toBe(0)
})
it('ignores other pointers and releases when buttons are lost off target',() => {
  const store=createSpatialGrabStore(),onPosition=vi.fn()
  render(<SpatialGrabProvider store={store}><Harness onPosition={onPosition} orbitRef={orbit()}/></SpatialGrabProvider>)
  pointer(screen.getByTestId('reader'),'pointerdown')
  pointer(window,'pointerup',2)
  pointer(window,'pointermove',2)
  expect(onPosition).not.toHaveBeenCalled()
  expect(store.ownerRef.current).toBe('event-reader')
  pointer(window,'pointermove',1,0,0)
  expect(store.ownerRef.current).toBeNull()
})
it('cleans up component ownership and listeners without clearing a different owner',() => {
  const store=createSpatialGrabStore(), onPosition=vi.fn(), ref=orbit()
  const ui=(show:boolean) => <SpatialGrabProvider store={store}><Harness show={show} onPosition={onPosition} orbitRef={ref}/></SpatialGrabProvider>
  const {rerender,unmount}=render(ui(true))
  pointer(screen.getByTestId('reader'),'pointerdown')
  rerender(ui(false))
  expect(store.ownerRef.current).toBeNull()
  pointer(window,'pointermove')
  expect(onPosition).not.toHaveBeenCalled()
  act(() => store.claim('other'))
  unmount()
  expect(store.ownerRef.current).toBeNull()
})
it('preserves a grab across canonical cursor rerenders and refuses another owner',() => {
  const store=createSpatialGrabStore(), ref=orbit(), first=vi.fn(), second=vi.fn()
  const ui=(callback:(n:number)=>void) => <SpatialGrabProvider store={store}><Harness onPosition={callback} orbitRef={ref}/></SpatialGrabProvider>
  const {rerender}=render(ui(first))
  act(() => store.claim('other'))
  pointer(screen.getByTestId('reader'),'pointerdown')
  pointer(window,'pointermove')
  expect(first).not.toHaveBeenCalled()
  act(() => store.release('other'))
  pointer(screen.getByTestId('reader'),'pointerdown')
  rerender(ui(second))
  pointer(window,'pointermove')
  expect(second).toHaveBeenCalledWith(4)
  expect(store.ownerRef.current).toBe('event-reader')
})
