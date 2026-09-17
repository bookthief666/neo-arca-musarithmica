import { VIRGA } from '../dimensions'

/** Fixed carriage-local seat of the single critical-edition carrier. */
export const CARRIER_SEAT_Z = 0

/** The one valid H1 operating pose. Channel is mechanical identity, not musical choice. */
export const CARRIER_READING_POSE = {
  channel: 0,
  z: CARRIER_SEAT_Z,
} as const

/** Six inspection positions across the source excerpt; not historical bands. */
const EVENT_MIN = -VIRGA.length * 0.36
const EVENT_MAX = VIRGA.length * 0.36
export const EVENT_READER_DETENTS = Array.from(
  { length: 6 },
  (_, index) => EVENT_MIN + (EVENT_MAX - EVENT_MIN) * index / 5,
) as readonly number[]

export const EVENT_READER_LOCAL_MIN = EVENT_MIN
export const EVENT_READER_LOCAL_MAX = EVENT_MAX
