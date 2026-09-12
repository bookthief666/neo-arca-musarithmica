# M1.1 Reliquary Realm Architecture Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Establish the smallest production realm/guidance seam for Arca Historica without changing musical authority or attempting the final Concept-I visual redesign.

**Architecture:** Add a thin `frontend/src/realms/` registry with Historica as the only available realm and Neo/Haeretica as future metadata. Guidance is a pure presentation mapping from the existing `InstrumentAffordance`; realm/guidance never enter `InstrumentState`, reducer actions, historical requests, or kernel output. `App` exposes the active realm and guidance metadata at the top-level DOM boundary, while CSS receives semantic Historica token aliases.

**Tech Stack:** React 19, TypeScript 5.9, Vitest 3, CSS custom properties.

**Spec:** `docs/superpowers/specs/2026-09-11-m1-1-reliquary-realm-architecture-design.md`

## Global Constraints

- Start from `feature/m1.1-reliquary-realm`, parented by `4124ebba8931b3bcab1f406bcb4dc0ec15692925`.
- Do not modify `InstrumentState`, `InstrumentAction`, historical source data, M0.9 kernel requests, or Ghost/backend behavior.
- `historica` is the only available realm in M1.1; `neo` and `haeretica` are metadata-only future entries.
- No user-facing realm switcher in this checkpoint.
- No final visual redesign, new audio, MIDI, Ghost, XR, corpus expansion, Neo generation, or Heretical musical law.
- Guidance is derived from existing `InstrumentAffordance` and remains presentation-only.

---

### Task 1: Realm registry and guidance contract

**Files:**
- Create: `frontend/src/realms/types.ts`
- Create: `frontend/src/realms/historica.ts`
- Create: `frontend/src/realms/registry.ts`
- Create: `frontend/src/realms/guidance.ts`
- Create/Test: `frontend/src/realms/registry.test.ts`

**Interfaces:**
- Consumes: `InstrumentAffordance` from `frontend/src/instrument/types.ts` as a type only.
- Produces: `ArcaRealmId`, `ArcaRealmDefinition`, `GuidanceMode`, `RealmGuidance`, `DEFAULT_REALM_ID`, `REALM_REGISTRY`, `getRealmDefinition()`, `getRealmGuidance()`.

- [ ] Write tests proving Historica is the default/only available realm, Neo/Haeretica are future-only, registry values are immutable metadata, quiet guidance returns `null`, and Historica scholia maps canonical affordances to terse copy.
- [ ] Verify the test fails because the realm modules do not yet exist.
- [ ] Implement the minimal typed realm registry and pure guidance mapping.
- [ ] Run the realm test and confirm it passes.

### Task 2: App boundary and Historica semantic tokens

**Files:**
- Modify/Test: `frontend/src/App.test.tsx`
- Modify: `frontend/src/App.tsx`
- Modify: `frontend/src/styles.css`

**Interfaces:**
- Consumes: `DEFAULT_REALM_ID`, `getRealmDefinition()`, `getRealmGuidance()`.
- Produces: `data-realm="historica"`, `data-realm-guidance`, `data-guidance-mode="scholia"` on the application boundary; Historica-scoped semantic CSS custom properties.

- [ ] Add App tests asserting the canonical realm/guidance metadata appears without changing the existing opening interaction.
- [ ] Verify the new App assertion fails before production wiring.
- [ ] Wire the constant Historica realm and derived guidance into `App` without touching reducer state or execution requests.
- [ ] Add `[data-realm='historica']` semantic realm tokens and map the current low-level material/motion aliases through them with no intended visual redesign.
- [ ] Run App tests and the realm tests.

### Task 3: Checkpoint verification and handoff

**Files:**
- No new runtime surface unless verification exposes a defect.

- [ ] Run `npm test`, `npm run typecheck`, `npm run lint`, and `npm run build` from `frontend/`.
- [ ] Run `bash scripts/verify_m1_0_1b.sh` from repository root when the full checkout is available.
- [ ] Confirm the diff does not touch historical data, kernel code, Ghost/backend, or instrument reducer/types.
- [ ] Commit/push the architecture checkpoint on `feature/m1.1-reliquary-realm`.
- [ ] Hand Claude only the remaining Concept-I browser-led visual implementation.
