#!/usr/bin/env python3
"""
Biophoton Research Knowledge Graph MCP Server.

Zero-dependency stdio JSON-RPC server following the QTrainerAI pattern.

7 tools:
  search_biophoton_kg  - BM25 full-text search with type/track filters
  get_entity           - Full entity by ID
  search_predictions   - Filter predictions by track/tier/section
  search_papers        - Filter papers by rating/category/track
  search_by_concept    - Concept reverse index lookup
  get_related          - Entities sharing concepts with a given entity
  biophoton_kg_stats   - Corpus statistics

Run: python3 biophoton_mcp_server.py  (reads stdin, writes stdout)
"""

import json
import sqlite3
import sys
from pathlib import Path

KG_DIR = Path(__file__).resolve().parent
DB_PATH = KG_DIR / "biophoton_kg.db"

# ── database helpers ─────────────────────────────────────────────────────────

_conn = None
_db_mtime = 0


def _get_conn():
    """Get SQLite connection, auto-reloading if DB file changed."""
    global _conn, _db_mtime
    import os
    if not DB_PATH.exists():
        return None
    mtime = os.path.getmtime(DB_PATH)
    if _conn is not None and mtime == _db_mtime:
        return _conn
    if _conn is not None:
        _conn.close()
    _conn = sqlite3.connect(str(DB_PATH))
    _conn.row_factory = sqlite3.Row
    _db_mtime = mtime
    return _conn


# ── tool implementations ─────────────────────────────────────────────────────

def _search_biophoton_kg(args: dict) -> str:
    query = args.get("query", "")
    entity_type = args.get("type", "")
    track = args.get("track", "")
    limit = min(args.get("limit", 20), 50)

    conn = _get_conn()
    if not conn:
        return "ERROR: Database not found. Run build_db.py."

    c = conn.cursor()

    if query:
        sql = """
            SELECT e.id, e.type, e.title, rank as score
            FROM entities_fts fts
            JOIN entities e ON e.id = fts.entity_id
            WHERE entities_fts MATCH ?
        """
        params = [query]
    else:
        sql = "SELECT e.id, e.type, e.title, 0 as score FROM entities e WHERE 1=1"
        params = []

    if entity_type:
        sql += " AND e.type = ?"
        params.append(entity_type)

    if track:
        sql += " AND e.id IN (SELECT entity_id FROM entity_tracks WHERE track = ?)"
        params.append(track.zfill(2))

    sql += (" ORDER BY rank" if query else " ORDER BY e.id") + " LIMIT ?"
    params.append(limit)

    c.execute(sql, params)
    results = []
    for r in c.fetchall():
        results.append({
            "id": r["id"],
            "type": r["type"],
            "title": r["title"][:150],
            "score": round(r["score"], 3) if r["score"] else 0,
        })

    return json.dumps({"count": len(results), "results": results}, indent=2)


def _get_entity(args: dict) -> str:
    entity_id = args.get("id", "")
    if not entity_id:
        return "ERROR: 'id' parameter required."

    conn = _get_conn()
    if not conn:
        return "ERROR: Database not found."

    c = conn.cursor()
    c.execute("SELECT data FROM entities WHERE id = ?", (entity_id,))
    row = c.fetchone()
    if not row:
        return f"Entity not found: {entity_id}"
    return row["data"]


def _search_predictions(args: dict) -> str:
    track = args.get("track", "")
    section = args.get("section", "")
    query = args.get("query", "")
    limit = min(args.get("limit", 30), 50)

    conn = _get_conn()
    if not conn:
        return "ERROR: Database not found."

    c = conn.cursor()

    sql = "SELECT e.id, e.type, e.title, e.data FROM entities e WHERE e.type = 'prediction'"
    params = []

    if track:
        sql += " AND e.id IN (SELECT entity_id FROM entity_tracks WHERE track = ?)"
        params.append(track.zfill(2))

    if section:
        sql += " AND json_extract(e.data, '$.section') LIKE ?"
        params.append(f"{section}%")

    sql += " ORDER BY e.id LIMIT ?"
    params.append(limit)

    c.execute(sql, params)
    results = []
    for r in c.fetchall():
        data = json.loads(r["data"])
        entry = {
            "id": data["id"],
            "section": data.get("section", ""),
            "title": data["title"][:150],
            "track": data.get("track", ""),
            "expected_value": data.get("expected_value", "")[:100],
        }
        results.append(entry)

    # If query provided, filter in Python
    if query:
        ql = query.lower()
        results = [r for r in results if ql in json.dumps(r).lower()]

    return json.dumps({"count": len(results), "results": results}, indent=2)


def _search_papers(args: dict) -> str:
    rating = args.get("rating", "")
    category = args.get("category", "")
    track = args.get("track", "")
    query = args.get("query", "")
    limit = min(args.get("limit", 30), 50)

    conn = _get_conn()
    if not conn:
        return "ERROR: Database not found."

    c = conn.cursor()

    sql = "SELECT e.id, e.data FROM entities e WHERE e.type = 'paper'"
    params = []

    if rating:
        sql += " AND json_extract(e.data, '$.rating') = ?"
        params.append(rating)

    if category:
        sql += " AND json_extract(e.data, '$.category') LIKE ?"
        params.append(f"%{category}%")

    if track:
        sql += " AND e.id IN (SELECT entity_id FROM entity_tracks WHERE track = ?)"
        params.append(track.zfill(2))

    sql += " ORDER BY e.id LIMIT ?"
    params.append(limit)

    c.execute(sql, params)
    results = []
    for r in c.fetchall():
        data = json.loads(r["data"])
        entry = {
            "id": data["id"],
            "first_author": data.get("first_author", ""),
            "year": data.get("year", ""),
            "rating": data.get("rating", ""),
            "category": data.get("category", ""),
            "tracks": data.get("tracks", []),
            "title": data["title"][:120],
        }
        results.append(entry)

    if query:
        ql = query.lower()
        results = [r for r in results if ql in json.dumps(r).lower()]

    return json.dumps({"count": len(results), "results": results}, indent=2)


def _search_by_concept(args: dict) -> str:
    concept = args.get("concept", "")
    if not concept:
        return "ERROR: 'concept' parameter required."

    limit = min(args.get("limit", 20), 50)

    conn = _get_conn()
    if not conn:
        return "ERROR: Database not found."

    c = conn.cursor()
    c.execute("""
        SELECT e.id, e.type, e.title
        FROM entity_concepts ec
        JOIN entities e ON e.id = ec.entity_id
        WHERE ec.concept LIKE ?
        ORDER BY e.type, e.id
        LIMIT ?
    """, (f"%{concept.lower()}%", limit))

    results = [{"id": r["id"], "type": r["type"], "title": r["title"][:150]}
               for r in c.fetchall()]

    return json.dumps({"count": len(results), "concept": concept, "results": results}, indent=2)


_STOP_WORDS = frozenset({
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


def _extract_terms(text: str, max_terms: int = 25) -> list[str]:
    """Extract key terms from text for BM25 query."""
    import re
    words = re.findall(r'[a-zA-Z]{3,}', text.lower())
    seen = set()
    terms = []
    for w in words:
        if w not in _STOP_WORDS and w not in seen:
            seen.add(w)
            terms.append(w)
    return terms[:max_terms]


def _get_related(args: dict) -> str:
    """Find related entities using BM25 text similarity (automatic linking)."""
    entity_id = args.get("id", "")
    if not entity_id:
        return "ERROR: 'id' parameter required."

    limit = min(args.get("limit", 15), 30)

    conn = _get_conn()
    if not conn:
        return "ERROR: Database not found."

    c = conn.cursor()

    # Get entity's FTS text
    c.execute("SELECT title, body FROM entities_fts WHERE entity_id = ?",
              (entity_id,))
    row = c.fetchone()
    if not row:
        return json.dumps({"entity_id": entity_id, "count": 0, "results": [],
                           "method": "bm25"})

    title = row["title"] or ""
    body = row["body"] or ""

    # Weight title 2x, extract key terms
    terms = _extract_terms(f"{title} {title} {body}")
    if not terms:
        return json.dumps({"entity_id": entity_id, "count": 0, "results": [],
                           "method": "bm25"})

    fts_query = " OR ".join(terms)

    c.execute("""
        SELECT e.id, e.type, e.title, rank as score
        FROM entities_fts fts
        JOIN entities e ON e.id = fts.entity_id
        WHERE entities_fts MATCH ?
          AND fts.entity_id != ?
        ORDER BY rank
        LIMIT ?
    """, (fts_query, entity_id, limit))

    results = [{
        "id": r["id"],
        "type": r["type"],
        "title": r["title"][:150],
        "bm25_score": round(r["score"], 3),
    } for r in c.fetchall()]

    return json.dumps({
        "entity_id": entity_id,
        "query_terms": terms[:10],
        "method": "bm25",
        "count": len(results),
        "results": results,
    }, indent=2)


def _biophoton_kg_stats(_args: dict) -> str:
    conn = _get_conn()
    if not conn:
        return "ERROR: Database not found."

    c = conn.cursor()
    stats = {}

    c.execute("SELECT COUNT(*) as n FROM entities")
    stats["total_entities"] = c.fetchone()["n"]

    c.execute("SELECT type, COUNT(*) as n FROM entities GROUP BY type ORDER BY type")
    stats["by_type"] = {r["type"]: r["n"] for r in c.fetchall()}

    c.execute("""
        SELECT et.track, COUNT(DISTINCT et.entity_id) as n
        FROM entity_tracks et GROUP BY et.track ORDER BY et.track
    """)
    stats["by_track"] = {r["track"]: r["n"] for r in c.fetchall()}

    c.execute("SELECT COUNT(DISTINCT concept) as n FROM entity_concepts")
    stats["distinct_concepts"] = c.fetchone()["n"]

    c.execute("""
        SELECT concept, COUNT(*) as n FROM entity_concepts
        GROUP BY concept ORDER BY n DESC LIMIT 15
    """)
    stats["top_concepts"] = {r["concept"]: r["n"] for r in c.fetchall()}

    # Paper ratings distribution
    c.execute("""
        SELECT json_extract(data, '$.rating') as rating, COUNT(*) as n
        FROM entities WHERE type = 'paper'
        GROUP BY rating ORDER BY n DESC
    """)
    stats["paper_ratings"] = {r["rating"]: r["n"] for r in c.fetchall()}

    # Cross-check status
    c.execute("""
        SELECT json_extract(data, '$.status') as status, COUNT(*) as n
        FROM entities WHERE type = 'cross_check'
        GROUP BY status
    """)
    stats["cross_check_status"] = {r["status"]: r["n"] for r in c.fetchall()}

    return json.dumps(stats, indent=2)


# ── MCP protocol ─────────────────────────────────────────────────────────────

TOOLS = [
    {
        "name": "search_biophoton_kg",
        "description": "BM25 full-text search across all biophoton research entities (papers, predictions, experiments, findings, tracks, groups, cross-checks, concepts). Returns ranked results.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query (BM25 full-text)"},
                "type": {"type": "string", "description": "Filter by entity type: paper, prediction, experiment, finding, track, research_group, cross_check, concept"},
                "track": {"type": "string", "description": "Filter by track number (01-08)"},
                "limit": {"type": "integer", "description": "Max results (default 20, max 50)"},
            },
        },
    },
    {
        "name": "get_entity",
        "description": "Get full entity data by ID. Entity IDs follow patterns like paper-1.1, pred-4.1, exp-1, finding-2026-02-11-simulator, track-01, group-zangari, cross-c1, concept-arrow.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "id": {"type": "string", "description": "Entity ID"},
            },
            "required": ["id"],
        },
    },
    {
        "name": "search_predictions",
        "description": "Search predictions with filters. 56 falsifiable predictions across 8 sections covering photocount statistics, quantum optics, detection, demyelination, unified model, waveguide simulator, MMI, and nanoantenna relay.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "track": {"type": "string", "description": "Filter by track (01-08)"},
                "section": {"type": "string", "description": "Filter by section prefix (e.g., '4' for all section 4.x)"},
                "query": {"type": "string", "description": "Text filter"},
                "limit": {"type": "integer", "description": "Max results (default 30)"},
            },
        },
    },
    {
        "name": "search_papers",
        "description": "Search the annotated bibliography. 43 papers with ratings (Essential/Important/Supplementary), categories, track associations, and annotations.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "rating": {"type": "string", "description": "Filter: Essential, Important, or Supplementary"},
                "category": {"type": "string", "description": "Filter by category (Foundational, Neural Hypothesis, Waveguide Theory, Quantum Models, Statistical Methods, Reviews)"},
                "track": {"type": "string", "description": "Filter by track (01-08)"},
                "query": {"type": "string", "description": "Text filter"},
                "limit": {"type": "integer", "description": "Max results (default 30)"},
            },
        },
    },
    {
        "name": "search_by_concept",
        "description": "Find entities by concept keyword. Concepts include: biophoton, myelin, waveguide, ARROW, demyelination, ROS, nanoantenna, relay, spectral filter, cuprizone, EAE, MMI, cavity QED, entanglement, etc.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "concept": {"type": "string", "description": "Concept keyword to search"},
                "limit": {"type": "integer", "description": "Max results (default 20)"},
            },
            "required": ["concept"],
        },
    },
    {
        "name": "get_related",
        "description": "Find entities related to a given entity using automatic BM25 text similarity. Extracts key terms from the entity's content and finds the most textually similar entities — no pre-computed links needed.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "id": {"type": "string", "description": "Entity ID to find related entities for"},
                "limit": {"type": "integer", "description": "Max results (default 15)"},
            },
            "required": ["id"],
        },
    },
    {
        "name": "biophoton_kg_stats",
        "description": "Get corpus statistics: entity counts by type and track, concept distribution, paper ratings, cross-check status.",
        "inputSchema": {
            "type": "object",
            "properties": {},
        },
    },
]

TOOL_HANDLERS = {
    "search_biophoton_kg": _search_biophoton_kg,
    "get_entity": _get_entity,
    "search_predictions": _search_predictions,
    "search_papers": _search_papers,
    "search_by_concept": _search_by_concept,
    "get_related": _get_related,
    "biophoton_kg_stats": _biophoton_kg_stats,
}


def handle_request(req: dict) -> dict | None:
    """Handle a single JSON-RPC request."""
    req_id = req.get("id")
    method = req.get("method", "")

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "serverInfo": {
                    "name": "biophoton-kg",
                    "version": "1.0.0",
                },
                "capabilities": {
                    "tools": {},
                },
            },
        }

    if method == "notifications/initialized":
        return None

    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {"tools": TOOLS},
        }

    if method == "tools/call":
        params = req.get("params", {})
        tool_name = params.get("name", "")
        tool_args = params.get("arguments", {})

        handler = TOOL_HANDLERS.get(tool_name)
        if not handler:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32601, "message": f"Unknown tool: {tool_name}"},
            }

        try:
            result_text = handler(tool_args)
        except Exception as e:
            result_text = f"ERROR: {e}"

        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "content": [{"type": "text", "text": result_text}],
            },
        }

    # Unknown method
    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "error": {"code": -32601, "message": f"Unknown method: {method}"},
    }


def main():
    """stdio JSON-RPC main loop."""
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except json.JSONDecodeError:
            continue

        resp = handle_request(req)
        if resp:
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
