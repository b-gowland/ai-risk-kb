#!/usr/bin/env python3
"""
Workflow 2 — Source-driven monitoring: classify.py
===================================================
Reads monitoring-diff.json (from poll-sources.py) and kb-entry-index.json,
makes one Claude API call per source batch to classify each new item against
the KB entry IDs (read from docs/ frontmatter), and writes a human-readable monitoring report.

Classification outputs per item:
  NEW_DOMAIN_NEEDED  — new risk category not covered by any existing entry
  NEW_ENTRY          — new entry needed within an existing domain
  UPDATE_ENTRY_XX    — existing entry XX should be updated (XX = entry ID)
  NO_ACTION          — not relevant to the KB

Output: automation/monitoring/monitoring-output/YYYY-MM-DD.md
        (also written to automation/reports/ for workflow compatibility)

Run:
  ANTHROPIC_API_KEY=... python automation/monitoring/classify.py
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

try:
    import anthropic
except ImportError:
    print("ERROR: anthropic package not installed. Run: pip install anthropic")
    sys.exit(1)

# ============================================================
# PATHS
# ============================================================

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "automation"))
from claude_client import (  # noqa: E402
    MODEL_SONNET,
    check_stop_reason,
    message_kwargs,
    response_text,
)

from monitoring.review_report import generate_report  # noqa: E402

MONITORING_DIR = REPO_ROOT / "automation" / "monitoring"
DIFF_FILE = MONITORING_DIR / "monitoring-diff.json"
OUTPUT_DIR = MONITORING_DIR / "monitoring-output"
REPORTS_DIR = REPO_ROOT / "automation" / "reports"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

DOCS_DIR = REPO_ROOT / "docs"


def load_kb_entries(docs_dir: Path = DOCS_DIR) -> list[dict]:
    """Build the KB entry index from each entry's frontmatter (title, description)."""
    entries = []
    for path in sorted(docs_dir.glob("domain-*/*.mdx")):
        front = path.read_text(encoding="utf-8").split("---", 2)[1]
        fields = dict(re.findall(r'^(title|description):\s*"?(.*?)"?\s*$', front, re.M))
        title = fields.get("title", path.stem)
        entry_id, _, name = title.partition(" — ")
        domain = path.parent.name.removeprefix("domain-")
        entries.append({"id": entry_id.strip(), "title": name.strip() or title,
                        "domain": f"{entry_id[:1]} — {domain.split('-', 1)[-1].title()}",
                        "topic": fields.get("description", "")[:240]})
    return entries


KB_ENTRIES = load_kb_entries()
KB_INDEX_TEXT = "\n".join(
    f"  {e['id']} | {e['title']} | {e['domain']} | {e['topic']}" for e in KB_ENTRIES
)


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


# ============================================================
# CLASSIFICATION
# ============================================================

CLASSIFY_SYSTEM = """You are a classifier for an AI risk knowledge base (KB). 
Your job is to read new items from AI risk monitoring sources and determine 
whether each item should trigger a KB update.

The KB has {n} entries across 7 domains (A–G). Your output must be valid JSON only — 
no preamble, no markdown fences, no explanation outside the JSON structure.

For each item, classify as one of:
  NEW_DOMAIN_NEEDED  — item describes a risk category with no matching KB entry
  NEW_ENTRY          — item warrants a new entry within an existing domain  
  UPDATE_ENTRY       — item warrants updating one or more existing entries
  NO_ACTION          — item is not relevant to the KB or is already well-covered

Be conservative: prefer UPDATE_ENTRY or NO_ACTION over NEW_ENTRY or NEW_DOMAIN_NEEDED 
unless the gap is clear and significant."""
CLASSIFY_SYSTEM = CLASSIFY_SYSTEM.replace("{n}", str(len(KB_ENTRIES)))


def parse_json_array(text: str) -> list:
    """Extract the first JSON array from model text, tolerating fences and prose."""
    cleaned = text.strip().removeprefix("```json").removeprefix("```").removesuffix("```")
    start = cleaned.find("[")
    if start == -1:
        raise ValueError("no JSON array found in classifier response")
    obj, _end = json.JSONDecoder().raw_decode(cleaned[start:])
    if not isinstance(obj, list):
        raise ValueError("classifier response is not a JSON array")
    return obj


def classify_batch(items: list[dict], client: anthropic.Anthropic) -> list[dict]:
    """Classify a batch of monitoring items against the KB index.

    Raises on API errors, truncation, unparseable output or missing items.
    """
    if not items:
        return []

    items_text = json.dumps([
        {
            "id": item.get("id", ""),
            "source": item.get("source_id", ""),
            "title": item.get("title", ""),
            "excerpt": item.get("body_excerpt", "")[:600],
            "url": item.get("url", ""),
            "date": item.get("release_date", ""),
        }
        for item in items
    ], indent=2)

    prompt = f"""KB entry index (ID | Title | Domain | Topic):
{KB_INDEX_TEXT}

New monitoring items to classify:
{items_text}

Return a JSON array. One object per item:
{{
  "item_id": "<id from input>",
  "item_title": "<title>",
  "action": "NEW_DOMAIN_NEEDED|NEW_ENTRY|UPDATE_ENTRY|NO_ACTION",
  "kb_matches": [
    {{"kb_id": "XX", "confidence": "high|medium|low", "rationale": "one sentence"}}
  ],
  "evidence_quote": "<key phrase from excerpt that justifies the action, max 100 chars>",
  "recommended_action": "<one sentence: what a content editor should do>"
}}

For NO_ACTION items, kb_matches may be empty. For UPDATE_ENTRY, list all affected entry IDs.
Return only the JSON array."""

    # Errors propagate: main() must know a batch failed so it can exit non-zero
    # and the workflow does not commit advanced last-seen state (which would
    # silently drop these items forever).
    response = client.beta.messages.create(
        **message_kwargs(MODEL_SONNET, prompt, effort="low", system=CLASSIFY_SYSTEM)
    )
    check_stop_reason(response)  # refusal / truncation
    results = parse_json_array(response_text(response))
    expected_ids = [item["id"] for item in items]
    returned_ids = [r.get("item_id") for r in results if isinstance(r, dict)]
    if (len(returned_ids) != len(results) or len(set(expected_ids)) != len(expected_ids)
            or sorted(returned_ids, key=str) != sorted(expected_ids, key=str)):
        raise ValueError("classifier must return exactly one result per input item")
    for result in results:
        if result.get("action") not in {"NEW_DOMAIN_NEEDED", "NEW_ENTRY", "UPDATE_ENTRY", "NO_ACTION"}:
            raise ValueError("classifier returned an invalid action")
        matches = result.get("kb_matches")
        if not isinstance(matches, list) or any(not isinstance(m, dict) for m in matches):
            raise ValueError("classifier returned invalid KB matches")
        if any(not isinstance(m.get("kb_id", ""), str) for m in matches):
            raise ValueError("classifier returned an invalid KB entry ID")
    return results


# ============================================================
# MAIN
# ============================================================

def main() -> None:
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY not set")
        sys.exit(1)

    if not DIFF_FILE.exists():
        print(f"ERROR: {DIFF_FILE} not found. Run poll-sources.py first.")
        sys.exit(1)

    diff_data = json.loads(DIFF_FILE.read_text())
    all_items = diff_data.get("items", [])
    run_date = diff_data.get("run_date", utc_now()[:10])

    print(f"[classify] {len(all_items)} item(s) to classify (run date: {run_date})")

    if not all_items:
        print("[classify] Nothing to classify. Writing empty report.")
        report = generate_report(run_date, [], [], {}, diff_data.get("source_health"))
        out_path = OUTPUT_DIR / f"{run_date}.md"
        out_path.write_text(report)
        # Also write to reports/ for workflow compatibility
        (REPORTS_DIR / f"monitoring_{run_date}.md").write_text(report)
        print(f"[classify] Report: {out_path}")
        return

    client = anthropic.Anthropic(api_key=api_key)

    # Count items per source for report summary
    source_counts: dict[str, int] = {}
    for item in all_items:
        sid = item.get("source_id", "unknown")
        source_counts[sid] = source_counts.get(sid, 0) + 1

    # Classify in batches of 10 (keeps prompt size manageable)
    BATCH_SIZE = 10
    all_classifications: list[dict] = []
    failed_batches = 0

    for i in range(0, len(all_items), BATCH_SIZE):
        batch = all_items[i:i + BATCH_SIZE]
        print(f"  Classifying batch {i // BATCH_SIZE + 1} ({len(batch)} items)...")
        try:
            results = classify_batch(batch, client)
        except Exception as exc:
            print(f"  [ERROR] Batch {i // BATCH_SIZE + 1} failed: {exc}")
            failed_batches += 1
            continue
        all_classifications.extend(results)
        if i + BATCH_SIZE < len(all_items):
            time.sleep(2)  # avoid rate limiting

    print(f"  Classified {len(all_classifications)} item(s)")

    # Generate report
    report = generate_report(run_date, all_items, all_classifications, source_counts,
                             diff_data.get("source_health"))

    # Write outputs
    out_path = OUTPUT_DIR / f"{run_date}.md"
    out_path.write_text(report)
    reports_path = REPORTS_DIR / f"monitoring_{run_date}.md"
    reports_path.write_text(report)

    # Write structured JSON alongside the markdown
    json_path = OUTPUT_DIR / f"{run_date}.json"
    json_path.write_text(json.dumps({
        "run_date": run_date,
        "items_reviewed": len(all_classifications),
        "items_received": len(all_items),
        "items": all_items,  # preserve source URLs/excerpts alongside classification IDs
        "failed_batches": failed_batches,
        "classifications": all_classifications,
        "source_counts": source_counts,
    }, indent=2))

    # Count actions for summary
    action_count = sum(
        1 for c in all_classifications
        if c.get("action") in ("NEW_DOMAIN_NEEDED", "NEW_ENTRY", "UPDATE_ENTRY")
    )

    print(f"\n[classify] Complete.")
    print(f"  Items reviewed:        {len(all_items)}")
    print(f"  Requiring action:      {action_count}")
    print(f"  Report: {out_path}")

    if failed_batches:
        # Exit 1 (not 2): the workflow skips the state commit, so these items
        # are re-polled and re-classified on the next run instead of being lost.
        print(f"\n[classify] ERROR: {failed_batches} batch(es) failed; state not advanced.")
        sys.exit(1)

    # Exit with non-zero if action items found (signals workflow to open issue)
    if action_count > 0:
        sys.exit(2)  # special exit code: "completed with action items"


if __name__ == "__main__":
    main()
