#!/usr/bin/env python3
"""Build a local SQLite full-text index of Markdown/text notes and search by words, phrases and path filters. No embeddings or network access."""

import argparse
import sqlite3
from pathlib import Path


def index(folder, db):
    folder = folder.resolve()
    if not folder.is_dir():
        raise ValueError("Notes folder does not exist")
    documents = []
    for path in sorted(folder.rglob("*")):
        relative = path.relative_to(folder)
        if any(part.startswith(".") for part in relative.parts) or path.is_symlink():
            continue
        if path.suffix.lower() not in (".md", ".txt", ".markdown") or not path.is_file():
            continue
        try:
            path.resolve().relative_to(folder)
        except ValueError:
            continue
        documents.append((str(relative), path.read_text(encoding="utf-8")))
    with sqlite3.connect(db) as conn:
        conn.execute("CREATE VIRTUAL TABLE IF NOT EXISTS notes USING fts5(path UNINDEXED, body)")
        conn.execute("DELETE FROM notes")
        conn.executemany("INSERT INTO notes(path, body) VALUES (?, ?)", documents)
    return len(documents)


def search(db, query, path_filter, limit):
    if not db.is_file():
        raise ValueError("Index does not exist; run index first")
    with sqlite3.connect(db.as_uri() + "?mode=ro", uri=True) as conn:
        return conn.execute("SELECT path, snippet(notes, 1, '[', ']', ' … ', 20) FROM notes WHERE notes MATCH ? AND instr(path, ?) > 0 ORDER BY rank LIMIT ?", (query, path_filter, limit)).fetchall()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="command", required=True)
    build = sub.add_parser("index")
    build.add_argument("folder", type=Path)
    build.add_argument("--db", type=Path, required=True)
    find = sub.add_parser("search")
    find.add_argument("query")
    find.add_argument("--db", type=Path, required=True)
    find.add_argument("--path", default="", help="Literal case-sensitive path substring")
    find.add_argument("--limit", type=int, default=10)
    a = p.parse_args()
    try:
        if a.command == "index":
            print(f"Indexed {index(a.folder, a.db)} documents")
        else:
            if a.limit < 1 or a.limit > 100:
                raise ValueError("limit must be between 1 and 100")
            for path, excerpt in search(a.db.resolve(), a.query, a.path, a.limit):
                print(f"{path}\n  {excerpt}")
    except (OSError, UnicodeError, ValueError, sqlite3.Error) as exc:
        p.exit(2, f"Index/search error: {exc}\n")


if __name__ == "__main__":
    main()
