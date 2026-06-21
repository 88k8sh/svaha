#!/usr/bin/env bash
# SessionStart hook — drop a per-session start marker.
#
# WHY: session-end-backstop.sh needs to know whether a _NEXT_NNN.md was written
# DURING this session. The precise way to answer that is "any _NEXT file newer than
# the moment this session started". This hook stamps that moment as a marker file
# keyed by session_id. The backstop reads it; without it the backstop falls back to
# a coarse 6-hour time window, which is fine but less precise.
#
# Trivial + fail-soft: reads the SessionStart stdin JSON, touches one temp file,
# exits 0. Never blocks (SessionStart cannot block anyway).
# Reads stdin JSON: { session_id, source, hook_event_name, ... }.

input=$(cat)
sid=$(printf '%s' "$input" | jq -r '.session_id // "unknown"' 2>/dev/null)
[ -z "$sid" ] && sid="unknown"
touch "${TMPDIR:-/tmp}/claude-session-start-${sid}" 2>/dev/null
exit 0
