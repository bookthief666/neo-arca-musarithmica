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

  it('derives concrete first-use Historica scholia from canonical affordances', () => {
    // Each line names the PART and the ACT. "Take a virga" and "Bring the
    // first bands into concord" are accurate and teach nothing: a first-time
    // reader does not yet know what a virga or a band is, or where either is.
    const say = (affordance: Parameters<typeof getRealmGuidance>[1]) =>
      getRealmGuidance('historica', affordance, 'scholia')?.text

    expect(say('open_arca')).toBe('Open the instrument.')
    expect(say('focus_bank_i')).toBe('Open Bank I.')
    expect(say('open_cell_iv')).toBe('Open Cell IV; the verified virgae are stored within.')
    expect(say('deploy_rods')).toBe('Lift a virga from its socket.')
    expect(say('place_held_rod')).toBe('Seat the lifted virga in the illuminated channel.')
    expect(say('align_rods')).toBe('Slide each virga until band I lies beneath the reader.')
    expect(say('engage_tone_ii')).toBe('The rule is concordant. Engage Tone II.')
    expect(say('read_transverse')).toBe('Tone II is set. Operate LECTIO.')
    expect(say('await_execution')).toBe('The Arca is reading.')
    expect(say('inspect_revelation')).toBe('Four voices are disclosed.')
    expect(say('recover')).toBe('The disposition is preserved; restore the reading.')

    expect(getRealmGuidance('historica', 'open_arca', 'scholia')).toEqual({
      affordance: 'open_arca',
      text: 'Open the instrument.',
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
