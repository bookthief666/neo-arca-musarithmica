#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "== M1.0.1B verification =="
echo "repo: $ROOT"
echo

echo "[1/7] Focused historical kernel + bridge tests"
python -m pytest \
  tests/test_arca_historica_kernel.py \
  tests/test_arca_mechanica_bridge.py \
  -q

echo
echo "[2/7] Full Python suite"
python -m pytest -q

echo
echo "[3/7] Frontend tests"
cd "$ROOT/frontend"
npm test

echo
echo "[4/7] Frontend typecheck"
npm run typecheck

echo
echo "[5/7] Frontend lint"
npm run lint

echo
echo "[6/7] Frontend production build"
npm run build

echo
echo "[7/7] Repository state"
cd "$ROOT"
git status --short --branch

echo
echo "M1.0.1B automated verification complete."
echo "Browser interaction and responsive visual QA are still mandatory before acceptance."
