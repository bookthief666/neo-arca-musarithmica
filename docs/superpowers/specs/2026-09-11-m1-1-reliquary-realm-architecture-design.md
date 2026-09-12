# M1.1 Reliquary Realm Architecture Design

## Purpose

M1.1 establishes the smallest production-grade presentation seam needed to make **Arca Historica / Reliquary** the canonical first interface realm while preserving a single authoritative instrument core. It also establishes a presentation-only guidance seam so the historical instrument can teach itself without introducing a second workflow state machine.

This design deliberately does **not** implement the final visual redesign. Browser-led visual iteration against Concept I — Reliquary Cabinet remains a subsequent implementation task.

## Starting authority

- Repository: `bookthief666/neo-arca-musarithmica`
- Parent branch: `feature/m1.0.1b-claude-visual-rescue`
- Required parent SHA: `4124ebba8931b3bcab1f406bcb4dc0ec15692925`
- M1.1 branch: `feature/m1.1-reliquary-realm`
- M0.9 historical kernel remains authoritative.
- Ghost/backend remains frozen and out of scope.

## Product model

The project will eventually support multiple interface realms over one instrument:

```text
                    SHARED INSTRUMENT CORE
                           |
          +----------------+----------------+
          |                |                |
    ARCA HISTORICA      NEO-ARCA      MODUS HAERETICUS
      Reliquary        Cybernetic        Transgressive
      Cabinet          Evolution           Mutation
```

A realm is **not** a separate app and is **not** musical authority. It may change presentation, motion, material language, guidance voice, and eventually selected interaction expression. It may not silently change historical source data, rod eligibility, alignment, tone logic, execution, provenance, or kernel output.

## Selected architectural approach

Use a **thin realm registry** rather than separate render trees or a generalized theme framework.

### Why

- Only Historica is approved and implemented now.
- The current reducer/action model is healthy and must remain canonical.
- A registry gives future Neo and Haeretica work a stable extension point without predicting their detailed layouts today.
- Realm-specific component variants can be added later only where real design divergence justifies them.
- This minimizes duplicated interaction, responsive, and accessibility logic.

## Realm domain

Create `frontend/src/realms/` with focused responsibilities.

### `types.ts`

Define:

```ts
export type ArcaRealmId = 'historica' | 'neo' | 'haeretica'
export type RealmAvailability = 'available' | 'future'

export interface ArcaRealmDefinition {
  id: ArcaRealmId
  label: string
  ceremonialLabel: string
  availability: RealmAvailability
  cssScope: string
  guidanceVoice: 'scholarly' | 'computational' | 'transgressive'
}
```

This type is presentation metadata only.

### `historica.ts`

Export the canonical Historica definition. Historica is the only realm with `availability: 'available'` in M1.1.

### `registry.ts`

Export a frozen registry containing:

- `historica` — available
- `neo` — future metadata stub only
- `haeretica` — future metadata stub only

Also export:

```ts
export const DEFAULT_REALM_ID: ArcaRealmId = 'historica'
export function getRealmDefinition(id: ArcaRealmId): ArcaRealmDefinition
```

No user-facing realm switcher is added in M1.1.

## Application seam

`App` receives or derives only a presentation realm id and exposes it at the top-level DOM boundary:

```html
<main data-realm="historica" ...>
```

The realm id must **not** enter:

- `InstrumentState`
- `InstrumentAction`
- `instrumentReducer`
- alignment requests
- historical kernel requests
- manifest/source data
- execution result objects

This separation is a hard invariant.

## CSS/token seam

The current material values already live primarily in `:root` custom properties. M1.1 should normalize them into semantic Historica realm tokens without materially redesigning the UI yet.

Use a scoped contract similar to:

```css
[data-realm='historica'] {
  --realm-wood-deep: ...;
  --realm-wood-mid: ...;
  --realm-brass: ...;
  --realm-brass-lit: ...;
  --realm-vellum: ...;
  --realm-vellum-bright: ...;
  --realm-ink: ...;
  --realm-ink-soft: ...;
  --realm-shadow: ...;
  --realm-authority-h0: ...;
  --realm-motion-mechanical: ...;
  --realm-motion-reading: ...;
  --realm-motion-reveal: ...;
}
```

Existing low-level aliases such as `--wood`, `--paper`, and `--brass` may temporarily point to these semantic realm tokens to avoid a risky CSS rewrite in the architecture checkpoint.

Future realms should override semantic realm tokens first. Component-specific divergence is added later only if tokens are insufficient.

## Guidance architecture

Guidance is presentation only. It is derived from the existing canonical `getNextAffordance()` output; it does not create a second progress model.

### Guidance mode

Define:

```ts
export type GuidanceMode = 'quiet' | 'scholia'
```

`quiet` suppresses visible explanatory copy while retaining accessibility announcements already derived from canonical state.

`scholia` allows short diegetic marginal phrases.

M1.1 may default to `scholia` for first-use presentation, but this preference must remain outside `InstrumentState`.

### Guidance entries

Define a pure Historica guidance mapping keyed by the existing `NextAffordance` type. Representative copy:

- `open_arca` -> `Open the instrument.`
- `focus_bank_i` -> `The first bank bears the verified corpus.`
- `open_cell_iv` -> `Cell IV preserves the operative fragment.`
- `deploy_rods` -> `Take a virga.`
- `place_held_rod` -> `Seat the carrier upon the rule.`
- `align_rods` -> `Bring the first bands into concord.`
- `engage_tone_ii` -> `Consult the Tone.`
- `read_transverse` -> `Read across the aligned band.`
- `await_execution` -> `The Arca is reading.`
- `inspect_revelation` -> `Four voices are disclosed.`
- `recover` -> `Restore the verified disposition.`

Exact copy may be lightly refined during implementation, but it must remain terse, diegetic, and non-instructional in tone.

### Selector

Expose a pure function conceptually equivalent to:

```ts
export function getRealmGuidance(
  realm: ArcaRealmId,
  affordance: NextAffordance,
  mode: GuidanceMode,
): RealmGuidance | null
```

It has no access to dispatch, reducer state mutation, manifest mutation, or execution clients.

## Teaching behavior

The visual implementation may later use `data-next-affordance` plus `getRealmGuidance()` to illuminate the next physical affordance and optionally show a small scholium.

The object should teach primarily through:

- exposed seams and handles
- empty destination sockets
- physical continuity/discontinuity of the transverse rule
- mechanical activation of Tone II
- progressive material emphasis

Text remains secondary.

No wizard, modal tutorial, progress stepper, `NEXT`, or `SKIP` UI is introduced.

## Historica visual authority

Concept I — Reliquary Cabinet is the art-direction reference for the subsequent visual pass.

Historica should eventually express:

- walnut/mahogany cabinet structure
- brass fittings and operable mechanisms
- vellum/paper historical surfaces
- dark ink
- restrained illumination
- visible Cell IV storage
- narrow physical carriers
- a carriage physically attached to the cabinet
- central transverse-reading mechanism
- mounted Mensa Tonographica in the lid
- subordinate provenance folio/seal

This architecture checkpoint only creates the seam; it does not attempt to reproduce Concept I through source-only editing.

## Historical truth boundary

Realm metadata and guidance may not alter historical truth.

### H0

Verified musical/source material remains unchanged.

### H1

Cabinet joinery, exact hardware, physical dimensions, material reconstruction, and interaction choreography may be clearly treated as restrained reconstruction.

### N1

Modern interface affordances, animation, responsive presentation, and the realm system itself are modern computational presentation.

No H1 or N1 element may be mislabeled as H0.

## Future Neo realm contract

Neo exists only as metadata with `availability: 'future'` in M1.1.

Later it may replace presentation qualities such as:

- wood -> advanced alloy/lacquer/glass
- ink -> luminous computational inscription
- brass channel -> cybernetic read rail
- paper manifestation -> living data surface

It must initially consume the same instrument actions and state selectors.

No Neo visual CSS or components are implemented in this architecture checkpoint.

## Future Haeretica realm contract

Haeretica exists only as metadata with `availability: 'future'` in M1.1.

It must **not** be implemented as a red/black skin now. Future Heretical presentation may correspond to genuinely altered musical law, so its UI should be integrated only when the musical authority boundary for that mode is explicitly defined.

No Haeretica CSS or components are implemented in this architecture checkpoint.

## Accessibility

Realm and guidance architecture must preserve:

- semantic controls
- keyboard operation
- slider semantics
- visible focus
- reduced-motion behavior
- screen-reader state announcements
- non-color-only meaning

Guidance copy cannot be the sole carrier of an actionable state.

## Testing invariants

Add focused tests that prove:

1. Historica is the default and only available M1.1 realm.
2. Neo and Haeretica are registered as future, not available.
3. Realm definitions are presentation metadata and are not part of `InstrumentState`.
4. `getRealmGuidance()` is a pure mapping from realm/affordance/mode.
5. `quiet` guidance returns no visible guidance.
6. Guidance selection does not dispatch or change reducer state.
7. Existing reducer and historical execution tests continue unchanged.
8. Existing full M1.0.1B verification gate remains green.

Avoid giant CSS snapshots.

## Files expected in the architecture checkpoint

Create:

- `frontend/src/realms/types.ts`
- `frontend/src/realms/historica.ts`
- `frontend/src/realms/registry.ts`
- `frontend/src/realms/guidance.ts`
- `frontend/src/realms/registry.test.ts`
- `frontend/src/realms/guidance.test.ts`

Modify narrowly:

- `frontend/src/App.tsx` — expose the active presentation realm and optional guidance output without entering reducer state.
- `frontend/src/styles.css` — introduce scoped Historica semantic tokens and aliases; no major visual redesign.

Do not modify:

- historical data
- M0.9 kernel
- Ghost/backend
- baseline refs

## Acceptance criteria for this checkpoint

The checkpoint is complete when:

- the branch cleanly identifies Historica as the canonical active realm;
- future Neo/Haeretica identifiers exist without unfinished UI;
- realm identity is visibly available to CSS/DOM but absent from musical state;
- diegetic guidance can be derived from canonical `NextAffordance` without creating another state machine;
- CSS has a semantic realm-token seam;
- focused realm/guidance tests pass;
- existing frontend and Python gates remain green;
- no material visual redesign is claimed;
- the branch is pushed cleanly for Claude to perform browser-led Reliquary rendering next.
