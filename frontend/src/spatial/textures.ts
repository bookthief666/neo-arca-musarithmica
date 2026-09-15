import * as THREE from 'three'
import type { HistoricalManifest, HistoricalSourceColumn, VoiceName } from '../instrument/types'
import { VIRGA } from './dimensions'

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
  context.fillText(`TESTIS IMPRESSVS · p. ${manifest.cell.printed_page}`, W / 2, H - 62)
  context.letterSpacing = '0px'

  return finish(element, 16)
}

const VOICE_ORDER: VoiceName[] = ['cantus', 'altus', 'tenor', 'bassus']
const VOICE_MARK: Record<VoiceName, string> = { cantus: 'C', altus: 'A', tenor: 'T', bassus: 'B' }

/**
 * THE FACE OF A VIRGA, drawn from that column's own bands.
 *
 * Ten bands run down the strip in canonical order. A verified band prints its
 * real content — the four voice rows for a pitch column, glyphs and relative
 * minim units for the rhythm column. An untranscribed band prints as ruled but
 * empty scholarship: crosshatched, stamped NON TRANSCRIPTVM. Nothing is
 * invented to fill the gap, because the gap is the historical fact.
 */
export function makeVirgaTexture(source: HistoricalSourceColumn) {
  const BAND = 172
  const W = 320
  const H = BAND * VIRGA.bandCount
  const { element, context } = canvas(W, H)
  layVellum(context, W, H)

  source.bands.forEach((band, index) => {
    const top = index * BAND
    const mid = top + BAND / 2

    // Band rule.
    context.strokeStyle = RULE
    context.lineWidth = 2
    context.beginPath()
    context.moveTo(0, top + 0.5)
    context.lineTo(W, top + 0.5)
    context.stroke()

    // The band's own index, running down the left margin.
    context.save()
    context.translate(22, mid)
    context.rotate(-Math.PI / 2)
    context.fillStyle = INK_MUTED
    context.font = `20px ${ENGRAVED}`
    context.textAlign = 'center'
    context.fillText(String(band.index).padStart(2, '0'), 0, 0)
    context.restore()

    if (band.status !== 'verified' || !band.content) {
      // Archival crosshatch: ruled, empty, and plainly not yet transcribed.
      context.save()
      context.beginPath()
      context.rect(44, top + 6, W - 56, BAND - 12)
      context.clip()
      context.strokeStyle = 'rgba(112, 88, 52, 0.22)'
      context.lineWidth = 1
      for (let d = -BAND; d < W + BAND; d += 13) {
        context.beginPath()
        context.moveTo(44 + d, top)
        context.lineTo(44 + d + BAND, top + BAND)
        context.stroke()
        context.beginPath()
        context.moveTo(44 + d + BAND, top)
        context.lineTo(44 + d, top + BAND)
        context.stroke()
      }
      context.restore()
      context.fillStyle = 'rgba(86, 68, 44, 0.92)'
      context.font = `19px ${ENGRAVED}`
      context.textAlign = 'center'
      context.letterSpacing = '2px'
      context.fillText('NON', W / 2 + 20, mid - 8)
      context.fillText('TRANSCRIPTVM', W / 2 + 20, mid + 18)
      context.letterSpacing = '0px'
      return
    }

    context.textAlign = 'center'
    if (source.kind === 'pitch' && 'rows' in band.content) {
      const rows = band.content.rows
      const voices = VOICE_ORDER.filter((voice) => rows[voice])
      const rowH = (BAND - 22) / voices.length
      voices.forEach((voice, r) => {
        const y = top + 26 + rowH * r
        context.fillStyle = INK_MUTED
        context.font = `17px ${ENGRAVED}`
        context.textAlign = 'left'
        context.fillText(VOICE_MARK[voice], 46, y)
        context.fillStyle = INK
        context.font = `27px ${ENGRAVED}`
        context.textAlign = 'center'
        const values = rows[voice]
        values.forEach((value, c) => {
          const x = 84 + ((W - 104) / values.length) * (c + 0.5)
          context.fillText(String(value), x, y)
        })
      })
    } else if ('glyphs' in band.content) {
      const { glyphs, relative_minim_units: units } = band.content
      const step = (W - 104) / glyphs.length
      glyphs.forEach((g, c) => {
        const x = 84 + step * (c + 0.5)
        context.fillStyle = INK
        context.font = `34px ${DISPLAY}`
        context.fillText(g === 'minim' ? '♩' : '\u{1D15D}', x, mid - 6)
        context.fillStyle = INK_MUTED
        context.font = `20px ${ENGRAVED}`
        context.fillText(String(units[c]), x, mid + 30)
      })
    }
  })

  return finish(element, 16)
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

/**
 * A channel's band index: the ten canonical offsets written I..X down a slim
 * engraved strip beside the channel.
 *
 * ONE texture per scale, not ten labels. The reader needs to be able to count
 * the stations a virga can occupy before being told to bring one to band I —
 * an instruction that means nothing if the bands themselves are invisible.
 * Drawn in the same engraved hand as the cabinet's other brass, so it reads as
 * part of the instrument rather than as an overlay on it.
 */
export function makeDetentScaleTexture(count: number) {
  const ROMAN = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X']
  const cell = 64
  const { element, context } = canvas(96, cell * count)
  const h = cell * count

  context.fillStyle = '#6d5730'
  context.fillRect(0, 0, 96, h)
  // A brushed grain along the strip, so it reads as metal rather than paper.
  for (let i = 0; i < 160; i += 1) {
    const y = Math.random() * h
    context.strokeStyle = `rgba(255, 233, 186, ${0.02 + Math.random() * 0.05})`
    context.lineWidth = 0.6
    context.beginPath()
    context.moveTo(0, y)
    context.lineTo(96, y)
    context.stroke()
  }

  context.textAlign = 'center'
  context.textBaseline = 'middle'
  for (let index = 0; index < count; index += 1) {
    // Band I sits at the FOOT of the virga, which is the -Z end of the channel,
    // so the strip counts in the same direction the rod's own bands run.
    const y = index * cell + cell / 2
    context.strokeStyle = 'rgba(38, 26, 10, 0.5)'
    context.lineWidth = 2
    context.beginPath()
    context.moveTo(6, index * cell)
    context.lineTo(90, index * cell)
    context.stroke()

    const numeral = ROMAN[index] ?? String(index + 1)
    context.font = `600 ${numeral.length > 3 ? 24 : 30}px ${ENGRAVED}`
    context.fillStyle = 'rgba(32, 22, 8, 0.82)'
    context.fillText(numeral, 48, y + 1)
    context.fillStyle = 'rgba(255, 238, 200, 0.5)'
    context.fillText(numeral, 48, y)
  }

  return finish(element)
}

/**
 * A small engraved legend for a piece of operating hardware — TONVS II beside
 * the selector, LECTIO on the carriage apron.
 *
 * These name the two acts the reader has to perform last, and they are cut
 * into the instrument rather than floated over it, so the machine says what
 * its controls are for in its own voice.
 */
export function makeLegendTexture(lines: string[], opts?: { tarnished?: boolean }) {
  const { element, context } = canvas(256, 128)
  const dark = opts?.tarnished ?? false

  const ground = context.createLinearGradient(0, 0, 0, 128)
  ground.addColorStop(0, dark ? '#5a4a28' : '#8a7038')
  ground.addColorStop(0.5, dark ? '#6b5730' : '#a58747')
  ground.addColorStop(1, dark ? '#4e4023' : '#7d6531')
  context.fillStyle = ground
  context.fillRect(0, 0, 256, 128)

  context.textAlign = 'center'
  context.textBaseline = 'middle'
  const step = 128 / (lines.length + 1)
  lines.forEach((line, index) => {
    const y = step * (index + 1)
    const size = index === 0 ? 34 : 44
    context.font = `600 ${size}px ${ENGRAVED}`
    context.letterSpacing = '4px'
    // Cut, then catch the light on the upper edge: an engraving, not a print.
    context.fillStyle = 'rgba(30, 20, 6, 0.85)'
    context.fillText(line, 128, y + 2)
    context.fillStyle = dark ? 'rgba(220, 200, 160, 0.35)' : 'rgba(255, 240, 205, 0.62)'
    context.fillText(line, 128, y)
  })
  context.letterSpacing = '0px'

  return finish(element)
}
