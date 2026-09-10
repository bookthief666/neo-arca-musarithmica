import { useRef } from 'react'
import type { ColumnRodInstance, HistoricalSourceColumn } from '../instrument/types'

interface ColumnRodProps {
  rod: ColumnRodInstance
  source: HistoricalSourceColumn
  onMove: (offset: number) => void
}

function pitchRows(content: unknown) {
  if (!content || typeof content !== 'object' || !('rows' in content)) return null
  const rows = (content as { rows: Record<string, number[]> }).rows
  return (
    <div className="rod-pitch-grid">
      {Object.entries(rows).map(([voice, values]) => (
        <span key={voice}><b>{voice.slice(0, 1).toUpperCase()}</b>{values.join(' ')}</span>
      ))}
    </div>
  )
}

function rhythmRow(content: unknown) {
  if (!content || typeof content !== 'object' || !('glyphs' in content)) return null
  const typed = content as { glyphs: string[]; relative_minim_units: number[] }
  return (
    <div className="rod-rhythm-grid">
      <span aria-hidden="true">♩ ♩ ♩ ♩ 𝅝 𝅝</span>
      <small>{typed.relative_minim_units.join(' · ')}</small>
    </div>
  )
}

export function ColumnRod({ rod, source, onMove }: ColumnRodProps) {
  const drag = useRef<{ y: number; offset: number; lastOffset: number } | null>(null)
  const activeBand = source.bands[rod.vertical_offset]

  return (
    <div
      className={`column-rod column-rod--${source.kind}`}
      data-offset={rod.vertical_offset}
      data-band-status={activeBand.status}
    >
      <div className="rod-cap">
        <span>{source.kind === 'pitch' ? 'COLVMNA' : 'NOTÆ'}</span>
        <small>EX. {rod.copy_index}</small>
      </div>
      <button
        type="button"
        role="slider"
        className="rod-window"
        aria-label={`${source.label}, copy ${rod.copy_index}. Active ${activeBand.label}. Use up and down arrow keys or drag vertically.`}
        aria-valuemin={1}
        aria-valuemax={10}
        aria-valuenow={rod.vertical_offset + 1}
        aria-valuetext={activeBand.label}
        onKeyDown={(event) => {
          if (event.key === 'ArrowUp') {
            event.preventDefault()
            onMove(rod.vertical_offset - 1)
          } else if (event.key === 'ArrowDown') {
            event.preventDefault()
            onMove(rod.vertical_offset + 1)
          } else if (event.key === 'Home') {
            event.preventDefault()
            onMove(0)
          } else if (event.key === 'End') {
            event.preventDefault()
            onMove(9)
          }
        }}
        onPointerDown={(event) => {
          drag.current = { y: event.clientY, offset: rod.vertical_offset, lastOffset: rod.vertical_offset }
          event.currentTarget.setPointerCapture(event.pointerId)
        }}
        onPointerMove={(event) => {
          if (!drag.current) return
          const delta = Math.round((event.clientY - drag.current.y) / 34)
          const nextOffset = Math.max(0, Math.min(9, drag.current.offset + delta))
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
        <span className="visually-hidden">Active band {rod.vertical_offset + 1} of 10.</span>
        <div className="rod-strip" style={{ transform: `translateY(${117 - rod.vertical_offset * 48}px)` }}>
          {source.bands.map((band) => (
            <div
              className={`rod-band ${band.status === 'verified' ? 'rod-band--verified' : 'rod-band--sealed'}`}
              key={band.index}
            >
              <span className="rod-band__index">{String(band.index).padStart(2, '0')}</span>
              {band.status === 'verified' ? (
                source.kind === 'pitch' ? pitchRows(band.content) : rhythmRow(band.content)
              ) : (
                <span className="seal-mark">NON TRANSCRIPTVM</span>
              )}
            </div>
          ))}
        </div>
      </button>
      <div className="rod-steps" aria-label={`Move ${source.label} copy ${rod.copy_index}`}>
        <button type="button" onClick={() => onMove(rod.vertical_offset - 1)} aria-label="Move rod up one band">↑</button>
        <span>{String(rod.vertical_offset + 1).padStart(2, '0')}</span>
        <button type="button" onClick={() => onMove(rod.vertical_offset + 1)} aria-label="Move rod down one band">↓</button>
      </div>
    </div>
  )
}
