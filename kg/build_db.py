#!/usr/bin/env python3
"""
Build SQLite + FTS5 database from biophoton_kg.jsonl.

Creates:
  biophoton_kg.db  - SQLite database with:
    entities       - main entity table (id, type, title, data JSON)
    entities_fts   - FTS5 full-text index on title + searchable text
    entity_tracks  - track associations
    entity_concepts - concept associations (reverse index)
"""

import json
import sqlite3
import sys
from pathlib import Path

KG_DIR = Path(__file__).resolve().parent
JSONL = KG_DIR / "biophoton_kg.jsonl"
DB = KG_DIR / "biophoton_kg.db"


def searchable_text(entity: dict) -> str:
    """Extract all searchable text from an entity."""
    parts = [entity.get("title", "")]

    etype = entity["type"]
    if etype == "paper":
        parts.extend([
            entity.get("annotation", ""),
            entity.get("first_author", ""),
            entity.get("journal", ""),
            entity.get("category", ""),
            entity.get("rating", ""),
        ])
    elif etype == "prediction":
        parts.extend([
            entity.get("section_title", ""),
            entity.get("expected_value", ""),
            entity.get("required_setup", ""),
            entity.get("falsification", ""),
        ])
    elif etype == "experiment":
        parts.extend([
            entity.get("tier", ""),
            entity.get("tier_description", ""),
            entity.get("predictions_tested", ""),
            entity.get("equipment", ""),
            entity.get("estimated_cost", ""),
        ])
    elif etype == "finding":
        parts.extend([
            entity.get("what", ""),
            entity.get("numbers", ""),
            entity.get("why_it_matters", ""),
            entity.get("tag", ""),
        ])
    elif etype == "track":
        parts.extend([
            entity.get("agent_role", ""),
            entity.get("mission", ""),
            entity.get("track_sections", ""),
        ])
    elif etype == "textbook":
        parts.extend([
            entity.get("annotation", ""),
            entity.get("category", ""),
        ])
    elif etype == "research_group":
        parts.extend([
            entity.get("description", ""),
            " ".join(entity.get("key_papers", [])),
        ])
    elif etype == "cross_check":
        parts.extend([
            entity.get("status", ""),
            entity.get("severity", ""),
            entity.get("resolution", ""),
        ])
    elif etype == "concept":
        parts.append(f"Referenced by {entity.get('ref_count', 0)} entities")

    # Add concepts as searchable text
    parts.extend(entity.get("concepts", []))

    return " ".join(p for p in parts if p)


def build():
    if not JSONL.exists():
        print(f"ERROR: {JSONL} not found. Run ingest.py first.", file=sys.stderr)
        return 1

    # Load entities
    entities = []
    with open(JSONL) as f:
        for line in f:
            line = line.strip()
            if line:
                entities.append(json.loads(line))

    print(f"Loaded {len(entities)} entities from {JSONL}")

    # Remove old DB
    if DB.exists():
        DB.unlink()

    conn = sqlite3.connect(str(DB))
    c = conn.cursor()

    # Create tables
    c.execute("""
        CREATE TABLE entities (
            id TEXT PRIMARY KEY,
            type TEXT NOT NULL,
            title TEXT NOT NULL,
            data TEXT NOT NULL
        )
    """)

    c.execute("""
        CREATE VIRTUAL TABLE entities_fts USING fts5(
            entity_id,
            title,
            body,
            tokenize='porter unicode61'
        )
    """)

    c.execute("""
        CREATE TABLE entity_tracks (
            entity_id TEXT NOT NULL,
            track TEXT NOT NULL,
            FOREIGN KEY (entity_id) REFERENCES entities(id)
        )
    """)

    c.execute("""
        CREATE TABLE entity_concepts (
            entity_id TEXT NOT NULL,
            concept TEXT NOT NULL,
            FOREIGN KEY (entity_id) REFERENCES entities(id)
        )
    """)

    # Create indices
    c.execute("CREATE INDEX idx_entities_type ON entities(type)")
    c.execute("CREATE INDEX idx_tracks_track ON entity_tracks(track)")
    c.execute("CREATE INDEX idx_tracks_entity ON entity_tracks(entity_id)")
    c.execute("CREATE INDEX idx_concepts_concept ON entity_concepts(concept)")
    c.execute("CREATE INDEX idx_concepts_entity ON entity_concepts(entity_id)")

    # Insert entities
    for e in entities:
        data_json = json.dumps(e, ensure_ascii=False)
        body = searchable_text(e)

        c.execute(
            "INSERT INTO entities (id, type, title, data) VALUES (?, ?, ?, ?)",
            (e["id"], e["type"], e["title"], data_json)
        )

        c.execute(
            "INSERT INTO entities_fts (entity_id, title, body) VALUES (?, ?, ?)",
            (e["id"], e["title"], body)
        )

        # Track associations
        for track in e.get("tracks", []):
            c.execute(
                "INSERT INTO entity_tracks (entity_id, track) VALUES (?, ?)",
                (e["id"], track)
            )

        # Concept associations
        for concept in e.get("concepts", []):
            c.execute(
                "INSERT INTO entity_concepts (entity_id, concept) VALUES (?, ?)",
                (e["id"], concept)
            )

    conn.commit()

    # Print stats
    c.execute("SELECT type, COUNT(*) FROM entities GROUP BY type ORDER BY type")
    print("\nEntity counts:")
    for row in c.fetchall():
        print(f"  {row[0]}: {row[1]}")

    c.execute("SELECT COUNT(DISTINCT track) FROM entity_tracks")
    print(f"\nDistinct tracks: {c.fetchone()[0]}")

    c.execute("SELECT COUNT(DISTINCT concept) FROM entity_concepts")
    print(f"Distinct concepts: {c.fetchone()[0]}")

    c.execute("SELECT COUNT(*) FROM entity_tracks")
    print(f"Track associations: {c.fetchone()[0]}")

    c.execute("SELECT COUNT(*) FROM entity_concepts")
    print(f"Concept associations: {c.fetchone()[0]}")

    conn.close()
    print(f"\nDatabase: {DB} ({DB.stat().st_size / 1024:.0f} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(build())
