import { expect, it } from 'vitest'
import { CARRIAGE, CASE, VIRGA } from './dimensions'
import { CARRIER_READING_POSE, CARRIER_SEAT_Z, EVENT_READER_DETENTS } from './scene/stations'

it('keeps the fixed carrier seat inside the drawer and clear of the open case',() => {
  const back=CARRIAGE.travel+CARRIER_SEAT_Z-VIRGA.length/2
  const front=CARRIAGE.travel+CARRIER_SEAT_Z+VIRGA.length/2
  expect(back).toBeGreaterThanOrEqual(CARRIAGE.travel-CARRIAGE.depth/2)
  expect(front).toBeLessThanOrEqual(CARRIAGE.travel+CARRIAGE.depth/2)
  expect(back).toBeGreaterThanOrEqual(CASE.depth/2)
})

it('defines one operative carrier pose and exactly six inspection detents', () => {
  expect(CARRIER_READING_POSE).toEqual(expect.objectContaining({ channel: 0 }))
  expect(EVENT_READER_DETENTS).toHaveLength(6)
  expect(new Set(EVENT_READER_DETENTS).size).toBe(6)
})

it('keeps source print inside the active guide lips', () => {
  expect(VIRGA.printableWidth).toBeLessThan(VIRGA.width)
  expect(VIRGA.width).toBeLessThan(CARRIAGE.activeChannelWidth)
})

it('retains true desk scale in metres',() => {
  expect(CASE.width).toBeGreaterThan(0.2)
  expect(CASE.width).toBeLessThan(0.4)
  expect(CASE.height).toBeLessThan(0.2)
})
