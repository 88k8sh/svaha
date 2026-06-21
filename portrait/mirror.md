# /mirror — show what the system infers about you (auditable)

**What it is.** `/mirror` surfaces the inferences the Portrait holds about *you* — and, unlike every "AI mirror" competitor, **shows its work.** Every claim it returns is pinned to the actual corpus evidence that produced it, carries a **✓VERIFIED / ?INFERRED / ✗UNCERTAIN** marker, and is **disputable**. Nothing ungrounded is ever shown.

> **The contrast (say this when the user asks "what do you know about me?"):**
> ChatGPT's saved memories are visible and editable — but its **inferred "Dreaming" profile**, the model it builds about you beyond what it saved, evolves silently and stays hidden: you can't see it, check its evidence, or correct it. `/mirror` is the inverse *for that inferred layer*: the profile is a file you own (`identity/PORTRAIT.md`), every line cites its source, and you can mark any line wrong. **What the inferred layer hides, this shows. What it asserts, this lets you falsify.**

This is a **mirror, not a mask** — it reflects you back to *you*. It never builds a clone of you to act as you to others.

---

## Two modes

### Mode A — full mirror (no argument)

`/mirror`

Read `identity/PORTRAIT.md` (the live current portrait) and render every claim it holds, grouped by the portrait's own sections (Stable identity · Becoming / growth · Unresolved tensions · Operator-patterns). For each claim emit the **audit line** (format below). Do not summarize, soften, or add claims that aren't in the file — render what's there, with its evidence intact.

If `identity/PORTRAIT.md` does not exist yet, say so plainly and point to `identity/PORTRAIT.template.md` + the go-live `cp` in `.gitignore`. Do **not** invent a portrait.

### Mode B — focused question

`/mirror what do you infer about how I make decisions?`
`/mirror what are you least sure about?`
`/mirror where have I disputed you?`

Answer **strictly from cited evidence in `identity/PORTRAIT.md`** (and `identity/disputed.md` for dispute-history questions). Pull only the claims whose section/subject matches the question, render each as an audit line, and stop.

**Optional recall — to *locate* matching claims, never to *invent* them.** If the live portrait is large and the question is by-meaning, you may use the optional `/recall` layer (spec: `recall.md`) to find which claims are relevant: if `portrait/identity/recall.db` exists, run `python3 recall/recall.py query "<the question>" --k 8` to surface candidate corpus passages, then map their `file:line` citations to the claims in `PORTRAIT.md` that cite the same source. If recall is absent/broken (no db, or the query prints the install note), grep `PORTRAIT.md` for matching claims exactly as today — never block on recall. **Hard limit:** recall only helps *select* which already-written, already-cited claims to render. It never adds a claim that isn't in `PORTRAIT.md`, and a recall hit with no corresponding portrait claim is **not** an answer — the grounded-only rule below still governs. recall finds; it does not infer.

**Hard rule — grounded-only.** If the question asks about something the portrait has **no cited claim** for, say exactly that:
> `No grounded claim on <topic>. The portrait infers nothing here that cites evidence — I won't guess.`
Never fill the gap from general reasoning, the chat session, or vibes. An ungrounded answer defeats the entire point of this tool. Absence of evidence is a *reportable result*, not a prompt to improvise.

---

## The audit line (the unit of output)

Every claim is rendered as:

```
<claim, one sentence>
  marker:     ✓VERIFIED | ?INFERRED | ✗UNCERTAIN
  confidence: <high|medium|low>
  evidence:   <source-id> → "<short quote or pointer>"   [+ more if multi-source]
  disputable: reply `/mirror dispute "<claim>"` if this is wrong
```

- **marker** mirrors CLAUDE.md's claim-verification markers: **✓VERIFIED** = drawn from text the user actually wrote/said in the corpus and quoted; **?INFERRED** = a pattern read across evidence, not a direct quote; **✗UNCERTAIN** = a weak read, shown only because the user asked and it's flagged as weak.
- **evidence** must resolve to a real entry in `identity/sources.md` (a `<source-id>`) plus a locator. A claim with no resolvable evidence is **not shown** — it's a bug in the portrait, report it as `⚠ unanchored claim — drop or anchor before next repaint`.
- **confidence** is the portrait's stated confidence; never upgrade it at render time.

**Never launder a marker.** A `?INFERRED` pattern is not reported as a fact. The marker is the honesty layer — if you can't cite it, you can't claim it.

---

## Disputing (the anti-Barnum loop)

`/mirror dispute "<claim>"`  → append the claim to `identity/disputed.md` with today's date, reason (ask the user one line: wrong / overreaching / outdated), and mark it `OPEN`.

Disputes are the falsifiability mechanism that kills the horoscope/Forer problem: a claim the user can't push back on is a fortune cookie. On the next repaint (`/portrait`), every `OPEN` dispute **must** be reconciled — the claim is corrected, narrowed, or dropped, and the dispute marked `RESOLVED` with what changed. A claim disputed **twice** (2-strike, mirrors the calibration loop) is dropped, not just softened, and the pattern that generated it is marked `DISTRUST` in future synthesis.

`/mirror` never argues with a dispute. The user's read of themselves outranks the inference — log it, don't defend it.

---

## Guardrails

- **Read-only.** `/mirror` reads `PORTRAIT.md` / `sources.md` / `disputed.md` and (in dispute mode) appends to `disputed.md`. It never rewrites the portrait — that's `/portrait`'s job.
- **Local-first.** Output stays in the session. The portrait and its corpus never auto-leave the machine (CLAUDE.md Privacy). If asked to export, route through the normal release/outbox gate, never silently. The optional recall index (`identity/recall.db`) is local-only and gitignored — same rule.
- **Recall is optional + find-only.** If `recall.db` is absent or its deps are missing, `/mirror` behaves exactly as today (grep over `PORTRAIT.md`). When present, recall only helps locate already-cited claims; it never adds an ungrounded one. No-invention still wins.
- **No invention.** Every line traces to cited evidence or it isn't shown. The whole value proposition is that this is the auditable mirror — break grounding and it's just another horoscope.
