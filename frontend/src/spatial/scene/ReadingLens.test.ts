import { expect, it } from 'vitest'
import { manifestFixture } from '../../test/fixtures'
import { getSourceReadingFrame } from '../../instrument/reading'
import { buildReadingLensDisplay, eventReaderPositionFromLocalScalar } from './readingLensModel'

it.each([
  [-0.05, 0], [-0.03, 1], [-0.01, 2], [0.01, 3], [0.03, 4], [0.05, 5],
])('maps local scalar %f to event position %i', (local, position) => {
  expect(eventReaderPositionFromLocalScalar(local, -0.05, 0.05)).toBe(position)
})

it('builds the complete event-six display from the validated source frame', () => {
  const display = buildReadingLensDisplay(getSourceReadingFrame(manifestFixture, 5))
  expect(display.eventLabel).toBe('Event 6 of 6')
  expect(display.voiceLabels).toEqual([
    'C · 3 → Bb', 'A · 7 → F#', 'T · 5 → D', 'B · 3 → Bb',
  ])
  expect(display.durationLabel).toBe('semibreve · 2 relative minim units')
})

it('labels the rail as an H1 event index rather than historical transverse reading', () => {
  const display = buildReadingLensDisplay(getSourceReadingFrame(manifestFixture, 0))
  expect(display.railLabel).toBe('EVENTVS I–VI · H1 INDEX')
  expect(display.railLabel.toLowerCase()).not.toContain('transverse')
})
