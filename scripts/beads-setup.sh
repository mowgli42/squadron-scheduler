#!/usr/bin/env bash
# Seed Beads from OpenSpec aircraft-scheduling capabilities.
# Run from repo root. Requires: bd
set -euo pipefail
cd "$(dirname "$0")/.."

if ! command -v bd &>/dev/null; then
  echo "Beads (bd) is not installed."
  exit 1
fi

bd init --prefix sq --non-interactive 2>/dev/null || true

# Prototype gap-close (implement in this repo)
bd create "A1: Sortie land window + turn-buffer aircraft conflicts" -t feature -p 0 \
  --labels "status:specified,capability:aircraft-assignment" \
  --description "OpenSpec: openspec/specs/aircraft-assignment/spec.md" || true
bd create "A2: Spare/backup tail assignment + spare≠primary" -t feature -p 0 \
  --labels "status:specified,capability:aircraft-assignment" || true
bd create "A3: Config vs loadout mismatch blockers" -t feature -p 0 \
  --labels "status:specified,capability:aircraft-assignment" || true
bd create "A4: Aircraft day board GET /aircraft/schedule" -t feature -p 0 \
  --labels "status:specified,capability:aircraft-day-board" || true
bd create "A5: Line number + callsign on sorties" -t feature -p 0 \
  --labels "status:specified,capability:flying-schedule" || true
bd create "A6: Load-crew minutes from loadout template" -t feature -p 0 \
  --labels "status:specified,capability:loadout-and-mx" || true
bd create "A7: Rest gate on crew assign" -t feature -p 0 \
  --labels "status:specified,capability:crew-assignment" || true
bd create "A8: Pen-and-ink change log" -t feature -p 0 \
  --labels "status:specified,capability:pen-and-ink" || true
bd create "A9: ER signature required before crew-ready" -t feature -p 0 \
  --labels "status:specified,capability:loadout-and-mx" || true
bd create "A10: Crew replace (upsert) on filled position" -t feature -p 0 \
  --labels "status:specified,capability:crew-assignment" || true
bd create "A11: Metrics — spares, ER, config mismatches" -t feature -p 0 \
  --labels "status:specified,capability:readiness-metrics" || true
bd create "A12: Demo 01–06 with spares + ER" -t feature -p 0 \
  --labels "status:specified,capability:demo-buildup" || true
bd create "A13: Frontend board — spare/ER/schedule/pen-ink" -t feature -p 1 \
  --labels "status:specified,capability:flying-schedule" || true

# Production (do not implement in prototype)
bd create "P1: Durable multi-user store" -t task -p 3 --labels "status:backlog,phase:production" || true
bd create "P2: Explicit process state machine" -t task -p 3 --labels "status:backlog,phase:production" || true
bd create "P3: Auth + squadron tenancy" -t task -p 3 --labels "status:backlog,phase:production" || true
bd create "P4: Live Ops–MX feed" -t task -p 3 --labels "status:backlog,phase:production" || true
bd create "P5: Full RAP / currency engine" -t task -p 3 --labels "status:backlog,phase:production" || true
bd create "P6: Hosted demo" -t task -p 3 --labels "status:backlog,phase:production" || true

echo "Beads seeded. Run: bd ready"
bd ready || true
bd list || true
