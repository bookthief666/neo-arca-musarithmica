import { HISTORICA_REALM } from './historica'
import type { ArcaRealmDefinition, ArcaRealmId } from './types'

const NEO_REALM = Object.freeze<ArcaRealmDefinition>({
  id: 'neo',
  label: 'Neo-Arca',
  ceremonialLabel: 'Cybernetic Continuation',
  availability: 'future',
  cssScope: 'neo',
  guidanceVoice: 'computational',
})

const HAERETICA_REALM = Object.freeze<ArcaRealmDefinition>({
  id: 'haeretica',
  label: 'Modus Haereticus',
  ceremonialLabel: 'Transgressive Mutation',
  availability: 'future',
  cssScope: 'haeretica',
  guidanceVoice: 'transgressive',
})

export const REALM_REGISTRY = Object.freeze({
  historica: HISTORICA_REALM,
  neo: NEO_REALM,
  haeretica: HAERETICA_REALM,
}) satisfies Readonly<Record<ArcaRealmId, Readonly<ArcaRealmDefinition>>>

export const DEFAULT_REALM_ID: ArcaRealmId = 'historica'

export function getRealmDefinition(id: ArcaRealmId): Readonly<ArcaRealmDefinition> {
  return REALM_REGISTRY[id]
}
