#!/usr/bin/env bash
# Stop hook — nudge a lightweight memory reflection as a session winds down.
# Non-blocking: emits a systemMessage only. Never sets continue:false.
#
# Tiered firing (gate per-turn nudging on medium+):
#   < 5 KB transcript        -> skip (trivial / empty session, nothing to reflect on)
#   5 KB .. 400 KB  (light)  -> fire ONCE per session. A short session that genuinely
#                               ends still gets one reflection prompt, but you are NOT
#                               nagged every turn while a light session is still active.
#   >= 400 KB     (medium+)  -> fire EVERY stop (30 s debounce). Consistent nudging once
#                               the session is substantive — capture memory before context
#                               degrades. 400 KB = the medium tier, same threshold the
#                               context-canary (YELLOW) and the CLAUDE.md gauge use.
#
# Design: keep the prompt minimal so Claude uses Haiku-equivalent effort (fast, cheap).
# The full /reflect command spec lives in ~/.claude/commands/reflect.md. Because reflect
# is idempotent and auto-downgrades when nothing is pending, firing it is always safe —
# if the session keeps going, no harm done.

input=$(cat)
tp=$(printf '%s' "$input" | jq -r '.transcript_path // empty' 2>/dev/null)
sid=$(printf '%s' "$input" | jq -r '.session_id // "unknown"' 2>/dev/null)

# No transcript -> nothing to reflect on.
if [ -z "$tp" ] || [ ! -f "$tp" ]; then exit 0; fi

# Byte size (macOS: stat -f%z; Linux fallback: stat -c%s).
size=$(stat -f%z "$tp" 2>/dev/null || stat -c%s "$tp" 2>/dev/null || echo 0)

FLOOR=5000      # below this = trivial/empty session, skip entirely
MEDIUM=400000   # ~400 KB = medium tier (matches context-canary YELLOW + CLAUDE.md gauge)

# Trivial session: never fire.
if [ "${size:-0}" -lt "$FLOOR" ]; then exit 0; fi

if [ "${size:-0}" -lt "$MEDIUM" ]; then
  # LIGHT tier: fire at most once per session (no time expiry).
  light_sentinel="${TMPDIR:-/tmp}/claude-memory-reflect-light-${sid}"
  if [ -f "$light_sentinel" ]; then exit 0; fi
  touch "$light_sentinel" 2>/dev/null
else
  # MEDIUM+ tier: fire every stop, debounced 30 s to avoid a double-fire on the same
  # stop event (still re-fires after the session continues and stops again).
  debounce="${TMPDIR:-/tmp}/claude-memory-reflect-${sid}"
  now=$(date +%s)
  if [ -f "$debounce" ]; then
    last=$(cat "$debounce" 2>/dev/null || echo 0)
    if [ $((now - last)) -lt 30 ]; then exit 0; fi
  fi
  echo "$now" > "$debounce" 2>/dev/null
fi

printf '{"systemMessage":"Session winding down — run /reflect now to capture any memory-worthy findings before the session closes. Keep it fast: update or create only memories that pass the bar (a future Claude would behave differently having read them). Reflect auto-escalates to /handoff if there is in-flight work or a queue. Emit the one-line reflect: summary when done."}\n'
exit 0
