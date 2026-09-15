import { useEffect } from 'react'
import { useThree } from '@react-three/fiber'
import * as THREE from 'three'
import { RoomEnvironment } from 'three/examples/jsm/environments/RoomEnvironment.js'

/**
 * A procedural studio environment.
 *
 * Physically-based metal is almost entirely REFLECTION: with direct lights
 * alone, brass at metalness 0.9 renders black except for a few specular dots,
 * which is exactly how the first pass looked. An environment gives it something
 * to reflect and the hardware becomes metal.
 *
 * RoomEnvironment ships inside the three package and is generated at runtime,
 * so this costs no network request and vendors no third-party HDRI — the
 * instrument carries no art it does not own.
 */
export function StudioEnvironment({ intensity = 0.55 }: { intensity?: number }) {
  const { gl, scene } = useThree()

  useEffect(() => {
    const pmrem = new THREE.PMREMGenerator(gl)
    pmrem.compileEquirectangularShader()
    const room = new RoomEnvironment()
    const target = pmrem.fromScene(room, 0.04)
    scene.environment = target.texture
    scene.environmentIntensity = intensity

    return () => {
      scene.environment = null
      target.texture.dispose()
      pmrem.dispose()
      room.traverse((object) => {
        const mesh = object as THREE.Mesh
        if (mesh.geometry) mesh.geometry.dispose()
        const material = mesh.material
        if (Array.isArray(material)) material.forEach((m) => m.dispose())
        else if (material) material.dispose()
      })
    }
  }, [gl, scene, intensity])

  return null
}
