#!/usr/bin/env bash
# next-boot.sh <system-dir> <NNN>
# The SINGLE WRITER for the _NEXT_NNN.booted occupancy sidecar.
#
# WHY THIS EXISTS (the double-booking soft-guard)
# next/ is shared mutable state and boot is read-only: nothing records that a
# session is CURRENTLY working a slot. So two sessions can boot the same _NEXT
# (most plausibly two near-simultaneous no-arg /session picks both auto-picking
# the lowest live slot), then duplicate the work AND race on the shared output
# files those moves write (CHANGELOG, indexes, caches) — the only real exposure,
# since the _NEXT plumbing itself is collision-safe (idempotent consume via
# next-consume.sh + atomic mint via next-write.sh).
#
# This is the deliberately SOFT mitigation (a hard lock was rejected — it needs a
# stale-lock reaper, breaks the read-only-boot invariant, and a TTL just re-creates
# the "is it really still live?" judgment the system already leaves to a human; see
# ledger/DECISIONS.md). A .booted hint is ADVISORY: nothing depends on its accuracy,
# so a stale/leaked one is HARMLESS and needs no reaper — next-live.sh surfaces
# "in use / booted HH:MM" so a human picking a slot sees occupancy, and the no-arg
# picker skips a just-booted slot. It is cleared when the slot retires
# (next-consume.sh) and next-live.sh stops showing it past its display window anyway.
#
# Unlike next-consume.sh this is NOT idempotent: each boot REFRESHES the timestamp,
# so "may be in use" tracks the most recent boot of the slot.
#
# It is the WRITER, not the POLICY: it does not decide whether to skip a slot —
# next-live.sh reports occupancy, the /session and /boot no-arg pickers act on it.
#
# Usage: next-boot.sh /absolute/path/to/system-dir 052

set -euo pipefail

SYSTEM_DIR="${1:?Usage: next-boot.sh <system-dir> <NNN>}"
NNN_RAW="${2:?Usage: next-boot.sh <system-dir> <NNN>}"
NEXT_DIR="${SYSTEM_DIR}/next"

# Same root guard as next-write.sh / next-consume.sh: SYSTEM_DIR must be the real
# system root, identified by its permanent _NEXT.md pointer/spec. A cwd-relative or
# mistyped path must fail loud, never stamp a sidecar in the wrong tree.
if [[ ! -f "${SYSTEM_DIR}/_NEXT.md" ]]; then
  echo "next-boot.sh: '${SYSTEM_DIR}/_NEXT.md' not found — SYSTEM_DIR is not the system root." >&2
  echo "  Pass an absolute path: next-boot.sh /absolute/path/to/system-dir <NNN>" >&2
  exit 1
fi

# Normalize the slot arg: accept 52, 052, _NEXT_052, _NEXT_052.md, _NEXT_052.booted.
nnn="${NNN_RAW##*_NEXT_}"; nnn="${nnn%.md}"; nnn="${nnn%.booted}"; nnn="${nnn%.consumed}"
if ! [[ "${nnn}" =~ ^[0-9]+$ ]]; then
  echo "next-boot.sh: '${NNN_RAW}' is not a slot number." >&2
  exit 1
fi

# Resolve the real _NEXT file (handles 3/4/5-digit widths) — refuse to stamp a
# slot with no matching .md (that would be an orphan occupancy sidecar).
md=""
shopt -s nullglob
for f in "${NEXT_DIR}"/_NEXT_*.md; do
  b=$(basename "$f"); n="${b#_NEXT_}"; n="${n%.md}"
  if (( 10#${n} == 10#${nnn} )); then md="$f"; nnn="$n"; break; fi
done
shopt -u nullglob

if [[ -z "${md}" ]]; then
  echo "next-boot.sh: no _NEXT_*.md matches '${NNN_RAW}' in ${NEXT_DIR} — refusing to stamp an orphan." >&2
  exit 1
fi

# A retired slot is not "in use" — don't mark a consumed slot booted.
if [[ -e "${NEXT_DIR}/_NEXT_${nnn}.consumed" ]]; then
  echo "next-boot.sh: _NEXT_${nnn} is already consumed — not marking booted."
  exit 0
fi

sidecar="${NEXT_DIR}/_NEXT_${nnn}.booted"
stamp="$(date -u +%Y-%m-%dT%H:%MZ)"
printf 'booted %s\n' "${stamp}" > "${sidecar}"   # refresh on every boot (not idempotent)
echo "${sidecar}"
