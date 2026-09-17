# M1.2.1R — Tasks 1–4 architectural checkpoint

Date: 2026-09-17

This records automated engineering verification, not physical Fold acceptance or acceptance of the complete M1.2.1R milestone. Tasks 5–10 were not started.

## Authority and scope

- Implementation branch: `feature/m1.2.1r-historical-computation-rescue`.
- Starting local/remote HEAD: `107bcb8f0326d1a09847c396344bf6696452c6d0`.
- Accepted M1.2 ancestor: `7dc5e3c66e4602478d4f8a23f45f136db457f0e1`; ancestry verified.
- Documentation authority: `e9fa058be127a7f48bb1800b14bf576398af4857`, the September 16 rescue specification and implementation plan on the design branch.
- Last production-code commit: `d112e620c017419de08a37983751c594fe5b128f`.
- This record is an additional documentation commit. Its enclosing commit is the release checkpoint; the final delivery message records the verified local/remote SHA after push.
- Preserved staged test commits: `bfb88e888ece8d771d5f1271b7d552c3c7a98e08` and `107bcb8f0326d1a09847c396344bf6696452c6d0`.
- Rejected candidate `ccda572849e15c60dde5d6d8f6f7d8f65bde088d` was neither merged nor cherry-picked. No canonical branch was advanced.
- M0.9 kernel and historical JSON are unchanged. Diff against starting HEAD also shows no changes to either staged interaction/ownership test file.

The owner-approved order was Task 3A bootstrap → Task 1 atomic v2 migration → Task 2 presentation refinement → Task 3 scene integration → Task 4 reading boundary. There was no reset, rebase, merge, or baseline mutation.

## Implemented boundaries

1. **Task 3A:** pure translated-axis detent helper and presentation-only ownership store/context. No scene integration in this prerequisite commit.
2. **Task 1:** strict v2 manifest/reading/execution contracts; server-resolved carrier, edition, source and fixed Tone policy; content digest; normalized request fingerprint; runtime TypeScript decoding. The reducer and every direct consumer migrated together. No compatibility reducer, synthetic rods, action aliases, band state, or Tone unlock state remains.
3. **Task 2:** shared source inscriptions across semantic and canvas presentations, explicit H1 pairing/carrier, H0 mensural identities, derived relative-minim normalization, and causal/recovery guidance.
4. **Task 3 integration:** the actual event-reader hook invokes the helper with a world-space origin and unchanged local limits. Scene-local ownership suppresses orbit/pinch/wheel while grabbed and releases on pointer-up, cancel, lost capture, buttons lost off target, blur, and component/provider cleanup.
5. **Task 4:** fail-closed source and executed frames. All six events are checked, including source dimensions, identities, selection/witness, degree/pitch/duration/offset parity and source-cell references. Executed frames take their values from the M0.9 fragment. The reducer runs the parity boundary before exposing execution or provenance.

The event-reader mesh is a minimal integration handle. It is not the later computation lens or a claim of historical transverse reading.

## RED → GREEN evidence

At the starting HEAD, the prescribed command:

```text
npm test -- --run src/spatial/interaction.test.ts src/spatial/grabOwnership.test.tsx
interaction: 12 failed, 4 passed
ownership: suite failed to load
```

The failures were the intended missing `projectRayToLocalDetent` export and missing `grabOwnership.tsx` module. TypeScript reported those corresponding missing imports (TS2305/TS2307).

After Task 3A, the same unchanged suites passed 20 tests and typecheck passed. After scene integration, the final exact focused command again reported:

```text
✓ src/spatial/grabOwnership.test.tsx (4 tests)
✓ src/spatial/interaction.test.ts (16 tests)
Test Files  2 passed (2)
Tests       20 passed (20)
```

Additional RED observations before their production changes:
- 22 Python bridge tests failed against v1 output/missing v2 methods.
- Decoder suite could not import the absent decoder; six new carrier-model tests failed against the old reducer.
- Migrated App/component/accessibility tests failed against old direct consumers.
- Task-2 authority-label test failed on missing classified inscriptions.
- Scene interaction lifecycle suite failed on the missing integration module.
- Reading suite failed on the missing reading module.
- Reducer accepted an intentionally mismatched result before the parity guard; that regression is now green.
- Three unknown-field tests demonstrated prototype-named fields slipping through the decoder; own-property checks now reject them.

## Verification results

| Check | Result |
|---|---|
| Task-1 focused Python bridge + immutable kernel suite | 35 passed |
| Task-1 complete frontend checkpoint | 53 passed in 12 files |
| Task-1 TypeScript | Passed |
| Task-2 prescribed component/App/renderer/realm gate | 13 passed in 4 files |
| Task-2 TypeScript and lint | Passed |
| Task-3 interaction, ownership, lifecycle, renderer and semantic neighbors | 35 passed in 5 files |
| Task-3 exact staged suites, final rerun | 20 passed in 2 files |
| Task-3 TypeScript | Passed |
| Task-4 reading selector suite | 35 passed |
| Task-4 selector + reducer gate | 42 passed in 2 files |
| Final full Python suite | 572 passed; 2 dependency deprecation warnings |
| Final complete frontend suite | 104 passed in 14 files |
| Final TypeScript (`tsc -b`) | Passed |
| Final ESLint | Passed |
| Final production build | Passed |
| Live Vite-preview/Python bridge smoke | Manifest v2: HTTP 200; reading v2: HTTP 200, six events/eight relative units; unknown request field: HTTP 422 |
| `git diff --check` | Passed |
| Required removed-contract source scan | No matches |
| `document.body.dataset.arcaGrab` source scan | No matches |
| Immutable kernel, JSON and staged-test diff | Empty |

The Python environment used the repository's dependency files, including installation from `requirements.lock.txt`. No dependency manifest or lockfile changed.

Build output:
- Main JS: 248.45 kB, gzip 77.78 kB.
- Lazy SpatialArca JS: 903.55 kB, gzip 244.63 kB.
- CSS: 85.77 kB, gzip 18.13 kB.

Warnings retained: Vite's >500 kB chunk advisory; a multiple-Three.js-instance warning in the jsdom interaction harness; npm's environment `http-proxy` warning; two Python dependency deprecations. None is a measured Fold-performance result.

The exact removed-contract scan was:

```bash
rg -n "RodTemplate|ColumnRodInstance|state\\.rods|heldRodId|DEPLOY_ROD|RETRIEVE_ROD|PLACE_HELD_ROD|MOVE_ROD|align_rods|deploy_rods|place_held_rod|engage_tone_ii|historical_alignment_ready|tonal_resolution|read_transverse|rod_templates|rod_instances|toneEngaged|alignmentReady|isAlignmentReady|onDeployRod|onMoveRod|onEngageTone|toneAvailable" frontend/src
```

## Architectural findings and handoff debt for Tasks 5–8

- Task-1 dependency closure extended beyond the named consumers: provenance rendering, procedural texture generation, the individual virga mesh, and station tests also depended on the removed contract. Those migrated in the atomic commit.
- Old tests asserting three-carrier alignment and band selection were replaced by tests of the approved single-carrier contract. The two owner-staged regression files were preserved byte-for-byte.
- The legacy view is now a minimal truthful v2 consumer. The spatial shell retains accepted cabinet/lid/carriage geometry. Neither presentation has passed new visual or physical comprehension QA.
- Carrier face text is source-classified but remains on the inherited small physical geometry. Readability, printable dimensions, dormant capacity covers, and the full carrier presentation remain subsequent work.
- The inherited carriage still contains static cross-channel apparatus and a geometry-only band-length constant; there are no selectable bands or canonical band offsets. Task 5 must resolve that visual remnant without treating it as live combinatorial agency.
- The new event-reader handle proves scene input plumbing. It does not yet expose the full source → Tone lookup → result computation visually. Task 6 owns the lens, linked Tone emphasis, and spatial reading presentation.
- Camera framing and camera-director intervention remain inherited. Task 7 must establish macro-workbench readability and behavior under trusted touch.
- Semantic controls use the same reducer and cursor. Task 8 still needs fuller announcements, focus/continuity refinement, and actual screen-reader QA.
- Source/execution frame validation is available for later views and is already enforced before the reducer accepts a result. Future views must consume this boundary rather than compute another historical result.
- Generated carrier texture/material and Mensa texture disposal were added where migration touched resource ownership.
- The existing Vite bridge middleware still uses the old internal error identifier `historical_alignment_rejected` for HTTP rejection; the frontend consumes its human-readable message. Renaming that identifier can be handled separately if a public error contract is introduced.
- No browser visual review, Fold touch verification, TalkBack session, GPU profiling, or XR verification is claimed here.

## New implementation commits and files by task

The following inventory is taken directly from Git, in execution order:

```text
COMMIT 4416684e15c30bdeccf42bc14ca3db859f89fc00 feat(m1.2.1r): bootstrap translated detents and scene grab ownership

frontend/src/spatial/grabOwnership.tsx
frontend/src/spatial/interaction.ts
COMMIT f641d9045bf7c8643dc987723263124fc6dde8c6 feat(m1.2.1r): migrate the instrument atomically to reading v2

frontend/src/App.reliquary.test.tsx
frontend/src/App.test.tsx
frontend/src/App.tsx
frontend/src/components/ArcaCabinet.tsx
frontend/src/components/ColumnRod.test.tsx
frontend/src/components/ColumnRod.tsx
frontend/src/components/ProvenanceLeaf.tsx
frontend/src/components/WorkingRule.tsx
frontend/src/instrument/client.ts
frontend/src/instrument/contracts.test.ts
frontend/src/instrument/contracts.ts
frontend/src/instrument/model.test.ts
frontend/src/instrument/model.ts
frontend/src/instrument/types.ts
frontend/src/realms/guidance.ts
frontend/src/realms/registry.test.ts
frontend/src/spatial/AccessibleInstrumentControls.test.tsx
frontend/src/spatial/AccessibleInstrumentControls.tsx
frontend/src/spatial/SpatialArca.tsx
frontend/src/spatial/scene/Lid.tsx
frontend/src/spatial/scene/Virga.tsx
frontend/src/spatial/scene/Virgae.tsx
frontend/src/spatial/scene/stations.ts
frontend/src/spatial/stations.test.ts
frontend/src/spatial/textures.ts
frontend/src/test/fixtures.ts
scripts/arca_mechanica_bridge.py
tests/test_arca_mechanica_bridge.py
COMMIT df1931c5b27abbad0ad44369ef357bcb5d558c84 refactor(m1.2.1r): clarify source authority and reading meaning

frontend/src/components/ArcaCabinet.tsx
frontend/src/components/ColumnRod.test.tsx
frontend/src/components/ColumnRod.tsx
frontend/src/components/ProvenanceLeaf.tsx
frontend/src/components/VoiceManifestation.tsx
frontend/src/components/carrierInscription.ts
frontend/src/realms/guidance.ts
frontend/src/realms/registry.test.ts
frontend/src/spatial/textures.ts
COMMIT 017cd699cf74ab6a95af9977cd7a2a4e50fd872e fix(m1.2.1r): integrate translated reader grabs and scene ownership

frontend/src/spatial/SpatialArca.tsx
frontend/src/spatial/orbitInput.ts
frontend/src/spatial/readerInteraction.test.tsx
frontend/src/spatial/readerInteraction.ts
frontend/src/spatial/scene/EventReader.tsx
COMMIT d112e620c017419de08a37983751c594fe5b128f feat(m1.2.1r): validate source and executed event frames

frontend/src/instrument/contracts.test.ts
frontend/src/instrument/contracts.ts
frontend/src/instrument/model.test.ts
frontend/src/instrument/model.ts
frontend/src/instrument/reading.test.ts
frontend/src/instrument/reading.ts
```

The additional checkpoint-document commits change only this report.

## Publication blocker

The authorized push was attempted with `git push origin HEAD:refs/heads/feature/m1.2.1r-historical-computation-rescue` and failed:

```text
fatal: could not read Username for 'https://github.com': No such device or address
```

No Git credential helper, GH_TOKEN, GITHUB_TOKEN, GIT_ASKPASS, or SSH agent was configured. The available GitHub commit-creation tool does not expose author/committer timestamps or raw commit upload; replaying the changes through it would create different commit objects. That route was not used to replace this history.

Remote HEAD remains `107bcb8f0326d1a09847c396344bf6696452c6d0`. Local and remote HEAD are therefore **not equal**. Implementation and automated verification are complete, but publication is blocked on workspace GitHub authentication. The final local SHA and a verified Git bundle preserving the complete branch are provided in the delivery message.
