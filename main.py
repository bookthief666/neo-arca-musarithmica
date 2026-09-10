"""main.py -- THE GHOST, exposed.

    uvicorn main:app --reload

Two endpoints, no more: ``GET /health`` reports what the engine can do, and
``POST /compose`` runs the whole pipeline and returns the composition together with
everything needed to reproduce, inspect and play it.

Deliberately absent from Phase 1: authentication, databases, background workers, cloud
configuration.  The engine is synchronous and CPU-bound (a typical eight-bar request
resolves in well under half a second), so it is defined with ordinary ``def`` handlers
and FastAPI runs them on its worker threadpool rather than blocking the event loop.
"""

from __future__ import annotations

import logging
import math
from typing import Any, Dict

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from constraints import PROFILES
from kircher_engine import ENGINE, ENGINE_NAME, ENGINE_VERSION, GenerationError
from midi_export import MidiExportError, composition_to_base64
from models import (
    ComposeRequest, ComposeResponse, ErrorResponse, HealthResponse,
    build_compose_response,
)
from rhythm import MeterError, SUPPORTED_METERS
from theory import CANDIDATE_TONICS, ModeName, TheoryError

logger = logging.getLogger("neo_arca")

MAX_MEASURES = 64

app = FastAPI(
    title="Neo-Arca Musarithmica",
    version=ENGINE_VERSION,
    summary="A seventeenth-century combinatorial music engine excavated from an "
            "impossible technological timeline.",
    description=(
        "Kircher's *Arca Musarithmica* (Musurgia Universalis, 1650) treated composition "
        "as something that could be encoded, categorised, permuted, constrained and "
        "executed through a formal symbolic system. This service replaces the wooden "
        "cabinet with a deterministic generative engine: free text enters through a "
        "*Polygraphia*-inspired semantic mapper, and a genuine four-part contrapuntal "
        "search returns SATB events, rule diagnostics and Base64 MIDI."
    ),
)

# The Skin & Eye will be a separate Vite dev server in Phase 2.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


#: How much of an oversized "input" field a validation-error diagnostic echoes back.
#: Comfortably above any legitimate field value (the longest is `text` at 600 chars) so
#: normal errors are never truncated; only a deliberately oversized adversarial input is.
_MAX_ECHOED_STRING_LENGTH = 1000


def _json_safe(value: object) -> object:
    """Recursively replace non-finite floats (NaN/+-Infinity) with a string.

    ``JSONResponse`` renders with ``allow_nan=False`` (Starlette's default, matching the
    JSON spec proper), so any raw ``nan``/``inf``/``-inf`` reaching it raises a bare
    ``ValueError`` from inside the response-rendering path itself -- an unhandled 500
    triggered by nothing worse than an adversarial-but-well-formed request (a literal
    ``NaN``/``Infinity`` token in the request body, which Python's own ``json.loads``
    accepts by default, ends up echoed back inside a validation error's ``"input"``
    field). Diagnostics payloads are built from a mix of request echoes and internal
    dataclasses, so this is applied at the one point they all funnel through --
    :func:`_error` -- rather than trusted to stay finite at every call site.
    """
    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            return repr(value)  # "nan", "inf", "-inf" -- still informative, always safe
        return value
    if isinstance(value, BaseException):
        # Pydantic's own error list embeds the original exception object verbatim under
        # `ctx.error` for a `field_validator` that raised `ValueError` (e.g. the tonic or
        # seed-length checks in models.py) -- never JSON-serialisable on its own.
        return str(value)
    if isinstance(value, str) and len(value) > _MAX_ECHOED_STRING_LENGTH:
        # Pydantic's validation errors echo the offending input verbatim under "input";
        # for a deliberately oversized field (the whole point of the length checks above)
        # that would otherwise reflect kilobytes of attacker-supplied text back in the
        # response for no diagnostic benefit.
        return value[:_MAX_ECHOED_STRING_LENGTH] + f"...(truncated from {len(value)})"
    if isinstance(value, dict):
        return {k: _json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(v) for v in value]
    return value


def _error(status_code: int, error: str, message: str,
           diagnostics: Dict[str, Any] | None = None) -> JSONResponse:
    payload = ErrorResponse(
        error=error, message=message, diagnostics=_json_safe(diagnostics or {})
    )
    return JSONResponse(status_code=status_code, content=payload.model_dump())


@app.exception_handler(RequestValidationError)
def _handle_validation_error(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Replaces FastAPI's default ``{"detail": [...]}`` shape with the same
    ``ErrorResponse`` envelope every other failure path uses, so a consumer never has to
    special-case "was this a Pydantic validation failure or something else". The raw
    Pydantic error list -- which can itself carry a non-finite ``"input"`` value, e.g. a
    literal ``Infinity`` sent for a numeric field -- is sanitised by :func:`_error` before
    it is ever handed to the JSON renderer.
    """
    return _error(
        status.HTTP_422_UNPROCESSABLE_CONTENT,
        "invalid_request",
        "the request did not match the expected shape; see diagnostics.errors",
        {"errors": exc.errors()},
    )


@app.exception_handler(TheoryError)
def _handle_theory_error(request: Request, exc: TheoryError) -> JSONResponse:
    return _error(status.HTTP_422_UNPROCESSABLE_CONTENT, "invalid_musical_input", str(exc))


@app.exception_handler(MeterError)
def _handle_meter_error(request: Request, exc: MeterError) -> JSONResponse:
    return _error(status.HTTP_422_UNPROCESSABLE_CONTENT, "invalid_meter", str(exc))


@app.exception_handler(GenerationError)
def _handle_generation_error(request: Request, exc: GenerationError) -> JSONResponse:
    """Two different failures share ``GenerationError``, and they are not the same
    category (see ``kircher_engine.GENERATION_ERROR_KINDS``): a bounded search that
    exhausted its budget is a property of *this request* -- a different seed, density,
    mode or measure count can succeed where this one didn't, so the client can usefully
    retry, and that is a 422. A relaxed search returning a defect the active law does not
    license is an implementation fault in the engine's own repair/relaxation logic;
    retrying the identical request cannot fix it, so that stays a 500.
    """
    if exc.kind == "search_exhausted":
        logger.info(
            "search exhausted (request-specific, client may retry): %s", exc,
            extra={"diagnostics": exc.diagnostics},
        )
        return _error(
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            "unrealizable_request",
            str(exc),
            exc.diagnostics,
        )
    logger.error(
        "generation defect (internal fault): %s", exc,
        extra={"diagnostics": exc.diagnostics},
    )
    return _error(
        status.HTTP_500_INTERNAL_SERVER_ERROR,
        "generation_defect",
        str(exc),
        exc.diagnostics,
    )


@app.exception_handler(MidiExportError)
def _handle_midi_error(request: Request, exc: MidiExportError) -> JSONResponse:
    logger.error("midi export failed: %s", exc)
    return _error(status.HTTP_500_INTERNAL_SERVER_ERROR, "midi_export_failed", str(exc))


@app.exception_handler(Exception)
def _handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
    """The fallback for anything not one of the specific cases above -- a genuine
    implementation gap, not a category of failure this service knows how to name yet.
    Logged with the full traceback server-side; the client gets the same structured
    envelope as every other failure, with no traceback or internal detail leaked. Every
    more specific handler above is still tried first (Starlette dispatches by walking the
    exception's MRO), so this only ever catches what nothing else claimed.
    """
    logger.exception(
        "unhandled exception while serving %s %s", request.method, request.url.path
    )
    return _error(
        status.HTTP_500_INTERNAL_SERVER_ERROR, "internal_error",
        "an unexpected internal error occurred",
    )


@app.get("/health", response_model=HealthResponse, tags=["engine"])
def health() -> HealthResponse:
    """Engine status and the vocabulary it accepts."""
    return HealthResponse(
        status="ok",
        engine=ENGINE_NAME,
        version=ENGINE_VERSION,
        modes=[m.value for m in ModeName],
        meters=list(SUPPORTED_METERS),
        law_profiles=sorted(PROFILES),
        tonics=list(CANDIDATE_TONICS),
        max_measures=MAX_MEASURES,
    )


@app.post(
    "/compose",
    response_model=ComposeResponse,
    tags=["arca"],
    responses={
        422: {
            "model": ErrorResponse,
            "description": (
                "The request is malformed (`invalid_request`, `invalid_musical_input`, "
                "`invalid_meter`), or it is well-formed but this particular combination "
                "of parameters could not be realised within the search budget "
                "(`unrealizable_request`) -- retrying with a different seed, density, "
                "mode or measure count may succeed where this one didn't."
            ),
        },
        500: {
            "model": ErrorResponse,
            "description": (
                "An internal fault, not a property of the request: the engine's own "
                "repair/relaxation logic let an unlicensed defect through "
                "(`generation_defect`), MIDI serialisation failed (`midi_export_failed`), "
                "or an unanticipated error occurred (`internal_error`). Retrying the "
                "identical request will not help; see `docs/API.md`, \"Error taxonomy\"."
            ),
        },
    },
)
def compose(request: ComposeRequest) -> ComposeResponse:
    """Run the Arca.

    The pipeline is: normalise the text, analyse it semantically, merge the result with
    any explicit overrides, derive a deterministic seed, plan phrases and cadences, solve
    the four-part voicing under the active law profile, add the rhythmic surface, repair
    anything the surface broke, validate, and serialise to MIDI.
    """
    composition = ENGINE.compose(
        text=request.text,
        seed=request.seed,
        mode=request.mode,
        tonic=request.tonic,
        tempo=request.tempo,
        meter=request.meter,
        measures=request.measures,
        phrase_measures=request.phrase_measures,
        density=request.density,
        heretical=request.heretical,
    )
    return build_compose_response(composition, composition_to_base64(composition))


@app.get("/", include_in_schema=False)
def root() -> Dict[str, str]:
    return {
        "engine": ENGINE_NAME,
        "version": ENGINE_VERSION,
        "docs": "/docs",
        "health": "/health",
        "compose": "POST /compose",
    }
