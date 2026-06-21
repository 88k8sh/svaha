#!/usr/bin/env bash
# PostToolUse hook — context compression canary.
# Fires after every tool call. Throttled to check every 10 calls per session.
# Two alert levels: yellow (warn) and red (write _NEXT.md now).
# Non-blocking: emits systemMessage only, never sets continue:false.
#
# Trigger = transcript BYTE-SIZE (a proxy for context fill). It's a heads-up, not
# ground truth — bytes-on-disk loosely track the model's real context fill — so
# the explicit "that's it" remains the reliable wrap-up path. Each level fires at
# most once per session.

input=$(cat)
tp=$(printf '%s' "$input" | jq -r '.transcript_path // empty' 2>/dev/null)
sid=$(printf '%s' "$input" | jq -r '.session_id // "unknown"' 2>/dev/null)

if [ -z "$tp" ] || [ ! -f "$tp" ]; then exit 0; fi

# Throttle: fire every 10 tool calls using a per-session counter.
counter_file="${TMPDIR:-/tmp}/claude-canary-count-${sid}"
count=$(cat "$counter_file" 2>/dev/null || echo 0)
count=$((count + 1))
echo "$count" > "$counter_file"
if [ $((count % 10)) -ne 0 ]; then exit 0; fi

# Sentinels: fire each level at most once per session.
yellow_sentinel="${TMPDIR:-/tmp}/claude-canary-yellow-${sid}"
red_sentinel="${TMPDIR:-/tmp}/claude-canary-red-${sid}"

# Transcript byte-size (macOS: stat -f%z; Linux fallback: stat -c%s).
size=$(stat -f%z "$tp" 2>/dev/null || stat -c%s "$tp" 2>/dev/null || echo 0)

YELLOW=400000   # ~400 KB — heads up, think about wrapping up
RED=700000      # ~700 KB — write _NEXT.md now, compression is close

if [ "${size:-0}" -ge "$RED" ] && [ ! -f "$red_sentinel" ]; then
    touch "$red_sentinel"
    printf '{"systemMessage":"🔴 CONTEXT CANARY — RED: transcript ~%dKB. Compression is likely close. Write _NEXT.md NOW (pending work, open moves, model tier) before context degrades. Do this on the next natural pause — do not wait for Stop."}\n' $((size / 1024))
    exit 0
fi

if [ "${size:-0}" -ge "$YELLOW" ] && [ ! -f "$yellow_sentinel" ]; then
    touch "$yellow_sentinel"
    printf '{"systemMessage":"🟡 CONTEXT CANARY — YELLOW: transcript ~%dKB. Context is getting heavy. Start thinking about a wrap-up: flag reboot point, note open moves, prepare _NEXT.md. Red alert fires around 700KB."}\n' $((size / 1024))
    exit 0
fi

exit 0
