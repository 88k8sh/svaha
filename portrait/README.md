<div align="center">

# Portrait

### A longitudinal self-portrait, anchored to evidence — an optional Throughline layer.

A mirror that reflects who you are *becoming* by reading your own corpus **and** Throughline's record of how you actually decide over time — every inference cited to the text that supports it, every portrait stored as a frozen dated snapshot, all of it local-first.

**[Throughline →](../README.md)** · [The behavior contract](../CLAUDE.md) · opt-in · MIT

</div>

---

## This is not a new idea

"AI builds a portrait of you" is a **crowded space**, and Portrait does not pretend otherwise. The genre already includes corpus-to-personality recaps (GPTRecap's type system, AI Wrapped), the viral "mirror / roast me" prompts, journaling tools that track your traits over time (Mindsera, Rosebud, Reflection.app), the clone-builders that imitate you to others (Second Me), and the incumbent that already does much of this — ChatGPT's evolving Memory / "Dreaming" profile. ChatGPT's *saved* memories are visible and user-editable; it's the **inferred** "Dreaming" layer — the model it builds about you beyond what it saved — that stays hidden.

So this page makes a **modest, honest** claim: not that Portrait is first, only, or novel — it isn't — but that it's a **differentiated, evidence-anchored take** that improves on a specific set of axes the existing tools handle weakly or not at all. Where a competitor is better or equal, the table below says so plainly.

## What it is

Portrait is an **optional bolt-on** that lives inside Throughline (`throughline/portrait/`). When you turn it on, it synthesizes a **longitudinal "becoming" portrait** — not a one-shot personality type or a mood-of-the-week, but an *arc*: who you were, who you're trending toward, and the diff between snapshots over time.

It draws from two sources at once:

1. **Your own existing corpus** — chat exports, your writing, your work product. Multi-source, already-existing, not journal entries you have to start producing inside someone's app.
2. **Throughline's own decision-history** — the frozen `_NEXT_NNN.md` handoffs, the conviction-vs-outcome calibration record, and the corrections that got promoted to rules. This is a record of *who you are as an operator*: what you actually do under uncertainty, where your high-conviction calls land, what mistakes you make twice.

It is a **mirror, not a mask.** It reflects you back to *you*. It does not build a clone that talks to other people in your voice — that's the opposite lane (Second Me, WeClone), and Portrait stays out of it deliberately.

And it is **anti-Barnum.** The standard failure of every tool in this genre is the horoscope effect — vague, flattering, universally-true statements that feel personal but aren't (the Forer effect). Portrait fights this structurally: **every inference carries a citation to the corpus evidence that produced it, marked `✓VERIFIED` (grounded in a quoted passage) or `?INFERRED` (a reading you can dispute).** A claim you can't trace to evidence is a claim you can delete. The portrait is meant to be argued with.

## How it reuses Throughline's own primitives

Portrait isn't a separate machine bolted on — it's built from the same spine Throughline already runs on:

- **Frozen numbered snapshots.** A portrait is stored exactly like a handoff: an immutable, dated `identity/portraits/_PORTRAIT_NNN.md`. You never rewrite an old one. The **becoming-arc is the diff across snapshots** — the same way the handoff loop never rewrites history.
- **Evidence markers + conviction tags.** The `✓VERIFIED` / `?INFERRED` anchoring and the graded conviction language are the ones already defined in `CLAUDE.md` — Portrait points an existing tool at a new target.
- **Local-first + no-hard-delete.** Same privacy rules as the rest of the system: nothing auto-leaves the machine, superseded snapshots are archived, not deleted.

The structural reason this is hard to copy: the decision-history input doesn't exist outside a context-OS. Journaling and chat tools can read what you *said*; only a system that has been recording your *decisions with their conviction and their outcomes* can read how you actually *operate*. That track record is the input no in-app journal or chat-recap has access to.

## The improvement — honestly scored

The genre is crowded, and Portrait ties or loses on most axes: longitudinal arc (Mindsera, Rosebud, ChatGPT's evolving Memory all track you over time), mirror-not-mask (table-stakes, not a differentiator), multi-source corpus (Second Me ingests yours too), and local-first (GPTRecap and others run client-side too). The gap that's real and wide is exactly **two axes**: (1) **per-claim evidence-anchoring / anti-Barnum** — every inference cites the corpus passage behind it, markered `✓VERIFIED` / `?INFERRED` and disputable (no competitor does this), and (2) **synthesis from your own decision-history** — the input no chat or journaling tool has, because it requires the surrounding context-OS to exist first.

So the supportable claim is the modest one: **Portrait is an improvement on a narrow, honest pair of axes — evidence-anchoring and decision-history synthesis — not the best at everything.** The combination, anchored to a decision-track-record nothing else has, is the part worth building.

## Activate it

Portrait ships inside Throughline — there's nothing extra to clone. It's **off by default** and opt-in; `setup.sh` deliberately does *not* install its commands. To enable it, install the three command files once:

```bash
# opt in — install the Portrait commands (from your Throughline project root):
cp portrait/portrait.md portrait/mirror.md portrait/recall.md ~/.claude/commands/

# then use them from your Throughline project root:
/portrait      # builds (or rebuilds) the current portrait + a new frozen snapshot from your corpus + decision-history
/mirror        # read-only: shows what the portrait infers about you, every line cited and disputable
/recall        # OPTIONAL local semantic search over your corpus — complements grep (one dependency; see below)
```

The first run walks you through pointing it at your corpus (chat exports, a writing folder, your work directory) and reads your existing `next/_NEXT_NNN.md` handoffs and calibration record automatically. Each `/portrait` run refreshes the current synthesis (`identity/PORTRAIT.md`) and mints a new frozen, dated snapshot (`identity/portraits/_PORTRAIT_NNN.md`, immutable once written); the becoming-arc is the diff across them. `/mirror` is the read-only companion — it renders the inferences with their evidence and lets you dispute any line (logged to `identity/disputed.md`, reconciled on the next `/portrait`). Superseded portraits are archived, never overwritten — same numbered-snapshot discipline as the handoff loop.

To turn it off, simply don't run it — nothing in the core loop depends on Portrait.

## Optional: a local semantic-recall layer (`/recall`)

By default, Portrait finds evidence with **grep** — exact, transparent, zero-dependency. That's the right tool for a small corpus or when you know the term. But on a **large imported corpus** (hundreds of chat conversations, a big writing folder) or a **long Throughline history** (dozens of `_NEXT_NNN.md` handoffs), grep misses things you phrased differently than you're now searching for — the passage that *means* "I felt carried" but never uses that word.

`/recall` adds an **optional, local, by-meaning index** for exactly that case. It **complements grep — it does not replace it.** When a `recall.db` exists, `/portrait` and `/mirror` pull candidate evidence *both* ways (semantic **and** grep/structured reads) and cite from both under the same anti-Barnum discipline. When it doesn't exist, both commands behave exactly as today. Nothing changes for small corpora, and nothing in the core loop depends on it.

**It has one real dependency — and we say so plainly.** `/recall` is **not** zero-dependency: it needs a light **local embedding model** (`fastembed` running `BAAI/bge-small-en-v1.5` — an ONNX model, ~130 MB, **no torch, no GPU, no server, no daemon**) plus `sqlite-vec` (a single-file SQLite vector extension — no server, no Docker). That's the whole footprint: two pip packages, one model download cached locally, one `.db` file.

```bash
pip install -r recall/requirements.txt    # the one dependency, disclosed up front
python3 recall/recall.py index            # build the local index from sources.md + your loop history
python3 recall/recall.py query "times I changed my mind under pressure" --k 8
```

- **Local-first.** Embeddings are computed **on your machine** — text never goes to an embedding API. The index `portrait/identity/recall.db` holds real corpus content and is **gitignored**, same as every other live portrait artifact. The repo ships the *method* (`recall/recall.py` + `recall/requirements.txt`); the index is never committed.
- **Opt-in + fail-soft.** If the dependency isn't installed, `recall.py` prints the one-line install command, tells you to use grep, and **exits cleanly** — it never crashes a portrait run. Absent recall = today's behavior.
- **When it helps vs. when grep is fine.** Reach for recall when the corpus is large or the history is long and you're searching *by meaning*. Stay on grep (skip recall entirely) when the corpus is small, when you know the exact term/name/date, or when you need an exhaustive "every occurrence of X" — recall returns a ranked candidate set, grep is complete by construction.
- **It never lowers the citation bar.** A recall hit is *candidate* evidence: the synthesizer still reads the passage, decides if it supports the claim, marks `✓VERIFIED`/`?INFERRED`, and writes the cited `evidence:` line. recall changes how candidates are *found*, not what a claim must clear to be *written*.

Full spec: [`recall.md`](recall.md).

## Privacy contract

This is the hard line, and it's non-negotiable:

- **The repo ships the *method*, not your portrait.** Templates, seeds, the synthesis prompt, and this README are the only Portrait files under version control. Your **filled-in corpus and your portrait snapshots are `.gitignored`** and never committed. Zero personal data in any shipped file.
- **Corpus and portraits stay local.** Your imported corpus and every generated snapshot live on your machine and **never auto-leave it** — same local-first rule as the rest of Throughline. There is no upload, no cloud profile, no telemetry. (Contrast the incumbent, whose *inferred* profile lives on their servers and is hidden from you — its saved memories are visible, but the model it builds beyond them is not.)
- **No hard deletes.** Superseded portraits are archived under `_ARCHIVE/`, not destroyed — your own history of becoming is preserved, the same way handoffs are.
- **The optional recall index follows the same fence.** `identity/recall.db` and the local model cache hold real corpus content and are gitignored / local-only; only the recall *method* (`recall/recall.py` + `requirements.txt`) ships. Embeddings are computed locally — recall adds no path off the machine.

If you fork or share this layer, you share the recipe. You never share the meal.

## License

[MIT](../LICENSE) — same as Throughline. The method is free; your portrait is yours and stays on your machine.
