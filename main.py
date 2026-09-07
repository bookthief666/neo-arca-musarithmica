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
from typing import Any, Dict

from fastapi import FastAPI, Request, status
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


def _error(status_code: int, error: str, message: str,
           diagnostics: Dict[str, Any] | None = None) -> JSONResponse:
    payload = ErrorResponse(
        error=error, message=message, diagnostics=diagnostics or {}
    )
    return JSONResponse(status_code=status_code, content=payload.model_dump())


@app.exception_handler(TheoryError)
def _handle_theory_error(request: Request, exc: TheoryError) -> JSONResponse:
    return _error(status.HTTP_422_UNPROCESSABLE_ENTITY, "invalid_musical_input", str(exc))


@app.exception_handler(MeterError)
def _handle_meter_error(request: Request, exc: MeterError) -> JSONResponse:
    return _error(status.HTTP_422_UNPROCESSABLE_ENTITY, "invalid_meter", str(exc))


@app.exception_handler(GenerationError)
def _handle_generation_error(request: Request, exc: GenerationError) -> JSONResponse:
    logger.warning("generation failed: %s", exc, extra={"diagnostics": exc.diagnostics})
    return _error(
        status.HTTP_500_INTERNAL_SERVER_ERROR,
        "generation_failed",
        str(exc),
        exc.diagnostics,
    )


@app.exception_handler(MidiExportError)
def _handle_midi_error(request: Request, exc: MidiExportError) -> JSONResponse:
    logger.error("midi export failed: %s", exc)
    return _error(status.HTTP_500_INTERNAL_SERVER_ERROR, "midi_export_failed", str(exc))


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
        422: {"model": ErrorResponse, "description": "The request could not be realised."},
        500: {"model": ErrorResponse, "description": "The generative search failed."},
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
