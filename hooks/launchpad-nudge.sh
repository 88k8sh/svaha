#!/usr/bin/env bash
# Stop hook — once per HEAVY session, surface a wrap-up nudge.
# Non-blocking by design: emits ONLY a systemMessage (shown to the user, and visible
# to Claude on the next turn). It never sets continue:false or decision:block, so it
# cannot force continuation or block stopping. Stays SILENT on short sessions.
#
# Trigger = transcript BYTE-SIZE (a proxy for a long / token-heavy session). Fires
# at most once per session (sentinel).
# Reads the Stop-hook stdin JSON: { transcript_path, session_id, ... }

input=$(cat)
tp=$(printf '%s' "$input" | jq -r '.transcript_path // empty' 2>/dev/null)
sid=$(printf '%s' "$input" | jq -r '.session_id // "unknown"' 2>/dev/null)

# No transcript -> nothing to measure.
if [ -z "$tp" ] || [ ! -f "$tp" ]; then exit 0; fi

# Fire at most once per session.
sentinel="${TMPDIR:-/tmp}/claude-launchpad-nudge-${sid}"
if [ -f "$sentinel" ]; then exit 0; fi

# Transcript byte-size (macOS: stat -f%z; Linux fallback: stat -c%s).
size=$(stat -f%z "$tp" 2>/dev/null || stat -c%s "$tp" 2>/dev/null || echo 0)

THRESHOLD=1200000   # ~1.2 MB transcript ~= a long / token-heavy session
if [ "${size:-0}" -lt "$THRESHOLD" ]; then exit 0; fi

touch "$sentinel" 2>/dev/null
printf '{"systemMessage":"Heavy session (large transcript) — a natural wrap-up point. Offer the user: (1) a reboot-point flag, (2) a model-tier / efficiency / cost note, (3) a next-session launchpad handoff."}\n'
exit 0
