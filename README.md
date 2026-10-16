# local-notes-search

Build a local SQLite full-text index of Markdown/text notes and search by words, phrases and path filters. No embeddings or network access.

## Status

Initial prototype, created in October 2026. This is a small,
independent starter project, without claims of production deployment or adoption.

## Installation

Python 3.10+ is required. No third-party Python packages are needed.
Copy this directory, then run commands from inside it.

## Usage

```sh
python3 cli.py index examples/notes --db notes.db
python3 cli.py search "release" --db notes.db
```

Run `python3 cli.py --help` for options. Reports go to standard output unless an
output file is specified. Input errors return status 2.

## Limitations

Requires Python SQLite with FTS5. Indexing rebuilds the selected database table. The database contains note text; keep it local. Hidden paths and symlinks are excluded. No semantic retrieval, tags or incremental updates.

## Development and contributing

Keep changes narrowly scoped. Include a reproducible example for a bug report.
Use synthetic fixtures rather than personal, proprietary or research data.
Run the project checks from this directory:

```sh
python3 -m unittest discover -s tests -v
```

## License

MIT; see [LICENSE](LICENSE).
