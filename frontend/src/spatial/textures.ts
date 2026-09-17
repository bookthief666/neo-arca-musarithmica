import * as THREE from 'three'
import type { HistoricalManifest, CriticalEditionCarrier, VoiceName } from '../instrument/types'

/**
 * Every texture in the spatial Arca is drawn here, procedurally, onto a canvas.
 *
 * Nothing is fetched and no image file is vendored: the instrument carries no
 * third-party art and there is no licensing ambiguity to inherit. It also means
 * the historical surfaces are drawn FROM THE MANIFEST — the Mensa and the virga
 * faces are renderings of the same verified data the kernel executes, not
 * pictures of data that might drift away from it.
 */

const INK = '#241705'
const INK_SOFT = '#4a3620'
const INK_MUTED = '#6f5a3b'
const RULE = 'rgba(58, 42, 24, 0.55)'

const DISPLAY = '"Iowan Old Style", "Palatino Linotype", Palatino, Georgia, serif'
const ENGRAVED = 'ui-monospace, "DejaVu Sans Mono", Menlo, Consolas, monospace'

function canvas(width: number, height: number) {
  const element = document.createElement('canvas')
  element.width = width
  element.height = height
  const context = element.getContext('2d')
  if (!context) throw new Error('2D canvas context unavailable for Arca texture generation.')
  return { element, context }
}

function finish(element: HTMLCanvasElement, anisotropy = 8) {
  const texture = new THREE.CanvasTexture(element)
  texture.colorSpace = THREE.SRGBColorSpace
  texture.anisotropy = anisotropy
  texture.needsUpdate = true
  return texture
}

/** Toned vellum ground, laid lines and all, used under every printed surface. */
function layVellum(context: CanvasRenderingContext2D, w: number, h: number) {
  const wash = context.createLinearGradient(0, 0, w * 0.35, h)
  wash.addColorStop(0, '#fdf8ec')
  wash.addColorStop(0.55, '#f4ecd8')
  wash.addColorStop(1, '#e6dabe')
  context.fillStyle = wash
  context.fillRect(0, 0, w, h)

  // Laid lines: the mould's wire marks, very faint.
  context.strokeStyle = 'rgba(120, 96, 58, 0.055)'
  context.lineWidth = 1
  for (let y = 0; y < h; y += Math.max(4, Math.round(h / 150))) {
    context.beginPath()
    context.moveTo(0, y + 0.5)
    context.lineTo(w, y + 0.5)
    context.stroke()
  }
  // Foxing: a few soft age spots so the sheet is not a flat fill.
  for (let i = 0; i < 26; i++) {
    const x = Math.random() * w
    const y = Math.random() * h
    const r = 3 + Math.random() * 16
    const spot = context.createRadialGradient(x, y, 0, x, y, r)
    spot.addColorStop(0, 'rgba(150, 118, 68, 0.05)')
    spot.addColorStop(1, 'rgba(150, 118, 68, 0)')
    context.fillStyle = spot
    context.beginPath()
    context.arc(x, y, r, 0, Math.PI * 2)
    context.fill()
  }
}

/** Figured walnut, drawn as drifting grain lines rather than a flat colour. */
export function makeWoodTexture(size = 1024) {
  const { element, context } = canvas(size, size)
  const base = context.createLinearGradient(0, 0, size * 0.4, size)
  base.addColorStop(0, '#8a5c3d')
  base.addColorStop(0.5, '#6d462e')
  base.addColorStop(1, '#4a2f1d')
  context.fillStyle = base
  context.fillRect(0, 0, size, size)

  // Grain: long lines that wander, bunching into figure here and there.
  for (let i = 0; i < 260; i++) {
    const y0 = Math.random() * size
    const amp = 4 + Math.random() * 26
    const period = 180 + Math.random() * 420
    const dark = Math.random() < 0.72
    context.strokeStyle = dark
      ? `rgba(36, 20, 10, ${0.05 + Math.random() * 0.14})`
      : `rgba(206, 154, 104, ${0.03 + Math.random() * 0.07})`
    context.lineWidth = 0.6 + Math.random() * 2.1
    context.beginPath()
    for (let x = 0; x <= size; x += 8) {
      const y = y0 + Math.sin((x / period) * Math.PI * 2 + i) * amp
      if (x === 0) context.moveTo(x, y)
      else context.lineTo(x, y)
    }
    context.stroke()
  }
  // Pores.
  for (let i = 0; i < 2600; i++) {
    context.fillStyle = `rgba(28, 15, 7, ${0.04 + Math.random() * 0.1})`
    context.fillRect(Math.random() * size, Math.random() * size, 1 + Math.random() * 2.4, 1)
  }
  const texture = finish(element)
  texture.wrapS = THREE.RepeatWrapping
  texture.wrapT = THREE.RepeatWrapping
  return texture
}

/** A roughness companion to the wood, so the grain catches light unevenly. */
export function makeWoodRoughness(size = 512) {
  const { element, context } = canvas(size, size)
  context.fillStyle = '#9a9a9a'
  context.fillRect(0, 0, size, size)
  for (let i = 0; i < 150; i++) {
    const y0 = Math.random() * size
    context.strokeStyle = `rgba(255,255,255,${0.04 + Math.random() * 0.1})`
    context.lineWidth = 1 + Math.random() * 3
    context.beginPath()
    for (let x = 0; x <= size; x += 10) {
      context.lineTo(x, y0 + Math.sin(x / 90 + i) * 12)
    }
    context.stroke()
  }
  const texture = new THREE.CanvasTexture(element)
  texture.wrapS = THREE.RepeatWrapping
  texture.wrapT = THREE.RepeatWrapping
  return texture
}

/** Plain toned vellum, for folio and card surfaces. */
export function makeVellumTexture(w = 512, h = 512) {
  const { element, context } = canvas(w, h)
  layVellum(context, w, h)
  return finish(element)
}

/**
 * THE MENSA TONOGRAPHICA, drawn from the manifest's verified tone mapping.
 *
 * The eight degree→pitch-class pairs are printed exactly as the kernel supplies
 * them. No octave, register or accidental is inferred here; the glyph swap is
 * purely typographic (b → ♭, # → ♯).
 */
export function makeMensaTexture(manifest: HistoricalManifest) {
  const W = 1024
  const H = 640
  const { element, context } = canvas(W, H)
  layVellum(context, W, H)

  const glyph = (pitch: string) => pitch.replace('b', '♭').replace('#', '♯')
  const degrees = Object.entries(manifest.tone.degree_to_pitch_class)

  // Plate mark: the impression the printing plate left in the sheet.
  context.strokeStyle = 'rgba(97, 72, 44, 0.3)'
  context.lineWidth = 2
  context.strokeRect(26, 26, W - 52, H - 52)

  context.textAlign = 'center'
  context.fillStyle = INK
  context.font = `600 52px ${DISPLAY}`
  context.letterSpacing = '7px'
  context.fillText('MENSA TONOGRAPHICA', W / 2, 108)
  context.letterSpacing = '0px'

  context.font = `italic 27px ${DISPLAY}`
  context.fillStyle = INK_SOFT
  context.fillText(`Tonus ${manifest.tone.number} · ${manifest.tone.name} · ${manifest.tone.system}`, W / 2, 152)

  // The ruled table of degrees.
  const tableX = 78
  const tableW = W - tableX * 2
  const tableY = 196
  const rowH = 74
  const cellW = tableW / degrees.length

  context.strokeStyle = RULE
  context.lineWidth = 2.5
  context.strokeRect(tableX, tableY, tableW, rowH * 2)
  context.lineWidth = 1.5
  for (let i = 1; i < degrees.length; i++) {
    context.beginPath()
    context.moveTo(tableX + cellW * i, tableY)
    context.lineTo(tableX + cellW * i, tableY + rowH * 2)
    context.stroke()
  }
  context.beginPath()
  context.moveTo(tableX, tableY + rowH)
  context.lineTo(tableX + tableW, tableY + rowH)
  context.stroke()

  degrees.forEach(([degree, pitch], index) => {
    const cx = tableX + cellW * (index + 0.5)
    context.fillStyle = INK_MUTED
    context.font = `28px ${ENGRAVED}`
    context.fillText(degree, cx, tableY + 48)
    context.fillStyle = INK
    context.font = `600 50px ${DISPLAY}`
    context.fillText(glyph(pitch), cx, tableY + rowH + 52)
  })

  context.fillStyle = INK_SOFT
  context.font = `italic 25px ${DISPLAY}`
  context.fillText('Mensæ tonus instructum dat congruum.', W / 2, tableY + rowH * 2 + 62)

  context.fillStyle = INK_MUTED
  context.font = `21px ${ENGRAVED}`
  context.letterSpacing = '3px'
  context.fillText(manifest.tone.witness, W / 2, H - 62)
  context.letterSpacing = '0px'

  return finish(element, 16)
}

const VOICE_ORDER: VoiceName[] = ['cantus', 'altus', 'tenor', 'bassus']
const VOICE_MARK: Record<VoiceName, string> = { cantus: 'C', altus: 'A', tenor: 'T', bassus: 'B' }

/** One editorial extract; no implied untranscribed musical choices. */
export function makeVirgaTexture(source: CriticalEditionCarrier) {
  const W = 512, H = 1024
  const { element, context } = canvas(W,H)
  layVellum(context,W,H)
  context.fillStyle = INK
  context.textAlign = 'left'
  context.font = `24px ${ENGRAVED}`
  const lines = [
    'PINAX IV · H1 EXTRACT',
    'VPERM 01',
    ...VOICE_ORDER.map(voice => VOICE_MARK[voice] + ' ' + source.pitch_source.content.rows[voice].join(' ')),
    'RPERM 03',
    ...source.rhythm_source.content.glyphs,
    'RELATIVE MINIM UNITS',
    source.rhythm_source.content.relative_minim_units.join(' '),
  ]
  lines.forEach((line,index) => context.fillText(line,18,48+index*58,W-36))
  return finish(element,16)
}

/** An engraved brass plate: the bank nameplates and the cabinet's identity. */
export function makeBrassPlateTexture(lines: { text: string; size: number; gap?: number }[], opts?: {
  width?: number; height?: number; tarnished?: boolean
}) {
  const W = opts?.width ?? 512
  const H = opts?.height ?? 160
  const { element, context } = canvas(W, H)

  const field = context.createLinearGradient(0, 0, 0, H)
  if (opts?.tarnished) {
    field.addColorStop(0, '#8d7c55'); field.addColorStop(0.35, '#75653f')
    field.addColorStop(0.75, '#564a2e'); field.addColorStop(1, '#3b3220')
  } else {
    field.addColorStop(0, '#fff6d8'); field.addColorStop(0.1, '#f2e2ab')
    field.addColorStop(0.42, '#d9bd80'); field.addColorStop(0.78, '#bb9b56'); field.addColorStop(1, '#8a6f33')
  }
  context.fillStyle = field
  context.fillRect(0, 0, W, H)

  // The bevelled field the inscription is cut into.
  context.strokeStyle = opts?.tarnished ? 'rgba(255,240,196,0.16)' : 'rgba(86, 66, 26, 0.42)'
  context.lineWidth = 3
  context.strokeRect(10, 10, W - 20, H - 20)

  const total = lines.reduce((sum, l) => sum + l.size + (l.gap ?? 8), 0)
  let y = (H - total) / 2 + lines[0].size
  context.textAlign = 'center'
  lines.forEach((line) => {
    // Engraved: a light catch under a dark stroke.
    context.font = `600 ${line.size}px ${line.size > 30 ? DISPLAY : ENGRAVED}`
    context.letterSpacing = '4px'
    context.fillStyle = opts?.tarnished ? 'rgba(255, 246, 214, 0.22)' : 'rgba(255, 250, 220, 0.7)'
    context.fillText(line.text, W / 2, y + 2)
    context.fillStyle = opts?.tarnished ? '#2f2818' : '#241802'
    context.fillText(line.text, W / 2, y)
    context.letterSpacing = '0px'
    y += line.size + (line.gap ?? 8)
  })

  return finish(element, 8)
}
