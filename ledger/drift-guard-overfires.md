# drift-guard over-fires

Log of drift-guard fires that were **noise** — the hook fired but no real coupling
applied (a prose edit that tripped a pattern, a path that matched too broadly). The
counterpart to `drift-guard-evidence.md` (real catches). `/audit` Tier 2 reads this to
decide whether a `§` trigger is too broad and should be tightened.

**How to use:** when the drift-guard fires and you judge it a false positive, append a
block. When you actually tighten the trigger that was over-firing, add a `Counter reset`
or `(resolved)` line so `/audit` starts that `§`'s count fresh.

Format per entry:

```
## YYYY-MM-DD — §N over-fire on `<file>`
- **Fired:** <which coupling message fired>
- **Why noise:** <why no real coupling applied>
- **Refinement hint:** <how the pattern could be tightened>
```

When a tightening lands:

```
## YYYY-MM-DD — §N Counter reset (resolved)
- Tightened: <what changed in drift-guard.py>
```

---

*(no over-fires logged yet — the baseline is young; see `drift-guard-evidence.md` for real catches)*
