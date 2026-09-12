import { useRef } from 'react'
import type { ColumnRodInstance, HistoricalSourceColumn, VoiceName } from '../instrument/types'

interface ColumnRodProps {
  rod: ColumnRodInstance
  source: HistoricalSourceColumn
  onMove: (offset: number) => void
}

/** Canonical drag sensitivity: one registered band per band-height of travel,
 *  so a dragged rod tracks the reader's finger exactly 1:1. */
export const BAND_DRAG_PIXELS = 46
const BAND_COUNT = 10
const VOICE_ORDER: VoiceName[] = ['cantus', 'altus', 'tenor', 'bassus']
const VOICE_MARK: Record<VoiceName, string> = { cantus: 'C', altus: 'A', tenor: 'T', bassus: 'B' }

function PitchFace({ content }: { content: unknown }) {
  if (!content || typeof content !== 'object' || !('rows' in content)) return null
  const rows = (content as { rows: Record<string, number[]> }).rows
  return (
    <div className="rod-face rod-face--pitch">
      {VOICE_ORDER.filter((voice) => rows[voice]).map((voice) => (
        <span className="rod-face__row" key={voice}>
          <b>{VOICE_MARK[voice]}</b>
          {rows[voice].map((value, index) => (
            <i key={index}>{value}</i>
          ))}
        </span>
      ))}
    </div>
  )
}

function RhythmFace({ content }: { content: unknown }) {
  if (!content || typeof content !== 'object' || !('glyphs' in content)) return null
  const typed = content as { glyphs: string[]; relative_minim_units: number[] }
  return (
    <div className="rod-face rod-face--rhythm">
      <span className="rod-face__row rod-face__row--glyphs" aria-hidden="true">
        {typed.glyphs.map((glyph, index) => (
          <i key={index} data-glyph={glyph}>{glyph === 'minim' ? '♩' : '\u{1D15D}'}</i>
        ))}
      </span>
      <span className="rod-face__row rod-face__row--units">
        {typed.relative_minim_units.map((unit, index) => (
          <i key={index}>{unit}</i>
        ))}
      </span>
    </div>
  )
}

export function ColumnRod({ rod, source, onMove }: ColumnRodProps) {
  const drag = useRef<{ y: number; offset: number; lastOffset: number } | null>(null)
  const activeBand = source.bands[rod.vertical_offset]
  const verified = activeBand.status === 'verified'
  const clamp = (value: number) => Math.max(0, Math.min(BAND_COUNT - 1, value))

  return (
    <article
      className={`column-rod column-rod--${source.kind}`}
      data-offset={rod.vertical_offset}
      data-band-status={activeBand.status}
      data-copy={rod.copy_index}
    >
      {/* Brass head: the part a hand actually grips. */}
      <div className="rod-head" aria-hidden="true">
        <span className="rod-head__knurl" />
        <span className="rod-head__mark">{source.kind === 'pitch' ? 'COLVMNA' : 'NOTÆ'}</span>
        <span className="rod-head__copy">EX. {rod.copy_index}</span>
      </div>

      <div className="rod-shaft">
        <button
          type="button"
          role="slider"
          className="rod-window"
          aria-label={`${source.label}, copy ${rod.copy_index}. Active ${activeBand.label}. Use up and down arrow keys or drag vertically.`}
          aria-valuemin={1}
          aria-valuemax={BAND_COUNT}
          aria-valuenow={rod.vertical_offset + 1}
          aria-valuetext={activeBand.label}
          onKeyDown={(event) => {
            if (event.key === 'ArrowUp') {
              event.preventDefault()
              onMove(clamp(rod.vertical_offset - 1))
            } else if (event.key === 'ArrowDown') {
              event.preventDefault()
              onMove(clamp(rod.vertical_offset + 1))
            } else if (event.key === 'Home') {
              event.preventDefault()
              onMove(0)
            } else if (event.key === 'End') {
              event.preventDefault()
              onMove(BAND_COUNT - 1)
            }
          }}
          onPointerDown={(event) => {
            drag.current = { y: event.clientY, offset: rod.vertical_offset, lastOffset: rod.vertical_offset }
            event.currentTarget.setPointerCapture(event.pointerId)
          }}
          onPointerMove={(event) => {
            if (!drag.current) return
            const delta = Math.round((event.clientY - drag.current.y) / BAND_DRAG_PIXELS)
            const nextOffset = clamp(drag.current.offset + delta)
            if (nextOffset === drag.current.lastOffset) return
            drag.current.lastOffset = nextOffset
            onMove(nextOffset)
          }}
          onPointerUp={(event) => {
            drag.current = null
            if (event.currentTarget.hasPointerCapture(event.pointerId)) {
              event.currentTarget.releasePointerCapture(event.pointerId)
            }
          }}
          onPointerCancel={() => { drag.current = null }}
        >
          <span className="visually-hidden">
            Band {rod.vertical_offset + 1} of {BAND_COUNT}. {verified ? 'Verified historical band on the transverse rule.' : 'Sealed band: the transverse reading is broken here.'}
          </span>

          <div className="rod-strip" style={{ ['--offset' as string]: String(rod.vertical_offset) }}>
            {source.bands.map((band) => (
              <div
                className={`rod-band ${band.status === 'verified' ? 'rod-band--verified' : 'rod-band--sealed'}`}
                key={band.index}
                data-band={band.index}
              >
                <span className="rod-band__index">{String(band.index).padStart(2, '0')}</span>
                {band.status === 'verified' ? (
                  source.kind === 'pitch' ? <PitchFace content={band.content} /> : <RhythmFace content={band.content} />
                ) : (
                  <span className="seal-mark">NON TRANSCRIPTVM</span>
                )}
              </div>
            ))}
          </div>

          {/* The reading aperture: where the transverse rule crosses this rod. */}
          <span className="rod-notch" aria-hidden="true">
            <span className="rod-notch__brass" />
            <span className="rod-notch__break" />
          </span>
        </button>

        {/* Ten machined detents down the rod's own edge. */}
        <div className="rod-detents" aria-hidden="true">
          {Array.from({ length: BAND_COUNT }, (_, index) => (
            <i key={index} className={index === rod.vertical_offset ? 'is-seated' : ''} data-detent={index + 1} />
          ))}
        </div>
      </div>

      <div className="rod-foot">
        <button
          type="button"
          className="rod-step"
          onClick={() => onMove(clamp(rod.vertical_offset - 1))}
          disabled={rod.vertical_offset === 0}
          aria-label="Move rod up one band"
        >
          <span aria-hidden="true">▲</span>
        </button>
        <span className="rod-foot__read" aria-hidden="true">{String(rod.vertical_offset + 1).padStart(2, '0')}</span>
        <button
          type="button"
          className="rod-step"
          onClick={() => onMove(clamp(rod.vertical_offset + 1))}
          disabled={rod.vertical_offset === BAND_COUNT - 1}
          aria-label="Move rod down one band"
        >
          <span aria-hidden="true">▼</span>
        </button>
      </div>
    </article>
  )
}
