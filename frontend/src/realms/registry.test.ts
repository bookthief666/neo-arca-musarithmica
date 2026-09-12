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
      text: 'Open the instrument.',
    })
    expect(getRealmGuidance('historica', 'deploy_rods', 'scholia')).toEqual({
      affordance: 'deploy_rods',
      text: 'Take a virga.',
    })
    expect(getRealmGuidance('historica', 'align_rods', 'scholia')).toEqual({
      affordance: 'align_rods',
      text: 'Bring the first bands into concord.',
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
    getRealmGuidance('historica', 'align_rods', 'quiet')

    expect(state).toEqual(snapshot)
    expect('realm' in state).toBe(false)
    expect('guidanceMode' in state).toBe(false)
  })
})
