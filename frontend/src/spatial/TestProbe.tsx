import { useEffect } from 'react'
import { useThree } from '@react-three/fiber'
import * as THREE from 'three'

/**
 * A DEV-ONLY testing seam.
 *
 * Browser-driven QA has to be able to aim at a real part of a 3D instrument —
 * tapping a guessed screen coordinate and hoping it lands on a virga is not a
 * test, it is a coin toss. This publishes just enough to project a named world
 * point to screen space, so the harness can press the actual object.
 *
 * It is compiled out of production builds by the `import.meta.env.DEV` guard,
 * and it exposes no way to CHANGE instrument state — a probe, not a back door.
 */
export function SpatialTestProbe() {
  const camera = useThree((s) => s.camera)
  const scene = useThree((s) => s.scene)
  const size = useThree((s) => s.size)
  const gl = useThree((s) => s.gl)

  useEffect(() => {
    if (!import.meta.env.DEV) return
    const project = (x: number, y: number, z: number) => {
      const v = new THREE.Vector3(x, y, z).project(camera)
      return {
        x: (v.x * 0.5 + 0.5) * size.width,
        y: (-v.y * 0.5 + 0.5) * size.height,
        visible: v.z < 1,
      }
    }
    const probe = {
      project,
      /** Screen position of a named scene object, found by traversal. */
      locate(name: string) {
        let found: THREE.Object3D | null = null
        scene.traverse((object) => { if (!found && object.name === name) found = object })
        if (!found) return null
        const world = new THREE.Vector3()
        ;(found as THREE.Object3D).getWorldPosition(world)
        return { ...project(world.x, world.y, world.z), world: world.toArray() }
      },
      camera: () => camera.position.toArray(),
      /**
       * Hardware-independent render cost. Frame rate under a software
       * rasteriser is meaningless, but draw calls, triangles and shader
       * programs are the numbers that actually predict behaviour on a phone
       * or a standalone headset.
       */
      cost: () => ({
        drawCalls: gl.info.render.calls,
        triangles: gl.info.render.triangles,
        programs: gl.info.programs?.length ?? 0,
        geometries: gl.info.memory.geometries,
        textures: gl.info.memory.textures,
        pixelRatio: gl.getPixelRatio(),
      }),
    }
    ;(window as unknown as { __arcaProbe?: typeof probe }).__arcaProbe = probe
    return () => { delete (window as unknown as { __arcaProbe?: typeof probe }).__arcaProbe }
  }, [camera, scene, size, gl])

  return null
}
