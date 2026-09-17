import type { ReadingFrame } from '../../instrument/reading'

const VOICE_LABEL = {
  cantus: 'C',
  altus: 'A',
  tenor: 'T',
  bassus: 'B',
} as const

export interface ReadingLensDisplay {
  eventLabel: string
  railLabel: string
  voiceLabels: string[]
  durationLabel: string
  activeDegrees: number[]
}

export function eventReaderPositionFromLocalScalar(local: number, minLocal: number, maxLocal: number): number {
  if (![local, minLocal, maxLocal].every(Number.isFinite) || maxLocal <= minLocal) {
    throw new Error('Invalid event-reader scalar range.')
  }
  const clamped = Math.max(minLocal, Math.min(maxLocal, local))
  return Math.round(((clamped - minLocal) / (maxLocal - minLocal)) * 5)
}

export function buildReadingLensDisplay(frame: ReadingFrame): ReadingLensDisplay {
  const voiceOrder = ['cantus', 'altus', 'tenor', 'bassus'] as const
  return {
    eventLabel: `Event ${frame.eventNumber} of 6`,
    railLabel: 'EVENTVS I–VI · H1 INDEX',
    voiceLabels: voiceOrder.map((voice) => {
      const value = frame.voices[voice]
      return `${VOICE_LABEL[voice]} · ${value.degree} → ${value.pitchClass}`
    }),
    durationLabel: `${frame.duration.glyph} · ${frame.duration.relativeMinimUnits} relative minim units`,
    activeDegrees: Array.from(new Set(voiceOrder.map((voice) => frame.voices[voice].degree))).sort((a, b) => a - b),
  }
}
