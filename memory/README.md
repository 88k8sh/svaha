# memory/

Persistent behavioral memory. Each file captures one rule, preference, or fact
that should shape how Claude operates in future sessions.

## Types

| Type | When to save | Example |
|---|---|---|
| `user` | Role, expertise, preferences | "user is a backend engineer, new to the frontend" |
| `feedback` | Corrections + confirmed non-obvious approaches | "don't summarize at end of response — user can read the diff" |
| `project` | Ongoing work, goals, decisions, deadlines | "merge freeze begins 2026-03-05 for mobile release" |
| `reference` | Pointers to external systems | "bugs tracked in Linear project INGEST" |

## File format

```markdown
---
name: short-kebab-case-slug
description: one-line summary — used to decide relevance in future sessions
metadata:
  type: user | feedback | project | reference
---

Memory body. For feedback/project: lead with the rule/fact, then **Why:** and **How to apply:** lines.
Link related memories with [[their-name]].
```

## Write guard (mandatory)

Before writing any memory file, scan `MEMORY.md` and state one of:
- `no overlap` — then write the new file
- `updating [name]` — then edit the existing file

This check must be visible. It prevents duplicates at write time.

## Content placement

- Behavioral corrections → `memory/` files
- Universal rules that apply every session → `CLAUDE.md`
- Stable system facts → `_LOADUP.md §2`
- Never duplicate across locations — pick one, keep it there

## Bar (both must pass before saving)

1. Would a future Claude behave differently after reading this entry?
2. Would that behavioral difference change the outcome of a real task in a meaningful way?

If either fails, skip it.
