#!/usr/bin/env python3
"""
CLI search tool for the biophoton research knowledge graph.

Usage:
  python3 search.py "demyelination"                  # Full-text search
  python3 search.py --type prediction "cuprizone"    # Filter by type
  python3 search.py --type prediction --track 06     # Filter by track
  python3 search.py --concept arrow                  # Concept reverse index
  python3 search.py --related pred-4.1               # BM25 auto-linked entities
  python3 search.py --related-concepts pred-4.1      # Concept-based related
  python3 search.py --get paper-1.1                  # Get entity by ID
  python3 search.py --stats                          # Corpus statistics
"""

import argparse
import json
import re
import sqlite3
import sys
import textwrap
from pathlib import Path

DB = Path(__file__).resolve().parent / "biophoton_kg.db"

STOP_WORDS = frozenset({
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "is", "are", "was", "were", "be", "been",
    "being", "have", "has", "had", "do", "does", "did", "will", "would",
    "could", "should", "may", "might", "can", "that", "this", "these",
    "those", "it", "its", "not", "no", "if", "than", "as", "so", "also",
    "very", "all", "each", "both", "such", "more", "most", "other", "some",
    "any", "only", "same", "about", "into", "through", "during", "before",
    "after", "above", "below", "between", "under", "over", "then", "once",
    "here", "there", "when", "where", "how", "what", "which", "who", "whom",
    "why", "out", "off", "up", "down", "just", "now", "new", "use", "used",
    "using", "based", "per", "via", "see", "two", "one",
})


def get_conn():
    if not DB.exists():
        print(f"ERROR: {DB} not found. Run build_db.py first.", file=sys.stderr)
        sys.exit(1)
    conn = sqlite3.connect(str(DB))
    conn.row_factory = sqlite3.Row
    return conn


def search_fts(query: str, entity_type: str = "", track: str = "", limit: int = 20):
    """BM25 full-text search with optional type/track filters."""
    conn = get_conn()
    c = conn.cursor()

    # Build FTS query
    if query:
        sql = """
            SELECT e.id, e.type, e.title, e.data,
                   rank as score
            FROM entities_fts fts
            JOIN entities e ON e.id = fts.entity_id
            WHERE entities_fts MATCH ?
        """
        params: list = [query]
    else:
        sql = "SELECT e.id, e.type, e.title, e.data, 0 as score FROM entities e WHERE 1=1"
        params: list = []

    if entity_type:
        sql += " AND e.type = ?"
        params.append(entity_type)

    if track:
        track = track.zfill(2)
        sql += " AND e.id IN (SELECT entity_id FROM entity_tracks WHERE track = ?)"
        params.append(track)

    if query:
        sql += " ORDER BY rank"
    else:
        sql += " ORDER BY e.id"

    sql += " LIMIT ?"
    params.append(limit)

    c.execute(sql, params)
    results = c.fetchall()
    conn.close()
    return results


def get_entity(entity_id: str):
    """Get full entity by ID."""
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT data FROM entities WHERE id = ?", (entity_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return json.loads(row["data"])
    return None


def search_by_concept(concept: str, limit: int = 20):
    """Find entities sharing a concept."""
    conn = get_conn()
    c = conn.cursor()
    concept_lower = concept.lower()
    c.execute("""
        SELECT e.id, e.type, e.title, e.data, 0 as score
        FROM entity_concepts ec
        JOIN entities e ON e.id = ec.entity_id
        WHERE ec.concept LIKE ?
        ORDER BY e.type, e.id
        LIMIT ?
    """, (f"%{concept_lower}%", limit))
    results = c.fetchall()
    conn.close()
    return results


def get_related(entity_id: str, limit: int = 20):
    """Find entities sharing concepts with a given entity."""
    conn = get_conn()
    c = conn.cursor()

    # Get the entity's concepts
    c.execute("SELECT concept FROM entity_concepts WHERE entity_id = ?", (entity_id,))
    concepts = [r["concept"] for r in c.fetchall()]
    if not concepts:
        conn.close()
        return []

    placeholders = ",".join(["?"] * len(concepts))
    c.execute(f"""
        SELECT e.id, e.type, e.title, e.data,
               COUNT(ec.concept) as score
        FROM entity_concepts ec
        JOIN entities e ON e.id = ec.entity_id
        WHERE ec.concept IN ({placeholders})
          AND ec.entity_id != ?
        GROUP BY e.id
        ORDER BY score DESC
        LIMIT ?
    """, concepts + [entity_id, limit])
    results = c.fetchall()
    conn.close()
    return results


def _extract_query_terms(text: str, max_terms: int = 25) -> list[str]:
    """Extract key terms from text for BM25 query, removing stop words."""
    words = re.findall(r'[a-zA-Z]{3,}', text.lower())
    seen = set()
    terms = []
    for w in words:
        if w not in STOP_WORDS and w not in seen:
            seen.add(w)
            terms.append(w)
    return terms[:max_terms]


def get_related_bm25(entity_id: str, limit: int = 15):
    """Find related entities using BM25 text similarity at runtime.

    Takes the entity's title + body text, extracts key terms,
    and runs them as an OR query against FTS5. No pre-computed
    links needed — purely automatic.
    """
    conn = get_conn()
    c = conn.cursor()

    # Get entity's FTS text
    c.execute("SELECT title, body FROM entities_fts WHERE entity_id = ?",
              (entity_id,))
    row = c.fetchone()
    if not row:
        conn.close()
        return []

    title = row["title"] or ""
    body = row["body"] or ""

    # Weight title 2x by repeating it
    text = f"{title} {title} {body}"
    terms = _extract_query_terms(text)

    if not terms:
        conn.close()
        return []

    # FTS5 OR query for similarity
    fts_query = " OR ".join(terms)

    c.execute("""
        SELECT e.id, e.type, e.title, e.data, rank as score
        FROM entities_fts fts
        JOIN entities e ON e.id = fts.entity_id
        WHERE entities_fts MATCH ?
          AND fts.entity_id != ?
        ORDER BY rank
        LIMIT ?
    """, (fts_query, entity_id, limit))

    results = c.fetchall()
    conn.close()
    return results


def get_stats():
    """Corpus statistics."""
    conn = get_conn()
    c = conn.cursor()

    stats = {}

    c.execute("SELECT COUNT(*) FROM entities")
    stats["total_entities"] = c.fetchone()[0]

    c.execute("SELECT type, COUNT(*) as cnt FROM entities GROUP BY type ORDER BY type")
    stats["by_type"] = {r["type"]: r["cnt"] for r in c.fetchall()}

    c.execute("""
        SELECT et.track, COUNT(DISTINCT et.entity_id) as cnt
        FROM entity_tracks et
        GROUP BY et.track
        ORDER BY et.track
    """)
    stats["by_track"] = {r["track"]: r["cnt"] for r in c.fetchall()}

    c.execute("SELECT COUNT(DISTINCT concept) FROM entity_concepts")
    stats["distinct_concepts"] = c.fetchone()[0]

    c.execute("""
        SELECT concept, COUNT(*) as cnt
        FROM entity_concepts
        GROUP BY concept
        ORDER BY cnt DESC
        LIMIT 15
    """)
    stats["top_concepts"] = {r["concept"]: r["cnt"] for r in c.fetchall()}

    conn.close()
    return stats


# ── display helpers ──────────────────────────────────────────────────────────

def fmt_entity_short(row):
    """Format an entity for short display."""
    etype = row["type"]
    eid = row["id"]
    title = row["title"]

    # Truncate long titles
    if len(title) > 100:
        title = title[:97] + "..."

    score = row["score"] if "score" in row.keys() else ""
    score_str = f" (score: {score:.2f})" if score and score != 0 else ""

    return f"  [{etype:15s}] {eid:30s} {title}{score_str}"


def fmt_entity_full(entity: dict):
    """Format full entity display."""
    lines = []
    etype = entity["type"]
    lines.append(f"ID: {entity['id']}")
    lines.append(f"Type: {etype}")
    lines.append(f"Title: {entity['title']}")

    if etype == "paper":
        lines.append(f"Author: {entity.get('first_author', '')}")
        lines.append(f"Year: {entity.get('year', '')}")
        lines.append(f"Journal: {entity.get('journal', '')}")
        lines.append(f"Rating: {entity.get('rating', '')}")
        lines.append(f"Category: {entity.get('category', '')}")
        lines.append(f"DOI: {entity.get('doi', '')}")
        if entity.get("annotation"):
            lines.append(f"\n{textwrap.fill(entity['annotation'], 80)}")

    elif etype == "prediction":
        lines.append(f"Section: {entity.get('section', '')}")
        lines.append(f"Track: {entity.get('track', '')}")
        lines.append(f"Expected: {entity.get('expected_value', '')}")
        lines.append(f"Setup: {entity.get('required_setup', '')}")
        lines.append(f"Falsification: {entity.get('falsification', '')}")

    elif etype == "experiment":
        lines.append(f"Rank: {entity.get('rank', '')}")
        lines.append(f"Tier: {entity.get('tier', '')} - {entity.get('tier_description', '')}")
        lines.append(f"Equipment: {entity.get('equipment', '')}")
        lines.append(f"Time: {entity.get('integration_time', '')}")
        lines.append(f"Cost: {entity.get('estimated_cost', '')}")

    elif etype == "finding":
        lines.append(f"Date: {entity.get('date', '')}")
        lines.append(f"Tag: {entity.get('tag', '')}")
        if entity.get("what"):
            lines.append(f"\nWhat: {entity['what']}")
        if entity.get("numbers"):
            lines.append(f"\nNumbers: {entity['numbers']}")
        if entity.get("why_it_matters"):
            lines.append(f"\nWhy: {entity['why_it_matters']}")

    elif etype == "cross_check":
        lines.append(f"Status: {entity.get('status', '')}")
        if entity.get("severity"):
            lines.append(f"Severity: {entity['severity']}")
        if entity.get("resolution"):
            lines.append(f"Resolution: {entity['resolution']}")

    elif etype == "concept":
        lines.append(f"Referenced by: {entity.get('ref_count', 0)} entities")
        refs = entity.get("entity_refs", [])
        if refs:
            lines.append("Entities: " + ", ".join(refs[:20]))
            if len(refs) > 20:
                lines.append(f"  ... and {len(refs) - 20} more")

    tracks = entity.get("tracks", [])
    if tracks:
        lines.append(f"Tracks: {', '.join(tracks)}")

    concepts = entity.get("concepts", [])
    if concepts:
        lines.append(f"Concepts: {', '.join(concepts[:15])}")

    return "\n".join(lines)


# ── main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Search biophoton research knowledge graph")
    parser.add_argument("query", nargs="*", help="Search query")
    parser.add_argument("--type", dest="entity_type", help="Filter by entity type")
    parser.add_argument("--track", help="Filter by track number (01-08)")
    parser.add_argument("--concept", help="Search by concept (reverse index)")
    parser.add_argument("--related", help="Find related entities via BM25 similarity (automatic)")
    parser.add_argument("--related-concepts", help="Find related entities via shared concepts (pre-computed)")
    parser.add_argument("--get", help="Get full entity by ID")
    parser.add_argument("--stats", action="store_true", help="Show corpus statistics")
    parser.add_argument("--limit", type=int, default=20, help="Max results (default 20)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()
    query = " ".join(args.query) if args.query else ""

    # Stats mode
    if args.stats:
        stats = get_stats()
        if args.json:
            print(json.dumps(stats, indent=2))
        else:
            print("=== Biophoton Research Knowledge Graph ===\n")
            print(f"Total entities: {stats['total_entities']}")
            print("\nBy type:")
            for t, n in stats["by_type"].items():
                print(f"  {t:20s} {n}")
            print("\nBy track:")
            for t, n in stats["by_track"].items():
                print(f"  Track {t}: {n} entities")
            print(f"\nDistinct concepts: {stats['distinct_concepts']}")
            print("\nTop concepts:")
            for c, n in stats["top_concepts"].items():
                print(f"  {c:30s} {n}")
        return

    # Get mode
    if args.get:
        entity = get_entity(args.get)
        if entity:
            if args.json:
                print(json.dumps(entity, indent=2))
            else:
                print(fmt_entity_full(entity))
        else:
            print(f"Entity not found: {args.get}", file=sys.stderr)
            sys.exit(1)
        return

    # Related mode (BM25 automatic linking)
    if args.related:
        results = get_related_bm25(args.related, args.limit)
        if args.json:
            print(json.dumps([json.loads(r["data"]) for r in results], indent=2))
        else:
            print(f"=== Related to {args.related} (BM25 auto-link, {len(results)} results) ===\n")
            for r in results:
                print(fmt_entity_short(r))
        return

    # Related mode (concept-based, pre-computed)
    if args.related_concepts:
        results = get_related(args.related_concepts, args.limit)
        if args.json:
            print(json.dumps([json.loads(r["data"]) for r in results], indent=2))
        else:
            print(f"=== Related to {args.related_concepts} (shared concepts, {len(results)} results) ===\n")
            for r in results:
                print(fmt_entity_short(r))
        return

    # Concept mode
    if args.concept:
        results = search_by_concept(args.concept, args.limit)
        if args.json:
            print(json.dumps([json.loads(r["data"]) for r in results], indent=2))
        else:
            print(f"=== Concept: {args.concept} ({len(results)} results) ===\n")
            for r in results:
                print(fmt_entity_short(r))
        return

    # Full-text search mode
    if not query and not args.entity_type and not args.track:
        parser.print_help()
        return

    results = search_fts(query, args.entity_type or "", args.track or "", args.limit)

    if args.json:
        print(json.dumps([json.loads(r["data"]) for r in results], indent=2))
    else:
        label = f"'{query}'" if query else "all"
        filters = []
        if args.entity_type:
            filters.append(f"type={args.entity_type}")
        if args.track:
            filters.append(f"track={args.track}")
        filter_str = f" ({', '.join(filters)})" if filters else ""

        print(f"=== Search: {label}{filter_str} ({len(results)} results) ===\n")
        for r in results:
            print(fmt_entity_short(r))


if __name__ == "__main__":
    main()
