import { useMemo, useRef } from 'react'
import { useFrame, useThree } from '@react-three/fiber'
import * as THREE from 'three'
import { CARRIAGE, VIRGA } from '../dimensions'
import { useReaderDrag } from '../readerInteraction'

// Presentation-only travel: six inspection positions, never six musical alternatives.
const MIN = -VIRGA.length * 0.36
const MAX = VIRGA.length * 0.36
export function EventReader({ position, travelRef, onPosition }: {
  position: number
  travelRef: React.RefObject<number>
  onPosition: (position: number) => void
}) {
  const constraint = useRef<THREE.Group>(null)
  const camera = useThree(s => s.camera)
  const canvas = useThree(s => s.gl.domElement)
  const math = useMemo(() => ({
    raycaster:new THREE.Raycaster(), ndc:new THREE.Vector2(),
    origin:new THREE.Vector3(), axis:new THREE.Vector3(), rotation:new THREE.Quaternion(),
  }),[])
  const begin = useReaderDrag(event => {
    const node=constraint.current
    const rect=canvas.getBoundingClientRect()
    if(!node || rect.width<=0 || rect.height<=0) return null
    math.ndc.set((event.clientX-rect.left)/rect.width*2-1,-(event.clientY-rect.top)/rect.height*2+1)
    math.raycaster.setFromCamera(math.ndc,camera)
    node.position.z=travelRef.current
    node.updateWorldMatrix(true,false)
    node.getWorldPosition(math.origin)
    node.getWorldQuaternion(math.rotation)
    math.axis.set(0,0,1).applyQuaternion(math.rotation).normalize()
    return {ray:math.raycaster.ray,worldOrigin:math.origin,worldAxis:math.axis,minLocal:MIN,maxLocal:MAX,count:6}
  }, onPosition)
  useFrame(() => { if(constraint.current) constraint.current.position.z=travelRef.current })
  return <group ref={constraint} position={[0,CARRIAGE.y+CARRIAGE.wall+VIRGA.thickness+0.014,travelRef.current]}>
    <mesh position={[0,0,MIN+(MAX-MIN)*position/5]} onPointerDown={event => {
      event.stopPropagation()
      begin(event.nativeEvent)
    }}>
      <boxGeometry args={[0.032,0.008,0.008]} />
      <meshStandardMaterial color="#d4b77a" metalness={0.75} roughness={0.35} />
    </mesh>
  </group>
}
