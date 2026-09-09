# UNCERTAINTIES.md — What we do not know

Open questions, recorded rather than resolved by invention. Anything here is a thing the
software must not assert.

---

## 0. The governing limitation of this pass

Research was done from an environment that **blocks image and page fetches** from
archive.org, Wikipedia, arca1650.info, andrewcashner.com, Zenodo and museum sites. We
consulted scholarly *description*; we did not read the 1650 text or see the engraving.

Everything in §§1–4 is open largely because of that. A session with unrestricted egress
should be able to close much of it in an afternoon.

## 1. Terminology

**Is *tariffa* Kircher's word for the rods?** — **UNRESOLVED, and we doubt it.**

The project brief describes the slats as "often described as *tariffae*". No source we
reached uses the word. Confirmed Latin: *arca*, *syntagma*, *pinax*, *musarithmus*,
*receptaculum*. English descriptions say slats, staves, tablets, rods, sliding panels.

*Action:* prefer *slat*/*rod*/*tablet* and *pinax*. If the interface wants "tariffa" for
flavour, label it N1. Do not attribute it to Kircher.

**What does Kircher call one column of numbers?** Unresolved; *musarithmus* covers the
tables collectively.

## 2. Structure and contents

- **Exactly how many *toni*?** Twelve, per one secondary source. Not counted in the
  primary text by us.
- **What are the twelve *toni*, concretely?** Their finals, ambitus and any affective
  associations — completely unknown to us.
- **How many *pinakes* in syntagma II?** We have eleven for syntagma I and an intended ten
  for syntagma III; syntagma II we never found.
- **Why twelve *receptacula* for eleven *pinakes*?** Kircher does not say, and neither can
  we.
- **The complete list of poetic metres.** We have four names (Euripidean, Anacreontic,
  Archilochian, Sapphic) out of an unknown total.
- **The tables themselves.** We hold **none** of the actual numbers. This is the blocking
  gap for ARCA HISTORICA.
- **How the four voices are laid out within a column** — one number per voice per syllable
  is our reading (H1), but the precise arrangement on the slat is unseen.
- **How rhythm lists pair with pitch columns.** That they are separate is documented; how
  a user pairs a particular rhythm with a particular column is not established.

## 3. The physical object

Every question in `VISUAL_RECONSTRUCTION.md` §2 is open: dimensions, timber, lid
mechanism, compartment construction, slat size, whether inscriptions are printed labels or
inked or engraved, metal fittings, the layout of a slat's face.

The one figure we have — "seventy-seven small sliding panels, one to two and a half
centimetres" — comes from a single secondary source, reads oddly as a measurement, and
**should not be built to**.

## 4. Surviving examples

- Which institution holds which cabinet, confirmed against catalogue records.
- Whether Pepys's example is still at the Pepys Library.
- How the four known examples differ from each other and from the book.
- What the Puebla example's "practical selection" of tables consists of, and what that
  implies about how the device was really used.

## 5. Musical questions our engine papers over

- **Did Kircher's tables observe a consistent counterpoint doctrine?** We assume the
  pre-composed progressions are grammatical (they must be, for his claim to hold), but we
  have not examined them, so we cannot say what rules they follow. Our Orthodox profile is
  therefore **not** derived from Kircher's practice — it is a modern construction that we
  believe is compatible with it.
- **What did Kircher expect for *musica ficta*?** Left to the performer; how much was
  assumed is unclear.
- **How were the *toni* meant to interact with the tables?** We assume degree-plus-tonus;
  whether transposition or ambitus constraints applied is unknown.
- **Cadences.** We know the period used contrapuntal clausulae, and we know we implement
  chord pairs instead. What we do *not* know is what cadential formulae Kircher's own
  tables actually contain.

## 6. Things we have decided rather than discovered

Recorded here so they are not mistaken for findings:

- Seven modern modes instead of twelve *toni* — a design choice (N1).
- Locrian's IV→i(dim) close — invented, because our own mode set includes a mode that
  cannot cadence conventionally (N1).
- The semantic lexicon's axis weights — authored by us, tuned by ear, with no external
  validation. They are inspectable and deterministic, but they are not *right* in any
  measurable sense.
- SATB ranges — defensible modern working ranges, not Kircher's.
- Modus Hæreticus in its entirety (HÆRETIC).

## 7. What would close the most, fastest

1. **A scan of Book VIII of *Musurgia universalis*.** Closes most of §§1–2 and the
   cadence question in §5.
2. **The plate facing p. 185, vol. II.** Closes much of §3.
3. **A museum catalogue record for the Wolfenbüttel cabinet.** Closes §4.
4. **Our own transcription of one *pinax*.** Unblocks a genuine ARCA HISTORICA — and one
   table is enough to prove the architecture before transcribing the rest.
