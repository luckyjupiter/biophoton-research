#!/usr/bin/env python3
"""
Ingest biophoton research markdown sources into biophoton_kg.jsonl.

Entity types:
  paper, prediction, experiment, finding, track, research_group, cross_check, concept

Sources:
  docs/bibliography.md     -> paper
  docs/master-predictions.md -> prediction, experiment, cross_check
  FINDINGS_LOG.md          -> finding
  track-NN/ROLE.md         -> track
  Cross-references         -> research_group, concept (reverse index)
"""

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = Path(__file__).resolve().parent / "biophoton_kg.jsonl"

# ── helpers ──────────────────────────────────────────────────────────────────

def slug(text: str) -> str:
    """Make a URL-safe slug."""
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:80]


def extract_concepts(text: str) -> list[str]:
    """Pull domain concepts from free text via keyword matching.

    Short keywords (<=4 chars) use word-boundary matching to avoid
    false positives (e.g., "AD" in "broadband"). Longer terms use
    simple substring matching.
    """
    # Long keywords: safe for substring matching
    long_kw = [
        "biophoton", "myelin", "waveguide", "demyelination",
        "singlet oxygen", "photocount", "Poisson", "Fano", "coherence",
        "entanglement", "biphoton", "nanoantenna", "spectral filter",
        "cuprizone", "Bayesian", "node of Ranvier", "node-of-Ranvier",
        "detector", "g-ratio", "action potential", "axon", "myelinated axon",
        "cavity QED", "Purcell", "cooperativity", "squeezed",
        "sub-Poissonian", "thermal", "decoherence", "kappa",
        "refractive index", "transfer matrix", "backpropagation",
        "soliton", "Davydov", "fractal", "entropy", "recurrence",
        "Hurst", "biomarker", "blueshift", "redshift", "spectral shift",
        "species redshift", "aging blueshift", "Alzheimer",
        "photonic saltatory conduction", "dual-signature", "cranial window",
        "optic nerve", "corpus callosum", "mitochondria",
        "lipid peroxidation", "triplet carbonyl", "phosphene",
        "Schmidt-Lanterman", "wavelength-division multiplexing",
        "polarization", "mode overlap", "coupling efficiency",
        "channel capacity", "information theory", "Mandel Q",
        "chi-squared", "likelihood ratio", "sensitivity analysis",
        "Monte Carlo", "Gillespie", "relay",
    ]

    # Short keywords: need word-boundary matching (\b) to avoid
    # "AD" matching "broadband", "MS" matching "systems", etc.
    short_kw = [
        "UPE", "ARROW", "ROS", "EAE", "MS", "MMI", "QFT", "PMT",
        "SNSPD", "SPAD", "EMCCD", "DFA", "ROC", "AUC", "AD", "VaD",
        "Bell", "CHSH", "HBT", "BIC", "Franson",
    ]

    found = set()
    tl = text.lower()

    for k in long_kw:
        if k.lower() in tl:
            found.add(k.lower())

    for k in short_kw:
        # Word-boundary match (case-insensitive)
        if re.search(r"\b" + re.escape(k) + r"\b", text, re.IGNORECASE):
            found.add(k.lower())

    return sorted(found)


def extract_tracks(text: str) -> list[str]:
    """Extract track references like 'Track 01', 'Tracks 1, 2', etc."""
    tracks = set()
    for m in re.finditer(r"Tracks?\s+([\d,\s]+)", text, re.IGNORECASE):
        for t in re.findall(r"\d+", m.group(1)):
            tracks.add(t.zfill(2))
    for m in re.finditer(r"\|\s*(\d{2})\s*\|", text):
        tracks.add(m.group(1))
    return sorted(tracks)


# ── paper parser ─────────────────────────────────────────────────────────────

def parse_bibliography(path: Path) -> list[dict]:
    """Parse docs/bibliography.md into paper entities."""
    text = path.read_text()
    entities = []

    # Split on ### headings (individual paper entries)
    sections = re.split(r"^### ", text, flags=re.MULTILINE)

    for sec in sections[1:]:  # skip preamble
        lines = sec.strip().split("\n")
        if not lines:
            continue

        # First line is the citation line
        cite_line = lines[0].strip()

        # Extract section number (e.g., "1.1", "3.7")
        num_match = re.match(r"^(\d+\.\d+)\s+", cite_line)
        section_num = num_match.group(1) if num_match else ""

        # For textbook sections (no number), use the heading text
        if not section_num:
            # Could be "Quantum Optics", "Waveguide Theory", etc.
            section_num = slug(cite_line[:40])

        body = "\n".join(lines[1:]).strip()

        # Extract rating
        rating_match = re.search(r"\*\*\[(Essential|Important|Supplementary)\]", body)
        rating = rating_match.group(1) if rating_match else "Unrated"

        # Extract tracks from the rating line
        tracks = extract_tracks(body)

        # Extract year
        year_match = re.search(r"\((\d{4})\)", cite_line)
        year = year_match.group(1) if year_match else ""

        # Extract author(s) - first author's last name
        author_match = re.match(r"[\d.]*\s*([A-Z][a-z]+(?:\s+et\s+al\.)?)", cite_line)
        first_author = author_match.group(1) if author_match else ""

        # Extract journal/source - text in *...*
        journal_match = re.search(r"\*([^*]+)\*", cite_line)
        journal = journal_match.group(1) if journal_match else ""

        # Extract DOI
        doi_match = re.search(r"DOI:\s*\[([^\]]+)\]", body + "\n" + cite_line)
        if not doi_match:
            doi_match = re.search(r"DOI:\s*\[([^\]]+)\]", cite_line)
        doi = doi_match.group(1) if doi_match else ""

        # Get the category from the parent ## heading
        category = ""
        # We'll derive it from the section number
        cat_map = {
            "1": "Foundational Biophoton Science",
            "2": "Neural Biophoton Hypothesis",
            "3": "Neural Waveguide Theory",
            "4": "Quantum Models",
            "5": "Time-Series and Statistical Methods",
            "6": "Reviews and Perspectives",
            "7": "Key Textbooks",
        }
        if section_num and "." in section_num:
            cat_key = section_num.split(".")[0]
            category = cat_map.get(cat_key, "")

        # Clean annotation text (remove rating line)
        annotation = re.sub(r"\*\*\[(?:Essential|Important|Supplementary)\].*?\*\*\s*", "", body).strip()
        annotation = annotation.rstrip("-").strip()

        entity_id = f"paper-{section_num}" if section_num else f"paper-{slug(cite_line[:50])}"

        # Textbook section headers (section 7) have no DOI, no year, no rating
        # They are headings like "Quantum Optics", "Waveguide Theory" etc.
        is_textbook = (not year and not doi and category == "Key Textbooks") or (
            "." not in section_num and rating == "Unrated"
        )

        entities.append({
            "id": entity_id,
            "type": "textbook" if is_textbook else "paper",
            "title": cite_line.strip(),
            "section": section_num,
            "first_author": first_author,
            "year": year,
            "journal": journal,
            "doi": doi,
            "rating": rating,
            "category": category,
            "tracks": tracks,
            "annotation": annotation,
            "concepts": extract_concepts(cite_line + " " + body),
        })

    # Also parse the summary table for any papers we might have missed
    # and the "New Additions" section
    new_additions = re.search(
        r"## New Additions.*?\n(.*?)(?=\n##|\Z)", text, re.DOTALL
    )
    if new_additions:
        table_text = new_additions.group(1)
        for row in re.finditer(
            r"\|\s*([^|]+)\|\s*(\d{4})\s*\|\s*([^|]+)\|\s*([^|]+)\|\s*([^|]+)\|",
            table_text
        ):
            ref = row.group(1).strip()
            year = row.group(2).strip()
            cat = row.group(3).strip()
            relevance = row.group(4).strip()
            tracks_str = row.group(5).strip()

            eid = f"paper-new-{slug(ref[:40])}"
            # Skip if we already have an entity with similar title
            if any(ref[:20].lower() in e["title"].lower() for e in entities):
                continue

            track_nums = [t.strip().zfill(2) for t in re.findall(r"\d+", tracks_str)]

            entities.append({
                "id": eid,
                "type": "paper",
                "title": ref,
                "section": "",
                "first_author": ref.split(" ")[0] if ref else "",
                "year": year,
                "journal": "",
                "doi": "",
                "rating": relevance,
                "category": cat,
                "tracks": track_nums,
                "annotation": "",
                "concepts": extract_concepts(ref),
            })

    return entities


# ── prediction parser ────────────────────────────────────────────────────────

def parse_predictions(path: Path) -> tuple[list[dict], list[dict], list[dict]]:
    """Parse docs/master-predictions.md into prediction, experiment, and cross_check entities."""
    text = path.read_text()
    predictions = []
    experiments = []
    cross_checks = []

    # Parse prediction tables (## 1. through ## 8.)
    pred_sections = re.split(r"^## (\d+)\.\s+(.+)$", text, flags=re.MULTILINE)
    # pred_sections = [preamble, num, title, body, num, title, body, ...]

    i = 1
    while i < len(pred_sections) - 2:
        sec_num = pred_sections[i]
        sec_title = pred_sections[i + 1].strip()
        sec_body = pred_sections[i + 2]
        i += 3

        # Stop when we hit non-prediction sections
        if "consistency" in sec_title.lower() or "accessible" in sec_title.lower():
            # Parse these separately below
            continue

        # Map section numbers to tracks
        sec_track_map = {
            "1": "01", "2": "04", "3": "05", "4": "06",
            "5": "07", "6": "00", "7": "08", "8": "06",
        }

        # Also try to extract track from section title
        title_track_match = re.search(r"Track\s+(\d+)", sec_title)
        section_default_track = ""
        if title_track_match:
            section_default_track = title_track_match.group(1).zfill(2)
        else:
            section_default_track = sec_track_map.get(sec_num, "")

        # Parse table rows
        for row in re.finditer(
            r"\|\s*(\d+\.\d+[a-z]?)\s*\|\s*([^|]+)\|\s*([^|]+)\|\s*([^|]+)\|\s*([^|]+)\|\s*([^|]+)\|",
            sec_body
        ):
            pred_num = row.group(1).strip()
            pred_text = row.group(2).strip()
            expected = row.group(3).strip()
            setup = row.group(4).strip()
            falsification = row.group(5).strip()
            last_col = row.group(6).strip()

            # Determine track: use last column if it's a number 1-8,
            # otherwise fall back to section default
            if last_col.isdigit() and int(last_col) <= 8:
                track = last_col.zfill(2)
            elif "Sim" in last_col:
                track = "00"  # simulator, not a specific track
            else:
                track = section_default_track

            full_text = f"{pred_text} {expected} {setup} {falsification}"

            predictions.append({
                "id": f"pred-{pred_num}",
                "type": "prediction",
                "title": pred_text,
                "section": pred_num,
                "section_title": sec_title,
                "expected_value": expected,
                "required_setup": setup,
                "falsification": falsification,
                "track": track,
                "tracks": [track],
                "concepts": extract_concepts(full_text),
            })

    # Parse cross-track consistency checks
    consistency_match = re.search(
        r"### Confirmed Consistencies\s*\n(.*?)(?=###|\Z)", text, re.DOTALL
    )
    if consistency_match:
        for row in re.finditer(
            r"\|\s*(C\d+)\s*\|\s*([^|]+)\|\s*([^|]+)\|\s*([^|]+)\|",
            consistency_match.group(1)
        ):
            cid = row.group(1).strip()
            tracks_str = row.group(2).strip()
            check = row.group(3).strip()
            status = row.group(4).strip()

            track_nums = [t.strip().zfill(2) for t in re.findall(r"\d+", tracks_str)]

            cross_checks.append({
                "id": f"cross-{cid.lower()}",
                "type": "cross_check",
                "title": check,
                "check_id": cid,
                "tracks": track_nums,
                "status": status,
                "severity": "",
                "resolution": "",
                "concepts": extract_concepts(check),
            })

    # Parse tensions
    tension_match = re.search(
        r"### Identified Tensions\s*\n(.*?)(?=\n---|\n##|\Z)", text, re.DOTALL
    )
    if tension_match:
        for row in re.finditer(
            r"\|\s*(T\d+)\s*\|\s*([^|]+)\|\s*([^|]+)\|\s*([^|]+)\|\s*([^|]+)\|",
            tension_match.group(1)
        ):
            tid = row.group(1).strip()
            tracks_str = row.group(2).strip()
            tension = row.group(3).strip()
            severity = row.group(4).strip()
            resolution = row.group(5).strip()

            track_nums = []
            for t in re.findall(r"\d+", tracks_str):
                track_nums.append(t.zfill(2))

            cross_checks.append({
                "id": f"cross-{tid.lower()}",
                "type": "cross_check",
                "title": tension,
                "check_id": tid,
                "tracks": track_nums,
                "status": "TENSION",
                "severity": severity.strip("*").strip(),
                "resolution": resolution,
                "concepts": extract_concepts(tension + " " + resolution),
            })

    # Parse experiment tiers
    for tier_match in re.finditer(
        r"### (Tier \d+):?\s*([^\n]+)\n(.*?)(?=### Tier|\n---|\n##|\Z)",
        text, re.DOTALL
    ):
        tier = tier_match.group(1).strip()
        tier_desc = tier_match.group(2).strip()
        tier_body = tier_match.group(3)

        for row in re.finditer(
            r"\|\s*(\d+)\s*\|\s*([^|]+)\|\s*([^|]+)\|\s*([^|]+)\|\s*([^|]+)\|\s*([^|]+)\|",
            tier_body
        ):
            rank = row.group(1).strip()
            name = row.group(2).strip()
            pred_tested = row.group(3).strip()
            equipment = row.group(4).strip()
            time_str = row.group(5).strip()
            cost = row.group(6).strip()

            full_text = f"{name} {pred_tested} {equipment}"

            # Extract track references from prediction numbers
            track_refs = set()
            for p in re.findall(r"(\d+)\.\d+", pred_tested):
                # Map prediction section to track
                sec_track_map = {"1": "01", "2": "04", "3": "05", "4": "06",
                                 "5": "07", "6": "00", "7": "08", "8": "06"}
                track_refs.add(sec_track_map.get(p, ""))
            track_refs.discard("")

            experiments.append({
                "id": f"exp-{rank}",
                "type": "experiment",
                "title": name,
                "rank": int(rank),
                "tier": tier,
                "tier_description": tier_desc,
                "predictions_tested": pred_tested,
                "equipment": equipment,
                "integration_time": time_str,
                "estimated_cost": cost,
                "tracks": sorted(track_refs),
                "concepts": extract_concepts(full_text),
            })

    return predictions, experiments, cross_checks


# ── findings parser ──────────────────────────────────────────────────────────

def parse_findings(path: Path) -> list[dict]:
    """Parse FINDINGS_LOG.md into finding entities."""
    text = path.read_text()
    entities = []

    # Split on ## headings
    sections = re.split(r"^## (\d{4}-\d{2}-\d{2})\s+\[([^\]]+)\]\s+(.+)$", text, flags=re.MULTILINE)
    # sections = [preamble, date, tag, title, body, date, tag, title, body, ...]

    i = 1
    while i < len(sections) - 3:
        date = sections[i]
        tag = sections[i + 1]
        title = sections[i + 2].strip()
        body = sections[i + 3]
        i += 4

        # Extract key fields
        what_match = re.search(r"\*\*What:\*\*\s*(.+?)(?=\n\*\*|\Z)", body, re.DOTALL)
        numbers_match = re.search(r"\*\*Numbers:\*\*\s*(.+?)(?=\n\*\*|\Z)", body, re.DOTALL)
        why_match = re.search(r"\*\*Why it matters:\*\*\s*(.+?)(?=\n\*\*|\Z)", body, re.DOTALL)
        files_match = re.search(r"\*\*Files:\*\*\s*(.+?)(?=\n\*\*|\Z)", body, re.DOTALL)
        podcast_match = re.search(r"\*\*Podcast potential:\*\*\s*(.+?)(?=\n\*\*|\n---|\Z)", body, re.DOTALL)

        what = what_match.group(1).strip() if what_match else ""
        numbers = numbers_match.group(1).strip() if numbers_match else ""
        why = why_match.group(1).strip() if why_match else ""
        files = files_match.group(1).strip() if files_match else ""
        podcast = podcast_match.group(1).strip() if podcast_match else ""

        # Extract track from tag
        tracks = []
        track_match = re.search(r"TRACK-(\d+)", tag)
        if track_match:
            tracks = [track_match.group(1).zfill(2)]
        elif tag in ("SIMULATOR", "BREAKTHROUGH", "CRITICAL"):
            tracks = extract_tracks(body)

        eid = f"finding-{date}-{slug(tag)}"
        full_text = f"{title} {what} {numbers} {why}"

        entities.append({
            "id": eid,
            "type": "finding",
            "title": title,
            "date": date,
            "tag": tag,
            "what": what,
            "numbers": numbers,
            "why_it_matters": why,
            "files": files,
            "podcast_potential": podcast,
            "tracks": tracks,
            "concepts": extract_concepts(full_text),
        })

    return entities


# ── track parser ─────────────────────────────────────────────────────────────

TRACK_INFO = {
    "01": ("Photocount Statistics", "The Quantum Optics Statistician"),
    "02": ("Time-Series & Fractal Analysis", "The Temporal Structure Analyst"),
    "03": ("Waveguide Propagation", "The Computational Photonics Engineer"),
    "04": ("Quantum Optics Formalism", "The Quantum Field Theorist"),
    "05": ("Signal-to-Noise & Detection Theory", "The Detection Engineer"),
    "06": ("Demyelination & Pathology", "The Biomedical Modeler"),
    "07": ("Unified Multi-Scale Model", "The Systems Integrator"),
    "08": ("MMI & Coherence Bridge", "The MMI-Biophoton Bridge Builder"),
}


def parse_tracks() -> list[dict]:
    """Create track entities from known track info + ROLE.md files."""
    entities = []
    for num, (title, role) in TRACK_INFO.items():
        role_path = ROOT / f"track-{num}" / "ROLE.md"
        mission = ""
        if role_path.exists():
            role_text = role_path.read_text()
            # Extract mission section
            mission_match = re.search(
                r"## Your Mission\s*\n(.*?)(?=\n##|\Z)", role_text, re.DOTALL
            )
            if mission_match:
                mission = mission_match.group(1).strip()

        track_files = list((ROOT / "tracks").glob(f"{num}-*.md"))
        track_doc_name = track_files[0].name if track_files else ""

        # Index the full track document content for deep search
        track_summary = ""
        if track_files:
            track_text = track_files[0].read_text()
            # Extract section headings as a summary
            headings = re.findall(r"^##+ (.+)$", track_text, re.MULTILINE)
            track_summary = " | ".join(headings)

        all_text = f"{title} {role} {mission} {track_summary}"

        entities.append({
            "id": f"track-{num}",
            "type": "track",
            "title": f"Track {num}: {title}",
            "track_number": num,
            "agent_role": role,
            "mission": mission,
            "track_document": track_doc_name,
            "track_sections": track_summary,
            "tracks": [num],
            "concepts": extract_concepts(all_text),
        })

    return entities


# ── research group parser ────────────────────────────────────────────────────

def parse_research_groups() -> list[dict]:
    """Extract research groups mentioned across findings and bibliography."""
    groups = {
        "zangari": {
            "name": "Zangari Group (Rome)",
            "description": "Nanoantenna theory + experimental confirmation (Ag+ at nodes of Ranvier). Dormant since 2021.",
            "key_papers": ["Zangari & Micheli 2018", "Zangari et al. 2021"],
            "tracks": ["01", "02", "06"],
        },
        "kumar-simon": {
            "name": "Kumar/Bhatt/Simon Group (Calgary)",
            "description": "Founded the neural waveguide hypothesis. Waveguide modeling, backpropagation learning proposal.",
            "key_papers": ["Kumar et al. 2016", "Kumar et al. 2018", "Zarkeshian et al. 2022"],
            "tracks": ["01", "03", "05"],
        },
        "dai": {
            "name": "Tang & Dai Group (Wuhan)",
            "description": "Experimental biophoton imaging + spectral measurements. In situ biophoton autography, glutamate-induced emission, species redshift.",
            "key_papers": ["Sun, Wang & Dai 2010", "Tang & Dai 2014", "Wang et al. 2016"],
            "tracks": ["01", "02", "06"],
        },
        "frede-simon": {
            "name": "Frede/Zadeh-Haghighi/Simon Group (Calgary/Waterloo)",
            "description": "Multi-node polarization preservation. Called nodes 'relay amplifiers'. Bridges waveguide theory and quantum optics.",
            "key_papers": ["Frede et al. 2023"],
            "tracks": ["01", "03"],
        },
        "cifra": {
            "name": "Cifra Group (Prague)",
            "description": "Rigorous critical examination of coherence claims. Established statistical standards for biophoton research.",
            "key_papers": ["Cifra & Pospisil 2014", "Cifra et al. 2015"],
            "tracks": ["02", "03", "04"],
        },
        "popp": {
            "name": "Popp Group (historical)",
            "description": "Founded biophoton research. Coined the term, proposed coherent field hypothesis. Claims later critiqued by Cifra.",
            "key_papers": ["Popp et al. 1984", "Popp et al. 1992", "Popp et al. 2002"],
            "tracks": ["02", "03", "04"],
        },
        "casey-murugan": {
            "name": "Casey/Murugan Group",
            "description": "First systematic tracking of UPE from living human brain. Coined 'photoencephalography'. 2025 iScience paper.",
            "key_papers": ["Casey et al. 2025"],
            "tracks": ["02", "04", "05"],
        },
        "liu-chen-ao": {
            "name": "Liu/Chen/Ao Group",
            "description": "Cavity QED treatment of myelin sheath. Entangled biphoton generation model. Published in Physical Review E 2024.",
            "key_papers": ["Liu, Chen & Ao 2024"],
            "tracks": ["01", "03"],
        },
    }

    entities = []
    for gid, info in groups.items():
        full_text = f"{info['name']} {info['description']} {' '.join(info['key_papers'])}"
        entities.append({
            "id": f"group-{gid}",
            "type": "research_group",
            "title": info["name"],
            "description": info["description"],
            "key_papers": info["key_papers"],
            "tracks": info["tracks"],
            "concepts": extract_concepts(full_text),
        })

    return entities


# ── concept reverse index ────────────────────────────────────────────────────

def build_concept_entities(all_entities: list[dict]) -> list[dict]:
    """Build concept entities as a reverse index from all other entities."""
    concept_map: dict[str, list[str]] = defaultdict(list)

    for e in all_entities:
        for c in e.get("concepts", []):
            concept_map[c].append(e["id"])

    entities = []
    for concept, refs in sorted(concept_map.items()):
        if len(refs) < 2:
            continue  # Skip concepts appearing only once
        entities.append({
            "id": f"concept-{slug(concept)}",
            "type": "concept",
            "title": concept,
            "entity_refs": refs,
            "ref_count": len(refs),
            "concepts": [concept],
        })

    return entities


# ── main ─────────────────────────────────────────────────────────────────────

def main():
    all_entities = []
    counts = defaultdict(int)

    # 1. Papers
    bib_path = ROOT / "docs" / "bibliography.md"
    if bib_path.exists():
        papers = parse_bibliography(bib_path)
        all_entities.extend(papers)
        counts["paper"] = len(papers)
        print(f"  papers: {len(papers)}")
    else:
        print(f"  WARNING: {bib_path} not found", file=sys.stderr)

    # 2. Predictions, experiments, cross-checks
    pred_path = ROOT / "docs" / "master-predictions.md"
    if pred_path.exists():
        predictions, experiments, cross_checks = parse_predictions(pred_path)
        all_entities.extend(predictions)
        all_entities.extend(experiments)
        all_entities.extend(cross_checks)
        counts["prediction"] = len(predictions)
        counts["experiment"] = len(experiments)
        counts["cross_check"] = len(cross_checks)
        print(f"  predictions: {len(predictions)}")
        print(f"  experiments: {len(experiments)}")
        print(f"  cross_checks: {len(cross_checks)}")
    else:
        print(f"  WARNING: {pred_path} not found", file=sys.stderr)

    # 3. Findings
    findings_path = ROOT / "FINDINGS_LOG.md"
    if findings_path.exists():
        findings = parse_findings(findings_path)
        all_entities.extend(findings)
        counts["finding"] = len(findings)
        print(f"  findings: {len(findings)}")
    else:
        print(f"  WARNING: {findings_path} not found", file=sys.stderr)

    # 4. Tracks
    tracks = parse_tracks()
    all_entities.extend(tracks)
    counts["track"] = len(tracks)
    print(f"  tracks: {len(tracks)}")

    # 5. Research groups
    groups = parse_research_groups()
    all_entities.extend(groups)
    counts["research_group"] = len(groups)
    print(f"  research_groups: {len(groups)}")

    # 6. Concept reverse index (built from all above)
    concepts = build_concept_entities(all_entities)
    all_entities.extend(concepts)
    counts["concept"] = len(concepts)
    print(f"  concepts: {len(concepts)}")

    # Write JSONL
    with open(OUT, "w") as f:
        for e in all_entities:
            f.write(json.dumps(e, ensure_ascii=False) + "\n")

    total = len(all_entities)
    print(f"\nTotal: {total} entities -> {OUT}")
    print(f"Breakdown: {dict(counts)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
