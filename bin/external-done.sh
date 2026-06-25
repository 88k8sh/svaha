#!/usr/bin/env bash
# external-done.sh <system-dir> <predecessor> <superseder> [note]
# The SINGLE WRITER for the EXTERNAL_DELIVERABLES.md out-of-tree supersession
# registry.
#
# WHY THIS EXISTS (the out-of-tree-staleness fix)
# In-tree work writes a completion signal the boot sweep can read: a (_NEXT_NNN)
# CHANGELOG marker, a .consumed sidecar, or — in a git repo — a commit log.
# OUT-OF-TREE deliverables — a shipped package, an essay, a sibling repo, anything
# that lives OUTSIDE this <system-dir> root — write NO such signal. So a move that
# was finished out-of-tree leaves its _NEXT slot reading live; re-minted into a
# fresh slot it defeats every mtime/staleness gate. This registry is that missing
# channel: the COMPLETING session records the supersession here; boot.md's Step B
# reads it FIRST on every boot.
#
# It is the WRITER, not the POLICY — it records a supersession the caller has
# already adjudicated; it never decides liveness and never retires a slot.
# Append-only (the append-only-logs rule — NOT numbered snapshots). Idempotent on
# an identical (predecessor -> superseder) pair (grep-before-append). bash-3.2-safe.
#
# Usage: external-done.sh <system-dir> <predecessor> "<superseder>" "<note>"
#   e.g. external-done.sh "$(pwd)" my-context-kit-v1 "acme-context plugin" \
#          "_NEXT_007 m2; source archived to _ARCHIVE/"

set -uo pipefail

SYSTEM_DIR="${1:?Usage: external-done.sh <system-dir> <predecessor> <superseder> [note]}"
PRED="${2:?Usage: external-done.sh <system-dir> <predecessor> <superseder> [note] — predecessor (the superseded deliverable) required}"
SUPER="${3:?Usage: external-done.sh <system-dir> <predecessor> <superseder> [note] — superseder (what replaced it) required}"
NOTE="${4:-}"

# Fields are written into a markdown table cell — a literal '|' would split the
# row into a malformed extra column. Deliverable names never contain one, so
# refuse loudly rather than silently corrupt the registry.
case "${PRED}${SUPER}${NOTE}" in
  *"|"*) echo "external-done.sh: a field contains '|', which would break the registry table — remove it." >&2; exit 1 ;;
esac

# Root guard: SYSTEM_DIR must be the real system root, identified by its permanent
# _NEXT.md pointer — never write into the wrong tree from a cwd-relative or
# mistyped path.
if [ ! -f "${SYSTEM_DIR}/_NEXT.md" ]; then
  echo "external-done.sh: '${SYSTEM_DIR}/_NEXT.md' not found — SYSTEM_DIR is not the system root." >&2
  echo "  Pass an absolute path: external-done.sh <system-dir> <pred> <super> [note]" >&2
  exit 1
fi

# Ledger dir: this kit keeps it at ledger/; an aakash_os-style tree at 30_LEDGER/.
# Accept either so the writer is portable across both layouts.
LEDGER_DIR=""
for _d in "${SYSTEM_DIR}/ledger" "${SYSTEM_DIR}/30_LEDGER"; do
  [ -d "${_d}" ] && { LEDGER_DIR="${_d}"; break; }
done
if [ -z "${LEDGER_DIR}" ]; then
  echo "external-done.sh: no ledger/ or 30_LEDGER/ under '${SYSTEM_DIR}'." >&2
  exit 1
fi
REG="${LEDGER_DIR}/EXTERNAL_DELIVERABLES.md"

# Create with a header if absent — append-only thereafter, never rewritten.
if [ ! -f "${REG}" ]; then
  {
    printf '# EXTERNAL_DELIVERABLES — out-of-tree supersession registry\n\n'
    printf '> **Append-only.** The missing completion signal for deliverables that live\n'
    printf '> OUTSIDE this tree (a shipped package, an essay, a sibling repo — anything not\n'
    printf '> under this `<system-dir>` root). They write no `(_NEXT_NNN)` CHANGELOG marker,\n'
    printf '> no `.consumed` sidecar, and no commit here — so a finished out-of-tree move\n'
    printf '> leaves its `_NEXT` slot reading live and can re-mint into a fresh slot that\n'
    printf '> defeats every staleness gate. The COMPLETING session records the supersession\n'
    printf '> here via `bin/external-done.sh`; `boot.md` reads it FIRST on every boot.\n'
    printf '> **Never edit a line — only append.**\n\n'
    printf '| recorded (UTC) | predecessor → superseder | note (slot + provenance) |\n'
    printf '|---|---|---|\n'
  } > "${REG}"
fi

# Idempotent: skip if this exact (predecessor → superseder) pair is already on file.
if grep -qF "| ${PRED} → ${SUPER} |" "${REG}" 2>/dev/null; then
  echo "external-done.sh: '${PRED} → ${SUPER}' already recorded — no-op."
  exit 0
fi

stamp="$(date -u +%Y-%m-%dT%H:%MZ)"
printf '| %s | %s → %s | %s |\n' "${stamp}" "${PRED}" "${SUPER}" "${NOTE:-—}" >> "${REG}"
echo "${REG}"
