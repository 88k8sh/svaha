#!/usr/bin/env python3
"""
recall.py — OPTIONAL, LOCAL semantic-recall layer for Portrait.

WHAT THIS IS
  A fuzzy, meaning-based search over Portrait's corpus. You ask in natural
  language ("times I changed my mind under pressure") and it returns the most
  semantically-similar chunks, each with a citation (file:line) and a similarity
  score, so a caller can evidence-anchor a claim.

WHAT THIS IS NOT
  It does NOT replace grep. grep is exact, transparent, and always available.
  This COMPLEMENTS grep: grep finds the literal string; recall finds the idea
  even when the words differ. Use grep when you know the term; use recall when
  you only know the shape of what you're looking for.

DEPENDENCIES (honest disclosure — this is NOT zero-dep)
  - sqlite-vec : single-file SQLite vector extension (no server, no daemon).
  - fastembed  : light local ONNX embedding model (BAAI/bge-small-en-v1.5,
                 ~130 MB downloaded + cached on first run). No torch.
  Pure-stdlib otherwise. If either import fails, this script prints the one-line
  install command and exits 0 (fail-soft) — it never crashes the caller, and it
  points you back to grep.

PRIVACY
  The built index (identity/recall.db) holds real corpus content and is
  gitignored / local-only. This script and requirements.txt ship the METHOD
  only — zero personal data.

USAGE
  python3 recall/recall.py index            # build/refresh the index
  python3 recall/recall.py query "<text>" [--k 5]
"""

from __future__ import annotations

import argparse
import os
import re
import sqlite3
import struct
import sys
from pathlib import Path

# --------------------------------------------------------------------------
# Paths (all anchored to this file so it runs from any cwd).
# --------------------------------------------------------------------------
HERE = Path(__file__).resolve().parent                 # .../portrait/recall
PORTRAIT_DIR = HERE.parent                              # .../portrait
IDENTITY_DIR = PORTRAIT_DIR / "identity"
THROUGHLINE_DIR = PORTRAIT_DIR.parent                  # .../throughline

DB_PATH = IDENTITY_DIR / "recall.db"
MODEL_CACHE = HERE / ".model_cache"                    # gitignored; fastembed cache

# Live sources manifest preferred; template is a fallback so a fresh clone can
# still demonstrate the wiring (it carries placeholder paths that won't resolve,
# which is fine — they're simply skipped).
SOURCES_LIVE = IDENTITY_DIR / "sources.md"
SOURCES_TEMPLATE = IDENTITY_DIR / "sources.template.md"

# Svaha-loop corpus (always-on, structurally-unique source class).
NEXT_DIR = THROUGHLINE_DIR / "next"
LEDGER_DIR = THROUGHLINE_DIR / "30_LEDGER"

MODEL_NAME = "BAAI/bge-small-en-v1.5"
EMBED_DIM = 384                                        # bge-small-en-v1.5 dim

# Chunking: character-window with overlap. Sensible defaults for prose/markdown.
CHUNK_CHARS = 900
CHUNK_OVERLAP = 200

TEXT_EXTS = {".md", ".txt", ".json", ".markdown", ".text"}

INSTALL_HINT = "pip install -r recall/requirements.txt"


# --------------------------------------------------------------------------
# Fail-soft dependency loading.
# --------------------------------------------------------------------------
def _load_deps():
    """Import optional deps. On failure, print the install hint and exit 0.

    Fail-soft is the contract: a missing dependency must NEVER crash a caller.
    It prints the one-line fix, points back to grep, and exits clean.
    """
    try:
        import sqlite_vec  # noqa: F401
        from fastembed import TextEmbedding  # noqa: F401
    except Exception as exc:  # ImportError or any load-time failure
        print(
            "recall: optional semantic-recall dependencies are not installed.\n"
            f"  cause : {type(exc).__name__}: {exc}\n"
            f"  fix   : {INSTALL_HINT}\n"
            "  note  : recall COMPLEMENTS grep; until installed, use grep for\n"
            "          exact-string search (always available, no deps).",
            file=sys.stderr,
        )
        sys.exit(0)  # fail-soft: clean exit, not a crash
    import sqlite_vec
    from fastembed import TextEmbedding
    return sqlite_vec, TextEmbedding


# --------------------------------------------------------------------------
# Embedding (cached singleton).
# --------------------------------------------------------------------------
_EMBEDDER = None


def _get_embedder(TextEmbedding):
    global _EMBEDDER
    if _EMBEDDER is None:
        MODEL_CACHE.mkdir(parents=True, exist_ok=True)
        _EMBEDDER = TextEmbedding(model_name=MODEL_NAME, cache_dir=str(MODEL_CACHE))
    return _EMBEDDER


def _embed(TextEmbedding, texts):
    """Return a list of float vectors for the given texts."""
    emb = _get_embedder(TextEmbedding)
    return [list(map(float, v)) for v in emb.embed(list(texts))]


def _pack(vec):
    """Pack a float vector as little-endian float32 bytes for sqlite-vec."""
    return struct.pack(f"<{len(vec)}f", *vec)


# --------------------------------------------------------------------------
# Manifest parsing — pull real local paths out of sources(.template).md.
# --------------------------------------------------------------------------
_PATH_LINE = re.compile(r"^\s*-\s*(?:path|source)\s*:\s*(.+?)\s*$", re.IGNORECASE)


def _parse_manifest_paths(manifest: Path):
    """Extract `- path: <...>` entries from a sources manifest.

    Placeholder/unresolved paths (template angle-brackets, non-existent files)
    are skipped silently — the manifest is allowed to carry seeds that don't
    resolve on a given machine.
    """
    out = []
    if not manifest.exists():
        return out
    for raw in manifest.read_text(encoding="utf-8", errors="replace").splitlines():
        m = _PATH_LINE.match(raw)
        if not m:
            continue
        val = m.group(1).strip()
        # Skip template placeholders like <ABSOLUTE local path, placeholder>.
        if val.startswith("<") or "placeholder" in val.lower() or not val:
            continue
        out.append(Path(os.path.expanduser(val)))
    return out


def _iter_text_files(roots):
    """Yield text files under each root (file or directory), de-duplicated."""
    seen = set()
    for root in roots:
        if not root.exists():
            continue
        if root.is_file():
            paths = [root]
        else:
            paths = sorted(root.rglob("*"))
        for p in paths:
            if not p.is_file():
                continue
            if p.suffix.lower() not in TEXT_EXTS:
                continue
            rp = p.resolve()
            if rp in seen:
                continue
            seen.add(rp)
            yield p


# --------------------------------------------------------------------------
# Chunking — character window with overlap, tracking the start line for
# citations (file:line).
# --------------------------------------------------------------------------
def _chunk_with_lines(text: str):
    """Yield (chunk_text, start_line) over `text`.

    start_line is 1-based, computed from the character offset so citations point
    at the line where the chunk begins.
    """
    if not text.strip():
        return
    # Precompute char-offset -> line number via newline positions.
    newline_pos = [i for i, ch in enumerate(text) if ch == "\n"]

    def line_of(offset: int) -> int:
        # number of newlines before offset, + 1 (1-based)
        lo, hi = 0, len(newline_pos)
        while lo < hi:
            mid = (lo + hi) // 2
            if newline_pos[mid] < offset:
                lo = mid + 1
            else:
                hi = mid
        return lo + 1

    step = max(1, CHUNK_CHARS - CHUNK_OVERLAP)
    n = len(text)
    pos = 0
    while pos < n:
        piece = text[pos:pos + CHUNK_CHARS]
        if piece.strip():
            yield piece.strip(), line_of(pos)
        pos += step


def _gather_chunks(roots):
    """Walk roots, chunk every text file, return list of (text, citation)."""
    chunks = []
    for f in _iter_text_files(roots):
        try:
            content = f.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        for chunk_text, start_line in _chunk_with_lines(content):
            citation = f"{f}:{start_line}"
            chunks.append((chunk_text, citation))
    return chunks


# --------------------------------------------------------------------------
# DB schema (sqlite-vec virtual table + a metadata table for text+citation).
# --------------------------------------------------------------------------
def _connect(sqlite_vec):
    con = sqlite3.connect(str(DB_PATH))
    con.enable_load_extension(True)
    sqlite_vec.load(con)
    con.enable_load_extension(False)
    return con


def _init_schema(con):
    con.execute(
        f"CREATE VIRTUAL TABLE IF NOT EXISTS vec_chunks "
        f"USING vec0(embedding float[{EMBED_DIM}])"
    )
    con.execute(
        "CREATE TABLE IF NOT EXISTS chunk_meta ("
        "  rowid INTEGER PRIMARY KEY,"
        "  text TEXT NOT NULL,"
        "  citation TEXT NOT NULL"
        ")"
    )
    con.commit()


# --------------------------------------------------------------------------
# Subcommand: index
# --------------------------------------------------------------------------
def cmd_index(args):
    sqlite_vec, TextEmbedding = _load_deps()

    # Resolve sources: manifest paths + always-on throughline loop.
    manifest = SOURCES_LIVE if SOURCES_LIVE.exists() else SOURCES_TEMPLATE
    manifest_paths = _parse_manifest_paths(manifest)
    loop_paths = [NEXT_DIR, LEDGER_DIR]
    roots = manifest_paths + loop_paths

    print(f"recall index: manifest = {manifest}")
    print(f"recall index: {len(manifest_paths)} resolvable manifest path(s) + "
          f"throughline loop ({NEXT_DIR.name}/, {LEDGER_DIR.name}/)")

    chunks = _gather_chunks(roots)
    if not chunks:
        print("recall index: no text content found to index. "
              "Point identity/sources.md at real corpus paths (see "
              "identity/sources.template.md) and re-run.", file=sys.stderr)
        sys.exit(0)

    print(f"recall index: {len(chunks)} chunk(s); embedding with {MODEL_NAME} "
          "(first run downloads the model, ~130 MB)...")

    IDENTITY_DIR.mkdir(parents=True, exist_ok=True)
    # Rebuild from scratch for a clean, reproducible index.
    if DB_PATH.exists():
        DB_PATH.unlink()

    con = _connect(sqlite_vec)
    _init_schema(con)

    texts = [c[0] for c in chunks]
    vectors = _embed(TextEmbedding, texts)

    for i, ((text, citation), vec) in enumerate(zip(chunks, vectors), start=1):
        con.execute(
            "INSERT INTO vec_chunks(rowid, embedding) VALUES (?, ?)",
            (i, _pack(vec)),
        )
        con.execute(
            "INSERT INTO chunk_meta(rowid, text, citation) VALUES (?, ?, ?)",
            (i, text, citation),
        )
    con.commit()
    con.close()

    print(f"recall index: wrote {len(chunks)} vectors -> {DB_PATH}")
    print("recall index: done. Query with:  "
          'python3 recall/recall.py query "<your text>" --k 5')


# --------------------------------------------------------------------------
# Subcommand: query
# --------------------------------------------------------------------------
def cmd_query(args):
    sqlite_vec, TextEmbedding = _load_deps()

    if not DB_PATH.exists():
        print("recall query: no index found at "
              f"{DB_PATH}. Build it first:  python3 recall/recall.py index\n"
              "  (or use grep for exact-string search in the meantime).",
              file=sys.stderr)
        sys.exit(0)

    qvec = _embed(TextEmbedding, [args.text])[0]

    con = _connect(sqlite_vec)
    rows = con.execute(
        "SELECT v.rowid, v.distance, m.text, m.citation "
        "FROM vec_chunks v "
        "JOIN chunk_meta m ON m.rowid = v.rowid "
        "WHERE v.embedding MATCH ? AND k = ? "
        "ORDER BY v.distance",
        (_pack(qvec), args.k),
    ).fetchall()
    con.close()

    if not rows:
        print("recall query: no hits. (Try grep for exact-string search.)")
        return

    print(f'recall query: "{args.text}"  (top {len(rows)})\n')
    for rank, (_rowid, distance, text, citation) in enumerate(rows, start=1):
        # sqlite-vec returns L2 distance by default; convert to a 0..1-ish
        # similarity for readability (lower distance = higher similarity).
        similarity = 1.0 / (1.0 + float(distance))
        snippet = " ".join(text.split())
        if len(snippet) > 320:
            snippet = snippet[:317] + "..."
        print(f"[{rank}] sim={similarity:.3f}  {citation}")
        print(f"    {snippet}\n")


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------
def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="recall",
        description="Optional local semantic recall over the Portrait corpus "
                    "(complements grep; never replaces it).",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_index = sub.add_parser("index", help="build/refresh the vector index")
    p_index.set_defaults(func=cmd_index)

    p_query = sub.add_parser("query", help="semantic top-k over the index")
    p_query.add_argument("text", help="natural-language query text")
    p_query.add_argument("--k", type=int, default=5, help="number of hits (default 5)")
    p_query.set_defaults(func=cmd_query)

    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
