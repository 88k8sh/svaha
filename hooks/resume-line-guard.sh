#!/usr/bin/env bash
# Stop hook — enforce the session closer invariant (CLAUDE.md).
# A handoff's "Next session: /session NNN" MUST resolve to an existing frozen
# <system-dir>/next/_NEXT_NNN.md. This catches the failure mode where a closer is
# emitted with a placeholder number or a number that was never written.
#
# Non-blocking: emits a corrective systemMessage only. Never sets continue:false.

input=$(cat)
tp=$(printf '%s' "$input" | jq -r '.transcript_path // empty' 2>/dev/null)
sid=$(printf '%s' "$input" | jq -r '.session_id // "unknown"' 2>/dev/null)

if [ -z "$tp" ] || [ ! -f "$tp" ]; then exit 0; fi

# Pull the most recent "Next session: /session NNN" line from assistant text.
closer_line=$(jq -rc 'select(.type=="assistant") | (.message.content[]? | select(.type=="text") | .text)' "$tp" 2>/dev/null \
  | grep -iE '^[[:space:]]*Next session:[[:space:]]*/session[[:space:]]+[0-9]+' | tail -1)

# No closer emitted -> nothing to enforce.
if [ -z "$closer_line" ]; then exit 0; fi

# Extract the session number; force base-10. A leading-zero "041" would otherwise
# be misread as octal by printf %d (→ _NEXT_033) and "08"/"09" would crash it.
num=$(printf '%s' "$closer_line" | grep -oE '/session[[:space:]]+[0-9]+' | grep -oE '[0-9]+' | head -1)
if [ -z "$num" ]; then exit 0; fi
num=$((10#$num))

fname=$(printf '_NEXT_%03d.md' "$num")
cfile=$(printf '_NEXT_%03d.consumed' "$num")
nextdir="<system-dir>/next"

# Two failure modes for the closer: the named _NEXT doesn't exist, or it exists
# but is already CONSUMED (its moves are done) — /session N would replay it.
problem=""
if [ ! -f "${nextdir}/${fname}" ]; then
  problem="does not exist"
elif [ -f "${nextdir}/${cfile}" ]; then
  problem="is already CONSUMED (moves done) — re-point at a live _NEXT or mint a new one"
fi

# No problem -> nothing to enforce.
if [ -z "$problem" ]; then exit 0; fi

# Debounce: at most once per 30 s per session (avoids double-fire on the same stop).
sentinel="${TMPDIR:-/tmp}/claude-resume-guard-${sid}"
now=$(date +%s)
if [ -f "$sentinel" ]; then
  last=$(cat "$sentinel" 2>/dev/null || echo 0)
  if [ $((now - last)) -lt 30 ]; then exit 0; fi
fi
echo "$now" > "$sentinel" 2>/dev/null

printf '{"systemMessage":"⚠ SESSION CLOSER INVARIANT — the closer you just emitted has /session %s but <system-dir>/next/%s %s. Run /handoff to mint a live _NEXT (or re-point at a still-live file), then re-emit the closer."}\n' "$num" "$fname" "$problem"
exit 0
