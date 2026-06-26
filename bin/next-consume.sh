#!/usr/bin/env bash
# next-consume.sh <system-dir> <NNN> [reason]
# The SINGLE WRITER for the _NEXT_NNN.consumed sidecar.
#
# WHY THIS EXISTS (the consume-leak fix, layer B)
# A slot used to be retired by a bare `touch _NEXT_NNN.consumed` typed by hand in
# several command specs (handoff boot-stamp + supersede-stamp, audit remediation).
# That manual touch was forgettable AND unauditable: slots finished OFF the
# boot->handoff path (reflection closes, cold finishes, /foldin, branch-off
# supersedes) silently never got stamped and sat "falsely live forever".
#
# This script makes every retire ONE auditable operation:
#   (1) validate the system dir and that a real _NEXT_NNN.md exists (no orphan
#       stamps), (2) stamp ONCE and idempotently (re-running is a safe no-op),
#       (3) record provenance INTO the sidecar (when + why), so a retire can
#       never half-happen and every retire is self-documenting.
#
# It is the WRITER, not the POLICY. It does NOT decide whether a slot is done —
# that judgment stays with the caller: the boot-coupled mint (next-write.sh
# --consume, layer A) for the normal path, or a human adjudicating a
# DONE-PROBABLE flag (next-live.sh, layer C) for everything else.
#
# Backward-compatible: legacy sidecars are empty 0-byte files; next-live.sh keys
# off existence + mtime, so writing a provenance line into new ones changes
# nothing for the detector while making `cat _NEXT_NNN.consumed` explain itself.
#
# Usage: next-consume.sh /absolute/path/to/system-dir 061 "done: superseded by _NEXT_065"

set -euo pipefail

SYSTEM_DIR="${1:?Usage: next-consume.sh <system-dir> <NNN> [reason]}"
NNN_RAW="${2:?Usage: next-consume.sh <system-dir> <NNN> [reason]}"
REASON="${3:-}"
NEXT_DIR="${SYSTEM_DIR}/next"

# Same root guard as next-write.sh: SYSTEM_DIR must be the real system root,
# identified by its permanent _NEXT.md pointer/spec. A cwd-relative or mistyped
# path must fail loud, never stamp a sidecar in the wrong tree.
if [[ ! -f "${SYSTEM_DIR}/_NEXT.md" ]]; then
  echo "next-consume.sh: '${SYSTEM_DIR}/_NEXT.md' not found — SYSTEM_DIR is not the system root." >&2
  echo "  Pass an absolute path: next-consume.sh /absolute/path/to/system-dir <NNN> [reason]" >&2
  exit 1
fi

# Kit guard (v0.6.2): the kit ships its own _NEXT.md spec (root-guard passes) but is
# NOT a user system — never stamp a sidecar on the shipped repo. A .svaha-kit marker flags it.
if [[ -f "${SYSTEM_DIR}/.svaha-kit" ]]; then
  echo "next-consume.sh: '${SYSTEM_DIR}' is the Svaha kit (.svaha-kit present), not a user system — refusing." >&2
  exit 1
fi

# Normalize the slot arg: accept 59, 059, _NEXT_059, _NEXT_059.md, _NEXT_059.consumed.
nnn="${NNN_RAW##*_NEXT_}"; nnn="${nnn%.md}"; nnn="${nnn%.consumed}"
if ! [[ "${nnn}" =~ ^[0-9]+$ ]]; then
  echo "next-consume.sh: '${NNN_RAW}' is not a slot number." >&2
  exit 1
fi

# Resolve the real _NEXT file (handles 3/4/5-digit widths) — refuse to stamp a
# slot with no matching .md (that would be an ORPHAN sidecar, the very desync
# next-live.sh flags).
md=""
shopt -s nullglob
for f in "${NEXT_DIR}"/_NEXT_*.md; do
  b=$(basename "$f"); n="${b#_NEXT_}"; n="${n%.md}"
  if (( 10#${n} == 10#${nnn} )); then md="$f"; nnn="$n"; break; fi
done
shopt -u nullglob

if [[ -z "${md}" ]]; then
  echo "next-consume.sh: no _NEXT_*.md matches '${NNN_RAW}' in ${NEXT_DIR} — refusing to stamp an orphan." >&2
  exit 1
fi

sidecar="${NEXT_DIR}/_NEXT_${nnn}.consumed"
if [[ -e "${sidecar}" ]]; then
  echo "next-consume.sh: _NEXT_${nnn} already consumed — no-op."
  exit 0
fi

stamp="$(date -u +%Y-%m-%dT%H:%MZ)"
if [[ -n "${REASON}" ]]; then
  printf 'consumed %s — %s\n' "${stamp}" "${REASON}" > "${sidecar}"
else
  printf 'consumed %s\n' "${stamp}" > "${sidecar}"
fi
# A retired slot is no longer "in use" — drop any occupancy hint (next-boot.sh).
# Harmless if absent; keeps next/ from accumulating dead .booted files over time.
rm -f "${NEXT_DIR}/_NEXT_${nnn}.booted"
echo "${sidecar}"
