"""models.py -- The API boundary.

Pydantic v2 request and response schemas.  No engine internals cross this line: every
dataclass in ``kircher_engine`` / ``constraints`` / ``semantics`` is projected into an
explicit, documented model here, so the wire format is a contract rather than an
accident of the implementation.

The response is shaped for the two consumers Phase 2 will bring:

* **THE VOICE** (Tone.js) reads ``score.voices`` -- four independently addressable
  event lists with absolute offsets in quarter-lengths, plus the tempo and meter needed
  to convert them to seconds.
* **THE SKIN & EYE** (React / Three.js) reads ``semantics``, ``score.progression``,
  ``score.phrases`` and ``validation.violations`` -- everything needed to draw the
  tariffa slats, the four voice traces and the rule diagnostics.
"""

from __future__ import annotations

import warnings
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator

from constraints import Intent, Severity
from rhythm import SUPPORTED_METERS
from theory import ModeName, TheoryError, normalize_note_name

MODE_NAMES = tuple(m.value for m in ModeName)

#: Reported in responses; kept here so this module stays decoupled from the engine.
ENGINE_NAME = "neo-arca-musarithmica"


# --------------------------------------------------------------------------------------
# Request
# --------------------------------------------------------------------------------------


class ComposeRequest(BaseModel):
    """A request to the Arca.

    Only ``text`` is required.  Every other field overrides what the Polygraphia stage
    would otherwise infer from the text; leave a field ``null`` to let the semantics
    decide it.
    """

    model_config = ConfigDict(extra="forbid", json_schema_extra={
        "example": {
            "text": "Sorrowful lament beneath a dying winter sun",
            "seed": 418,
            "mode": None,
            "tonic": None,
            "tempo": None,
            "measures": 8,
            "meter": "4/4",
            "heretical": False,
        }
    })

    text: str = Field(
        ..., min_length=1, max_length=600,
        description="Free text interpreted by the Polygraphia semantic stage.",
    )
    seed: Optional[Union[int, str]] = Field(
        None,
        description="Deterministic seed. Integers are used directly; strings are "
                    "hashed stably. Omit to derive a seed from the request itself.",
    )
    mode: Optional[str] = Field(
        None, description=f"One of: {', '.join(MODE_NAMES)}. Overrides the semantics."
    )
    tonic: Optional[str] = Field(
        None, description="The final, e.g. 'D', 'Bb', 'F#'. Overrides the semantics."
    )
    tempo: Optional[int] = Field(
        None, ge=30, le=240, description="Beats per minute. Overrides the semantics."
    )
    measures: int = Field(8, ge=1, le=64, description="Length of the composition.")
    meter: Optional[str] = Field(
        None, description=f"One of: {', '.join(SUPPORTED_METERS)}."
    )
    phrase_measures: Optional[int] = Field(
        None, ge=1, le=16, description="Measures per phrase. Overrides the semantics."
    )
    density: Optional[float] = Field(
        None, ge=0.0, le=1.0,
        description="Rhythmic density 0..1. Overrides the semantics.",
    )
    heretical: Optional[bool] = Field(
        None,
        description="Force MODUS HAERETICUS on or off. Omit to let the text decide.",
    )

    @field_validator("seed", mode="before")
    @classmethod
    def _seed_not_bool(cls, value: object) -> object:
        # Must run *before* coercion: pydantic's smart union would otherwise widen
        # ``True`` into the integer 1 and silently accept it as a seed.
        if isinstance(value, bool):
            raise ValueError("seed must be an integer or a string, not a boolean")
        return value

    @field_validator("text")
    @classmethod
    def _text_not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("text must contain at least one non-whitespace character")
        return value

    @field_validator("mode")
    @classmethod
    def _known_mode(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        lowered = value.strip().lower()
        if lowered not in MODE_NAMES:
            raise ValueError(
                f"unknown mode {value!r}; expected one of {', '.join(MODE_NAMES)}"
            )
        return lowered

    @field_validator("meter")
    @classmethod
    def _known_meter(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        stripped = value.strip()
        if stripped not in SUPPORTED_METERS:
            raise ValueError(
                f"unsupported meter {value!r}; expected one of "
                f"{', '.join(SUPPORTED_METERS)}"
            )
        return stripped

    @field_validator("tonic")
    @classmethod
    def _valid_tonic(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        try:
            return normalize_note_name(value)
        except TheoryError as exc:
            raise ValueError(str(exc)) from exc


# --------------------------------------------------------------------------------------
# Response -- semantics
# --------------------------------------------------------------------------------------


with warnings.catch_warnings():
    # ``register`` is one of the ten semantic axes and is part of the wire contract.
    # It also happens to shadow ``BaseModel.register`` (inherited from ABCMeta), which
    # pydantic warns about; the field works correctly, so the warning is suppressed here
    # rather than distorting the published field name.
    warnings.filterwarnings("ignore", message='Field name "register".*', category=UserWarning)

    class SemanticAxesModel(BaseModel):
        """The ten continuous axes the lexicon projects onto, each in ``[-1, 1]``."""

        valence: float = Field(..., description="-1 sorrowful .. +1 radiant")
        energy: float = Field(..., description="-1 motionless .. +1 violent")
        density: float = Field(..., description="-1 sparse .. +1 teeming")
        tension: float = Field(..., description="-1 consonant .. +1 chromatic")
        register: float = Field(..., description="-1 subterranean .. +1 high")
        contour: float = Field(..., description="-1 falling .. +1 rising")
        cadence: float = Field(..., description="-1 unresolved .. +1 firmly closed")
        heresy: float = Field(..., description="-1 orthodox .. +1 transgressive")
        weight: float = Field(..., description="-1 weightless .. +1 massive")
        luminosity: float = Field(..., description="-1 murky .. +1 luminous")


class MatchedTermModel(BaseModel):
    token: str = Field(..., description="The word as it appeared in the text.")
    lexeme: str = Field(..., description="The lexicon entry it resolved to.")
    weight: float = Field(..., description="Signed multiplier from negators/intensifiers.")


class SemanticSuggestionModel(BaseModel):
    mode: str
    tonic: str
    tempo: int
    meter: str
    measures: int
    density: float
    register_shift: int
    contour_bias: float
    cadence_strength: float
    tension: float
    heresy: float
    heretical: bool
    phrase_measures: int
    articulation: str
    mood: str
    ensemble: str
    instrumentation: Dict[str, str]


class SemanticAnalysisModel(BaseModel):
    source_text: str
    normalized_text: str
    tokens: List[str]
    matched_terms: List[MatchedTermModel]
    unmatched_tokens: List[str]
    axes: SemanticAxesModel
    mode_scores: Dict[str, float]
    suggestion: SemanticSuggestionModel
    fallback_used: bool = Field(
        ...,
        description="True when no lexicon term matched and the axes were derived from a "
                    "stable hash of the text instead.",
    )


# --------------------------------------------------------------------------------------
# Response -- score
# --------------------------------------------------------------------------------------


class NoteEventModel(BaseModel):
    pitch: str = Field(..., description="Spelled pitch, e.g. 'Eb4'.")
    midi: int = Field(..., ge=0, le=127)
    offset: float = Field(..., description="Onset in quarter-lengths from the start.")
    duration: float = Field(..., description="Notated length in quarter-lengths.")
    sounding_duration: float = Field(
        ...,
        description="Length after the articulation gate. THE VOICE should use this; the "
                    "exported MIDI carries the notated duration.",
    )
    velocity: int = Field(..., ge=0, le=127)
    role: str = Field(
        ...,
        description="structural | passing | neighbour | suspension | anticipation | "
                    "escape | chromatic | displaced",
    )
    slot: int = Field(..., description="Index of the harmonic slot this note falls in.")
    measure: int


class VoiceLineModel(BaseModel):
    voice: str = Field(..., description="soprano | alto | tenor | bass")
    instrument: str
    instrument_name: str
    range: Dict[str, int]
    event_count: int
    events: List[NoteEventModel]


class PhraseModel(BaseModel):
    index: int
    first_measure: int
    last_measure: int
    first_slot: int
    last_slot: int
    cadence: str
    cadence_provenance: str = Field(
        ...,
        description="How much historical authority this formula carries. 'H1' = period "
                    "practice implemented approximately; 'N1' = a Neo-Arca construction; "
                    "'HAERETIC' = a declared transgression. Cadences here are chord "
                    "pairs, not the contrapuntal clausulae that historically define "
                    "them -- see docs/PROVENANCE.md section 3.",
    )
    cadence_note: str = Field(
        ..., description="What this particular formula does and does not claim."
    )


class HarmonicSlotModel(BaseModel):
    index: int
    offset: float
    duration: float
    measure: int
    chord: str = Field(..., description="Roman-numeral label, '#' marks musica ficta.")
    quality: str
    root_pitch_class: int
    is_cadential: bool
    is_final: bool


class ScoreModel(BaseModel):
    tonic: str
    mode: str
    mood: str
    tempo: int
    meter: str
    measures: int
    total_quarter_length: float
    duration_seconds: float
    law_profile: str
    key_signature_sharps: int = Field(
        ...,
        description="Signed circle-of-fifths position of the final AS SPELLED: positive "
                    "is sharps, negative is flats. Derived from the spelling, so C# and "
                    "Db differ (7 sharps against 5 flats). May exceed 7 -- G# Ionian is "
                    "genuinely 8 sharps.",
    )
    key_signature_notatable: int = Field(
        ...,
        description="The same signature wrapped into the +/-7 a staff and a MIDI file "
                    "can express. Equal to key_signature_sharps unless that exceeds 7.",
    )
    key_signature_is_notatable: bool = Field(
        ..., description="False when the true signature needs more than 7 accidentals."
    )
    musica_ficta_pitch_classes: List[int]
    progression: List[str]
    phrases: List[PhraseModel]
    slots: List[HarmonicSlotModel]
    voices: List[VoiceLineModel]


# --------------------------------------------------------------------------------------
# Response -- diagnostics
# --------------------------------------------------------------------------------------


class RuleViolationModel(BaseModel):
    rule: str
    severity: Severity = Field(
        ...,
        description="Graded under Orthodox law so severities are comparable between "
                    "profiles, whichever profile generated the music.",
    )
    voices: List[str]
    position: float = Field(..., description="Offset in quarter-lengths.")
    detail: str
    penalty: float
    slot: Optional[int] = Field(None, description="Harmonic slot this falls in.")
    licensed: bool = Field(
        ...,
        description="True when the ACTIVE law profile permits this rule class. Under "
                    "MODUS HAERETICUS a parallel fifth is licensed; under Orthodox law "
                    "it is not. This is what decides `passed`.",
    )
    intent: Intent = Field(
        ...,
        description="How this occurrence arose. 'deliberate': the generator recorded a "
                    "decision that produces it (a chromatic ornament, an alien triad). "
                    "'emergent': licensed by the active law, but nothing sought this "
                    "one. 'defect': an unlicensed error, i.e. an implementation fault. "
                    "'incidental': an ordinary stylistic observation.",
    )
    reason: Optional[str] = Field(
        None,
        description="The recorded decision that explains a 'deliberate' violation.",
    )


class ValidationModel(BaseModel):
    profile: str
    passed: bool = Field(
        ...,
        description="True when no violation is classified as a 'defect'. Licensed "
                    "transgressions never fail a composition.",
    )
    counts_by_rule: Dict[str, int]
    counts_by_severity: Dict[str, int]
    counts_by_intent: Dict[str, int]
    defect_count: int = Field(
        ..., description="Unlicensed error-severity violations: genuine faults."
    )
    deliberate_count: int
    emergent_count: int
    licensed_count: int
    recorded_intents: Dict[str, int] = Field(
        default_factory=dict,
        description="What the generator deliberately sought, by kind of decision.",
    )
    violations: List[RuleViolationModel]


class SearchModel(BaseModel):
    slots: int
    candidate_sets_built: int
    candidates_considered: int
    nodes_visited: int = Field(
        ...,
        description="Total enumeration nodes actually visited, counting every pass.",
    )
    lenient_enumerations: int = Field(
        ...,
        description="Slots whose strict enumeration was empty and needed the lenient "
                    "fallback. The fallback shares the slot's single node allowance.",
    )
    node_budget_hits: int = Field(
        ...,
        description="Slot enumerations that stopped on the node budget rather than on "
                    "running out of candidates.",
    )
    backtracks: int
    relaxation_level: int = Field(
        ...,
        description="0 is full strictness; higher means the SEARCH had to drop hard "
                    "rules to find any solution at all. The returned music is still "
                    "guaranteed defect-free -- a relaxed search that produced an "
                    "unlicensed error fails with 500 rather than returning.",
    )
    relaxed: bool = Field(
        False, description="Shorthand for relaxation_level > 0."
    )
    solver_restarts: int
    repair_passes: int
    phrases_without_tritone: int = Field(
        0,
        description="Phrases that left repair with no sounding tritone. Under "
                    "MODUS HAERETICUS the grammar then injects one.",
    )
    tritone_injections: int = 0
    repair_exhausted: bool = Field(
        ...,
        description="True when repair hit max_repair_passes with hard violations still "
                    "outstanding; whatever remains is reported in `validation`.",
    )
    ornaments_applied: int
    ornaments_reverted: int
    elapsed_ms: float
    budget_exhausted: bool


class ProvenanceModel(BaseModel):
    engine_version: str
    seed: str = Field(
        ...,
        description="The resolved seed, as a DECIMAL STRING, not a JSON number. It is "
                    "drawn from a full 64-bit range, which exceeds 2**53 - 1 -- the "
                    "largest integer JavaScript's Number type represents exactly -- so "
                    "a bare JSON number here would silently lose precision in a browser. "
                    "Parse it with BigInt(seed) if you need the numeric value; never "
                    "with Number(seed) or the unary + operator. If you only need to "
                    "compare or store it, treat it as an opaque string.",
    )
    requested_seed: Optional[str] = Field(
        None,
        description="The seed exactly as the request gave it, also as a decimal string "
                    "when numeric (same precision rationale as `seed`), or the original "
                    "string unchanged, or null if the request omitted it.",
    )
    law_profile: str
    config_fingerprint: str
    runtime: Dict[str, str] = Field(
        default_factory=dict,
        description="Python and music21 versions this was produced on. The engine "
                    "chooses the same notes on any runtime; these versions scope the "
                    "stronger claim that the MIDI bytes are identical too. See "
                    "docs/DETERMINISM.md for the precise, tiered guarantee.",
    )


class ConfigurationModel(BaseModel):
    text: str
    mode: str
    mood: str
    tonic: str
    tonic_pitch_class: int
    tempo: int
    meter: str
    measures: int
    phrase_measures: int
    density: float
    register_shift: int
    contour_bias: float
    cadence_strength: float
    tension: float
    heresy: float
    heretical: bool
    law_profile: str
    articulation: str
    gate: float
    intensity: float
    ensemble: str
    instrumentation: Dict[str, str]


class EngineModel(BaseModel):
    name: str
    version: str
    law_profile: str
    law_title: str


class ComposeResponse(BaseModel):
    engine: EngineModel
    provenance: ProvenanceModel
    configuration: ConfigurationModel
    semantics: SemanticAnalysisModel
    score: ScoreModel
    validation: ValidationModel
    search: SearchModel
    midi_base64: str = Field(
        ..., description="The complete four-part composition as a Base64 Standard MIDI "
                         "File, one track per voice."
    )


# --------------------------------------------------------------------------------------
# Health
# --------------------------------------------------------------------------------------


class HealthResponse(BaseModel):
    status: str
    engine: str
    version: str
    modes: List[str]
    meters: List[str]
    law_profiles: List[str]
    tonics: List[str]
    max_measures: int


# --------------------------------------------------------------------------------------
# Errors
# --------------------------------------------------------------------------------------


class ErrorResponse(BaseModel):
    error: str
    message: str
    diagnostics: Dict[str, Any] = Field(default_factory=dict)


# --------------------------------------------------------------------------------------
# Projection
# --------------------------------------------------------------------------------------


def _wire_safe_provenance(provenance: Any) -> "ProvenanceModel":
    """Project :class:`determinism.Provenance` with seeds as JS-safe decimal strings.

    ``Provenance.seed`` is a Python int drawn from a full 64-bit range -- correct and
    convenient internally, but a JSON *number* that large silently loses precision the
    moment a browser parses it (JS ``Number`` is exact only up to 2**53 - 1). Both seed
    fields are therefore converted to decimal strings here, at the API boundary, rather
    than by widening the internal `Provenance` dataclass -- the engine's own arithmetic on
    seeds stays ordinary integer arithmetic; only the wire representation changes.
    """
    payload = provenance.as_dict()
    payload["seed"] = str(payload["seed"])
    requested = payload["requested_seed"]
    payload["requested_seed"] = None if requested is None else str(requested)
    return ProvenanceModel(**payload)


def build_compose_response(composition: Any, midi_base64: str) -> ComposeResponse:
    """Project a :class:`kircher_engine.Composition` onto the wire format."""
    from harmony import cadence_provenance
    from theory import Speller  # local import keeps models.py free of engine imports

    speller = Speller(composition.config.tonic, composition.config.mode)
    plan = composition.plan
    return ComposeResponse(
        engine=EngineModel(
            name=ENGINE_NAME,
            version=composition.provenance.engine_version,
            law_profile=composition.profile.name,
            law_title=composition.profile.title,
        ),
        provenance=_wire_safe_provenance(composition.provenance),
        configuration=ConfigurationModel(**composition.config.as_dict()),
        semantics=SemanticAnalysisModel(**composition.analysis.as_dict()),
        score=ScoreModel(
            tonic=composition.config.tonic,
            mode=composition.config.mode.value,
            mood=composition.config.mood,
            tempo=composition.config.tempo,
            meter=composition.config.meter,
            measures=composition.config.measures,
            total_quarter_length=round(composition.total_ql, 6),
            duration_seconds=round(composition.duration_seconds, 3),
            law_profile=composition.profile.name,
            key_signature_sharps=speller.signature_sharps(),
            key_signature_notatable=speller.notatable_signature(),
            key_signature_is_notatable=speller.signature_is_notatable(),
            musica_ficta_pitch_classes=sorted(plan.ficta_pcs),
            progression=plan.progression(),
            phrases=[
                PhraseModel(
                    index=p.index,
                    first_measure=p.first_measure,
                    last_measure=p.last_measure,
                    first_slot=p.first_slot,
                    last_slot=p.last_slot,
                    cadence=p.cadence.value,
                    cadence_provenance=cadence_provenance(p.cadence).classification,
                    cadence_note=cadence_provenance(p.cadence).note,
                )
                for p in plan.phrases
            ],
            slots=[
                HarmonicSlotModel(
                    index=s.index,
                    offset=round(s.offset, 6),
                    duration=round(s.duration, 6),
                    measure=s.timing.measure,
                    chord=s.triad.label,
                    quality=s.triad.quality.value,
                    root_pitch_class=s.triad.root_pc,
                    is_cadential=s.is_cadential,
                    is_final=s.is_final,
                )
                for s in plan.slots
            ],
            voices=[VoiceLineModel(**payload) for payload in composition.voice_payload()],
        ),
        validation=ValidationModel(**composition.validation.as_dict()),
        search=SearchModel(**composition.stats.as_dict()),
        midi_base64=midi_base64,
    )


__all__ = [
    "ComposeRequest", "ComposeResponse", "HealthResponse", "ErrorResponse",
    "SemanticAxesModel", "MatchedTermModel", "SemanticSuggestionModel",
    "SemanticAnalysisModel", "NoteEventModel", "VoiceLineModel", "PhraseModel",
    "HarmonicSlotModel", "ScoreModel", "RuleViolationModel", "ValidationModel",
    "SearchModel", "ProvenanceModel", "ConfigurationModel", "EngineModel",
    "build_compose_response", "MODE_NAMES", "ENGINE_NAME",
]
