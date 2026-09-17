import { describe, expect, it } from 'vitest'
import { createInitialState } from '../instrument/model'
import { getRealmGuidance } from './guidance'
import { DEFAULT_REALM_ID, REALM_REGISTRY, getRealmDefinition } from './registry'

describe('Arca presentation realms', () => {
  it('keeps Historica as the only available realm and the canonical default', () => {
    expect(DEFAULT_REALM_ID).toBe('historica')
    expect(getRealmDefinition(DEFAULT_REALM_ID)).toMatchObject({
      id: 'historica',
      availability: 'available',
      guidanceVoice: 'scholarly',
    })

    const available = Object.values(REALM_REGISTRY)
      .filter((realm) => realm.availability === 'available')
      .map((realm) => realm.id)

    expect(available).toEqual(['historica'])
    expect(REALM_REGISTRY.neo.availability).toBe('future')
    expect(REALM_REGISTRY.haeretica.availability).toBe('future')
    expect(Object.isFrozen(REALM_REGISTRY)).toBe(true)
    expect(Object.values(REALM_REGISTRY).every(Object.isFrozen)).toBe(true)
  })

  it('derives terse Historica scholia from canonical affordances', () => {
    expect(getRealmGuidance('historica', 'open_arca', 'scholia')).toEqual({
      affordance: 'open_arca',
      text: 'The cabinet carries a critical edition of one Pinax-IV computation.',
    })
    expect(getRealmGuidance('historica', 'retrieve_carrier', 'scholia')).toEqual({
      affordance: 'retrieve_carrier',
      text: 'This H1 carrier joins separately verified pitch degrees and mensural identities.',
    })
    expect(getRealmGuidance('historica', 'inspect_event', 'scholia')).toEqual({
      affordance: 'inspect_event',
      text: 'Each event combines four scale degrees with one mensural duration.',
    })
  })

  it('suppresses visible scholia in quiet mode and for future realms', () => {
    expect(getRealmGuidance('historica', 'open_arca', 'quiet')).toBeNull()
    expect(getRealmGuidance('neo', 'open_arca', 'scholia')).toBeNull()
    expect(getRealmGuidance('haeretica', 'open_arca', 'scholia')).toBeNull()
  })

  it('cannot mutate instrument authority because guidance consumes no instrument state', () => {
    const state = createInitialState(false)
    const snapshot = structuredClone(state)

    getRealmGuidance('historica', 'focus_bank_i', 'scholia')
    getRealmGuidance('historica', 'inspect_event', 'quiet')

    expect(state).toEqual(snapshot)
    expect('realm' in state).toBe(false)
    expect('guidanceMode' in state).toBe(false)
  })
})
