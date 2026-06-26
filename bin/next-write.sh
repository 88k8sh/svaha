#!/usr/bin/env bash
# next-write.sh <system-dir> <content-file>
# Writes the next numbered _NEXT_NNN.md in <system-dir>/next/.
#
# All handoffs live in one folder: <system-dir>/next/
# No archiving sweep — the folder is the single source of truth.
#
# _NEXT_000 / _NEXT_001 are permanent and never removed.
# The unnumbered _NEXT.md pointer/spec at <system-dir>/_NEXT.md is never touched.
# Numbers auto-expand: 001–999 (3 digits), 1000–9999 (4), etc.
#
# Two stamps are applied to the written file:
#   1. Focus label  — "# __FOCUS__ <label>" line 1 → "# _NEXT_NNN — <label>".
#   2. Checkpoint    — the "__CHECKPOINT__" sentinel in the `checkpoint:` line →
#                      `git rev-parse --short HEAD` (or "n/a" outside a repo). This
#                      is the Verified-Handoff anchor the next boot diffs against.
# Both stamps are no-ops if the sentinel is absent (backward-compatible).
#
# Usage: next-write.sh /absolute/path/to/system-dir /tmp/handoff_content.md [--consume NNN]

set -euo pipefail

SYSTEM_DIR="${1:?Usage: next-write.sh <system-dir> <content-file> [--consume NNN]}"
CONTENT_FILE="${2:?Usage: next-write.sh <system-dir> <content-file> [--consume NNN]}"

# Freshness/ownership guard (the _NEXT_070 mis-mint backstop). A handoff content
# file is ALWAYS written seconds before this runs, by the current user. Refuse a
# stale or foreign-owned content file so a leftover at a FIXED /tmp path can never
# be blindly minted + consumed against. Caught in the origin system: a fixed temp
# name (/tmp/handoff_next.md) collided with a 2-day-old file owned by another user
# → its content was minted as _NEXT_070 and consumed the real _NEXT_068. Always
# write the content to a UNIQUE mktemp path; this guard is the backstop that makes
# the stale-content class impossible. (The owner check below is platform-aware —
# BSD `stat -f %Su` vs GNU `stat -c %U`; the mtime check via find -mmin is portable.)
if [[ ! -f "${CONTENT_FILE}" ]]; then
  echo "next-write.sh: content file '${CONTENT_FILE}' not found." >&2
  exit 1
fi
if [[ -n "$(find "${CONTENT_FILE}" -mmin +60 2>/dev/null)" ]]; then
  echo "next-write.sh: content file '${CONTENT_FILE}' is >60 min old — refusing to mint" >&2
  echo "  possibly-stale content. A handoff file is written seconds before minting; regenerate" >&2
  echo "  it to a unique path (mktemp), then re-run." >&2
  exit 1
fi
# Owner: BSD stat uses `-f %Su`, GNU coreutils uses `-c %U`. Detect explicitly —
# `stat -f '%Su' FILE` does NOT fail-soft on GNU (`-f` there means --file-system,
# so it exits 0 printing a filesystem blob that an OR-chain would mistake for the
# owner, falsely rejecting every mint). A real-Linux container run caught this 2026-06-25.
if stat --version >/dev/null 2>&1; then
  owner="$(stat -c '%U' "${CONTENT_FILE}" 2>/dev/null || echo '')"   # GNU/Linux
else
  owner="$(stat -f '%Su' "${CONTENT_FILE}" 2>/dev/null || echo '')"  # BSD/macOS
fi
if [[ -n "${owner}" && "${owner}" != "$(id -un)" ]]; then
  echo "next-write.sh: content file '${CONTENT_FILE}' is owned by '${owner}', not you — refusing" >&2
  echo "  (the cross-user /tmp-collision signature). Write your handoff to a unique mktemp path." >&2
  exit 1
fi

NEXT_DIR="${SYSTEM_DIR}/next"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Optional --consume NNN: the slot THIS handoff booted from, retired atomically
# AFTER the new slot is written + checkpoint-stamped (consume-leak fix, layer A).
# Folding the retire into the mint makes "mint successor + retire predecessor"
# ONE operation — you cannot mint a successor while forgetting to retire the
# predecessor, and the predecessor is never retired before its successor exists.
CONSUME_NNN=""
if [[ "${3:-}" == "--consume" ]]; then
  CONSUME_NNN="${4:?--consume requires a slot number, e.g. --consume 065}"
fi

# Sanity guard: SYSTEM_DIR must be the real system root, identified by its
# permanent _NEXT.md pointer/spec. Without this, a cwd-relative or mistyped path
# silently creates a fresh next/ tree and restarts numbering at 001 — which can
# collide with another session's parallel slots. Fail loud instead of mis-writing.
if [[ ! -f "${SYSTEM_DIR}/_NEXT.md" ]]; then
  echo "next-write.sh: '${SYSTEM_DIR}/_NEXT.md' not found — SYSTEM_DIR is not the system root." >&2
  echo "  Pass an absolute path: next-write.sh /absolute/path/to/system-dir <content-file>" >&2
  exit 1
fi

# Kit guard (v0.6.2): the Svaha kit ships its own _NEXT.md spec, so the root-guard
# above passes for the kit dir — but the kit is NOT a user system; minting here would
# pollute the shipped repo (the kit-as-system-dir footgun). A .svaha-kit marker flags it.
if [[ -f "${SYSTEM_DIR}/.svaha-kit" ]]; then
  echo "next-write.sh: '${SYSTEM_DIR}' is the Svaha kit (.svaha-kit present), not a user system — refusing to mint." >&2
  echo "  Run /init in your own project, or scope the handoff to your personal system." >&2
  exit 1
fi

num_of()    { local b; b=$(basename "$1"); b=${b#_NEXT_}; printf '%s' "${b%.md}"; }
width_for() { if (( $1 > 9999 )); then echo 5; elif (( $1 > 999 )); then echo 4; else echo 3; fi; }
slot()      { local w; w=$(width_for "$1"); printf "%s/_NEXT_%0${w}d.md" "${NEXT_DIR}" "$1"; }

mkdir -p "${NEXT_DIR}"

# Highest existing number in the next/ folder so numbers never repeat.
shopt -s nullglob
latest=0
for f in "${NEXT_DIR}"/_NEXT_*.md; do
  n=$(num_of "${f}")
  if (( 10#${n} > latest )); then latest=$(( 10#${n} )); fi
done
shopt -u nullglob

next=$(( latest + 1 ))
out="$(slot "${next}")"
# Atomic reserve (closes the simultaneous-mint TOCTOU). Reserve the slot with an
# O_EXCL create via `noclobber` rather than a check-then-write: if a concurrent
# session already grabbed this number — OR wins the race for it in the same instant —
# the create fails and we bump on. The old `while [[ -e ]]` guard only caught the
# SEQUENTIAL case; two mints interleaving between the test and the write both passed
# it and both wrote the same slot, silently clobbering one session's handoff. We now
# exclusively own "${out}" (an empty file) before any content is written into it.
until ( set -o noclobber; : > "${out}" ) 2>/dev/null; do
  next=$(( next + 1 ))
  out="$(slot "${next}")"
done

# Crash/empty-mint cleanup: the reserve above creates an EMPTY "${out}" before any
# content is written. A mid-mint crash — or the empty-slot guard in the --consume
# branch below — would otherwise leave a 0-byte _NEXT_NNN.md that BURNS the slot
# number and makes `next-live.sh --check` report a permanent false desync until it's
# removed by hand. This EXIT trap drops "${out}" on ANY exit while it is still
# zero-bytes; once real content lands it is non-empty, so the trap is a no-op on the
# success path. Preserves the real exit code so callers still see mint failures.
trap 'rc=$?; if [[ -n "${out:-}" && -f "${out}" && ! -s "${out}" ]]; then rm -f "${out}"; fi; exit $rc' EXIT

# Focus-label stamp: if line 1 is the sentinel "# __FOCUS__ <label>", rewrite it
# to "# _NEXT_NNN — <label>" (NNN = resolved slot, padded to the filename's width).
# No sentinel → copy verbatim (backward-compatible with title-less handoffs).
first_line=$(head -n 1 "${CONTENT_FILE}")
sentinel='# __FOCUS__ '
if [[ "${first_line}" == "${sentinel}"* ]]; then
  w=$(width_for "${next}")
  label=${first_line#${sentinel}}
  header=$(printf '# _NEXT_%0*d — %s' "${w}" "${next}" "${label}")
  { printf '%s\n' "${header}"; tail -n +2 "${CONTENT_FILE}"; } > "${out}"
else
  cp "${CONTENT_FILE}" "${out}"
fi

# Checkpoint stamp (the Verified-Handoff anchor): resolve the git short-SHA at
# handoff time and substitute it for the literal "__CHECKPOINT__" sentinel that
# the handoff template leaves in the `checkpoint:` line. The next boot diffs
# <checkpoint>..HEAD to verify the world still matches the handoff's claims.
#   - In a git repo: use `git rev-parse --short HEAD`.
#   - Not a repo (or HEAD unborn): stamp "n/a" — boot falls back to grep-only checks.
# bash-3.2 safe: no sed -i (non-portable on macOS), no mapfile; a single awk pass
# only on the first matching sentinel keeps it dependency-light and idempotent.
# A handoff that hard-typed its own SHA (no sentinel) is left untouched.
if git -C "${SYSTEM_DIR}" rev-parse --git-dir >/dev/null 2>&1; then
  checkpoint=$(git -C "${SYSTEM_DIR}" rev-parse --short HEAD 2>/dev/null || printf 'n/a')
  [[ -n "${checkpoint}" ]] || checkpoint='n/a'
else
  checkpoint='n/a'
fi
if grep -q '__CHECKPOINT__' "${out}"; then
  tmp="${out}.tmp.$$"
  awk -v sha="${checkpoint}" '
    !done && /__CHECKPOINT__/ { sub(/__CHECKPOINT__/, sha); done=1 }
    { print }
  ' "${out}" > "${tmp}" && mv "${tmp}" "${out}"
fi

# Layer A: retire the booted-from slot ONLY now that the successor exists and is
# non-empty — so carry-forward (which lives in the new slot) always precedes the
# retire, and a failed/empty write never retires its predecessor. Consume output
# goes to stderr so stdout stays the single new-filename contract callers read.
if [[ -n "${CONSUME_NNN}" ]]; then
  if [[ ! -s "${out}" ]]; then
    echo "next-write.sh: new slot '${out}' is empty — NOT consuming _NEXT_${CONSUME_NNN}." >&2
    exit 1
  fi
  "${SCRIPT_DIR}/next-consume.sh" "${SYSTEM_DIR}" "${CONSUME_NNN}" "superseded by $(basename "${out}" .md)" >&2 \
    || echo "next-write.sh: warning — wrote ${out} but failed to consume _NEXT_${CONSUME_NNN}; stamp it by hand with bin/next-consume.sh." >&2
fi

echo "${out}"
