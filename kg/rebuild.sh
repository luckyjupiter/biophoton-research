#!/bin/bash
# Rebuild biophoton knowledge graph from markdown sources
set -e
cd "$(dirname "$0")"
echo "=== Ingesting markdown sources ==="
python3 ingest.py
echo ""
echo "=== Building SQLite + FTS5 database ==="
python3 build_db.py
echo ""
echo "=== Quick verification ==="
python3 search.py --stats
