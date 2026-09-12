import type { InstrumentAffordance } from '../instrument/types'

export type ArcaRealmId = 'historica' | 'neo' | 'haeretica'
export type RealmAvailability = 'available' | 'future'
export type RealmGuidanceVoice = 'scholarly' | 'computational' | 'transgressive'
export type GuidanceMode = 'quiet' | 'scholia'

export interface ArcaRealmDefinition {
  id: ArcaRealmId
  label: string
  ceremonialLabel: string
  availability: RealmAvailability
  cssScope: string
  guidanceVoice: RealmGuidanceVoice
}

export interface RealmGuidance {
  affordance: InstrumentAffordance
  text: string
}
