import { useMemo } from 'react'
import * as THREE from 'three'
import { makeWoodRoughness, makeWoodTexture } from './textures'

/**
 * THE MATERIAL HIERARCHY, in physically-based terms.
 *
 * The same discipline the 2D instrument observed, now expressed as real
 * surfaces: wood carries structure, brass is the only thing that operates,
 * vellum is the only thing that carries historical information, and a recess
 * is genuinely dark rather than merely dim.
 *
 * Every material here is created ONCE and shared by every mesh that needs it.
 * A cabinet of this many parts would otherwise compile a hundred near-identical
 * shader programs, which matters on the Fold and matters far more on a Quest.
 */
export interface ArcaMaterials {
  wood: THREE.MeshStandardMaterial
  woodDark: THREE.MeshStandardMaterial
  brass: THREE.MeshStandardMaterial
  brassDark: THREE.MeshStandardMaterial
  brassLit: THREE.MeshStandardMaterial
  void: THREE.MeshStandardMaterial
  felt: THREE.MeshStandardMaterial
  vellum: THREE.MeshStandardMaterial
  wax: THREE.MeshStandardMaterial
  dispose: () => void
}

export function useArcaMaterials(): ArcaMaterials {
  return useMemo(() => {
    const grain = makeWoodTexture()
    const grainRough = makeWoodRoughness()
    grain.repeat.set(1.6, 1.6)
    grainRough.repeat.set(1.6, 1.6)

    const wood = new THREE.MeshStandardMaterial({
      map: grain,
      roughnessMap: grainRough,
      roughness: 0.62,
      metalness: 0.04,
      color: new THREE.Color('#c8a888'),
    })
    const woodDark = new THREE.MeshStandardMaterial({
      map: grain,
      roughnessMap: grainRough,
      roughness: 0.72,
      metalness: 0.03,
      color: new THREE.Color('#8a6e58'),
    })
    // Cast brass. High metalness, low-ish roughness: it should pick up the key
    // light as a specular streak, which is what makes it read as metal.
    const brass = new THREE.MeshStandardMaterial({
      color: new THREE.Color('#c3a25c'), metalness: 0.94, roughness: 0.28,
    })
    const brassDark = new THREE.MeshStandardMaterial({
      color: new THREE.Color('#7d6531'), metalness: 0.92, roughness: 0.44,
    })
    // Reserved for the ONE lit affordance and for verified continuity.
    const brassLit = new THREE.MeshStandardMaterial({
      color: new THREE.Color('#e8cb87'), metalness: 0.9, roughness: 0.2,
      emissive: new THREE.Color('#5a3f12'), emissiveIntensity: 0.55,
    })
    const voidMat = new THREE.MeshStandardMaterial({
      color: new THREE.Color('#0d0906'), roughness: 0.95, metalness: 0,
    })
    const felt = new THREE.MeshStandardMaterial({
      color: new THREE.Color('#1b1310'), roughness: 1, metalness: 0,
    })
    const vellum = new THREE.MeshStandardMaterial({
      color: new THREE.Color('#f6eedb'), roughness: 0.88, metalness: 0,
    })
    const wax = new THREE.MeshStandardMaterial({
      color: new THREE.Color('#8a3520'), roughness: 0.55, metalness: 0,
    })

    const all = [wood, woodDark, brass, brassDark, brassLit, voidMat, felt, vellum, wax]
    return {
      wood, woodDark, brass, brassDark, brassLit, void: voidMat, felt, vellum, wax,
      dispose: () => {
        all.forEach((m) => m.dispose())
        grain.dispose()
        grainRough.dispose()
      },
    }
  }, [])
}
