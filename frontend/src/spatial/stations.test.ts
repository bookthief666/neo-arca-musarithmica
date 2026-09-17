import { expect, it } from 'vitest'
import { CARRIAGE, CASE, VIRGA } from './dimensions'
import { CARRIER_SEAT_Z } from './scene/stations'
it('keeps the fixed carrier seat inside the drawer and clear of the open case',() => {
  const back=CARRIAGE.travel+CARRIER_SEAT_Z-VIRGA.length/2
  const front=CARRIAGE.travel+CARRIER_SEAT_Z+VIRGA.length/2
  expect(back).toBeGreaterThanOrEqual(CARRIAGE.travel-CARRIAGE.depth/2)
  expect(front).toBeLessThanOrEqual(CARRIAGE.travel+CARRIAGE.depth/2)
  expect(back).toBeGreaterThanOrEqual(CASE.depth/2)
})
it('retains true desk scale in metres',() => {
  expect(CASE.width).toBeGreaterThan(0.2)
  expect(CASE.width).toBeLessThan(0.4)
  expect(CASE.height).toBeLessThan(0.2)
})
