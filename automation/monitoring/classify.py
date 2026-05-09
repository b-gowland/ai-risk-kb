#!/usr/bin/env python3
"""
Workflow 2 — Source-driven monitoring: classify.py
===================================================
Reads monitoring-diff.json (from poll-sources.py) and kb-entry-index.json,
makes one Claude API call per source batch to classify each new item against
the 26 KB entry IDs, and writes a human-readable monitoring report.

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
MONITORING_DIR = REPO_ROOT / "automation" / "monitoring"
DIFF_FILE = MONITORING_DIR / "monitoring-diff.json"
OUTPUT_DIR = MONITORING_DIR / "monitoring-output"
REPORTS_DIR = REPO_ROOT / "automation" / "reports"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# KB entry index — built inline from docs (no separate file needed)
KB_ENTRIES = [
    {"id": "A1", "title": "Hallucination / Confabulation", "domain": "A — Technical",
     "topic": "AI produces factually wrong or fabricated outputs presented with confidence."},
    {"id": "A2", "title": "Model Drift / Performance Degradation", "domain": "A — Technical",
     "topic": "Model performance degrades over time as real world shifts from training conditions."},
    {"id": "A3", "title": "Robustness & Brittleness", "domain": "A — Technical",
     "topic": "AI fails unpredictably on unusual inputs, edge cases, or conditions not seen in training."},
    {"id": "A4", "title": "Explainability & Interpretability Gaps", "domain": "A — Technical",
     "topic": "AI models cannot explain why they produced a given output — blocking audit and transparency."},
    {"id": "B1", "title": "Accountability Gaps", "domain": "B — Governance",
     "topic": "No identifiable person or function is responsible for AI system decisions or outcomes."},
    {"id": "B2", "title": "Regulatory Non-Compliance", "domain": "B — Governance",
     "topic": "AI systems breach applicable laws, regulations, or standards across jurisdictions."},
    {"id": "B3", "title": "AI Lifecycle Governance Failure", "domain": "B — Governance",
     "topic": "Inadequate governance across development, deployment, monitoring, and decommissioning."},
    {"id": "B4", "title": "Third-Party / Supply Chain AI Risk", "domain": "B — Governance",
     "topic": "AI risk introduced through vendors, suppliers, open-source components, upstream models."},
    {"id": "C1", "title": "Data Poisoning", "domain": "C — Security",
     "topic": "Adversaries corrupt training data to produce a model that behaves maliciously in targeted scenarios."},
    {"id": "C2", "title": "Prompt Injection", "domain": "C — Security",
     "topic": "Malicious instructions in content hijack an AI system to take unauthorised actions."},
    {"id": "C3", "title": "Model Theft / Extraction", "domain": "C — Security",
     "topic": "Adversaries reconstruct a proprietary AI model by querying it and training a surrogate."},
    {"id": "C4", "title": "Deepfakes & Synthetic Media Fraud", "domain": "C — Security",
     "topic": "AI-generated synthetic audio/video used to impersonate individuals and manipulate decisions."},
    {"id": "C5", "title": "AI-Enabled Cyber Attacks", "domain": "C — Security",
     "topic": "Adversaries use AI to enhance scale and sophistication of cyber attacks."},
    {"id": "D1", "title": "Training Data Quality & Representativeness", "domain": "D — Data",
     "topic": "Biased or unrepresentative training data produces models that fail for underrepresented groups."},
    {"id": "D2", "title": "Privacy & Data Protection", "domain": "D — Data",
     "topic": "AI systems create vectors for personal information breaches through memorisation and exfiltration."},
    {"id": "D3", "title": "Intellectual Property & Copyright", "domain": "D — Data",
     "topic": "AI systems may reproduce copyrighted material or carry licence contamination risks."},
    {"id": "E1", "title": "Algorithmic Bias & Discrimination", "domain": "E — Fairness",
     "topic": "AI models produce systematically different outcomes based on protected characteristics."},
    {"id": "E2", "title": "Harmful / Toxic Content Generation", "domain": "E — Fairness",
     "topic": "AI systems generate harmful, offensive, or illegal content at scale."},
    {"id": "E3", "title": "Misinformation & Disinformation", "domain": "E — Fairness",
     "topic": "AI systems generate or amplify false, misleading, or deceptive information at scale."},
    {"id": "F1", "title": "Over-Reliance & Automation Bias", "domain": "F — Deployment",
     "topic": "Users excessively trust AI outputs, reducing independent verification even when AI is wrong."},
    {"id": "F2", "title": "Shadow AI", "domain": "F — Deployment",
     "topic": "Employees use unauthorised AI tools, submitting sensitive data outside organisational control."},
    {"id": "F3", "title": "Scope Creep & Deployment Beyond Intended Use", "domain": "F — Deployment",
     "topic": "AI systems used beyond their intended, tested, approved scope — invalidating the risk assessment."},
    {"id": "G1", "title": "Operational Dependency & Concentration Risk", "domain": "G — Systemic",
     "topic": "Over-reliance on a small number of hyperscale AI providers creates systemic single points of failure."},
    {"id": "G2", "title": "Environmental Impact", "domain": "G — Systemic",
     "topic": "Training and operating large AI models consumes significant energy and water."},
    {"id": "G3", "title": "Workforce Displacement & Socioeconomic Impact", "domain": "G — Systemic",
     "topic": "AI-driven automation displaces roles, creating operational and reputational risk."},
    {"id": "G4", "title": "AI System Safety & Loss of Control", "domain": "G — Systemic",
     "topic": "Agentic and autonomous AI systems take actions beyond the scope intended or authorised."},
]

KB_INDEX_TEXT = "\n".join(
    f"  {e['id']} | {e['title']} | {e['domain']} | {e['topic']}"
    for e in KB_ENTRIES
)


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


# ============================================================
# CLASSIFICATION
# ============================================================

CLASSIFY_SYSTEM = """You are a classifier for an AI risk knowledge base (KB). 
Your job is to read new items from AI risk monitoring sources and determine 
whether each item should trigger a KB update.

The KB has 26 entries across 7 domains (A–G). Your output must be valid JSON only — 
no preamble, no markdown fences, no explanation outside the JSON structure.

For each item, classify as one of:
  NEW_DOMAIN_NEEDED  — item describes a risk category with no matching KB entry
  NEW_ENTRY          — item warrants a new entry within an existing domain  
  UPDATE_ENTRY       — item warrants updating one or more existing entries
  NO_ACTION          — item is not relevant to the KB or is already well-covered

Be conservative: prefer UPDATE_ENTRY or NO_ACTION over NEW_ENTRY or NEW_DOMAIN_NEEDED 
unless the gap is clear and significant."""


def classify_batch(items: list[dict], client: anthropic.Anthropic) -> list[dict]:
    """Classify a batch of monitoring items against the KB index."""
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

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            system=CLASSIFY_SYSTEM,
            messages=[{"role": "user", "content": prompt}],
        )
        text = response.content[0].text.strip()
        # Strip markdown fences if present
        text = text.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        return json.loads(text)
    except Exception as exc:
        print(f"  [ERROR] Classification API call failed: {exc}")
        return []


# ============================================================
# REPORT GENERATION
# ============================================================

def generate_report(
    run_date: str,
    all_items: list[dict],
    classifications: list[dict],
    source_counts: dict[str, int],
) -> str:
    """Generate human-readable markdown report."""

    # Bucket by action
    new_domain = [c for c in classifications if c.get("action") == "NEW_DOMAIN_NEEDED"]
    new_entry = [c for c in classifications if c.get("action") == "NEW_ENTRY"]
    update_entry = [c for c in classifications if c.get("action") == "UPDATE_ENTRY"]
    no_action = [c for c in classifications if c.get("action") == "NO_ACTION"]

    action_count = len(new_domain) + len(new_entry) + len(update_entry)

    lines = [
        f"# Source monitoring report — {run_date}",
        "",
        f"**Items reviewed:** {len(all_items)}  ",
        f"**Items requiring action:** {action_count}  ",
        f"**No action:** {len(no_action)}  ",
        "",
        "**Sources polled:**",
    ]
    for source_id, count in sorted(source_counts.items()):
        lines.append(f"- {source_id}: {count} new item(s)")

    lines += ["", "---", ""]

    if new_domain:
        lines += [
            "## 🔴 New domain needed",
            "_These items describe risk categories not covered by any existing KB entry._",
            "",
        ]
        for c in new_domain:
            lines += [
                f"### {c.get('item_title', 'Untitled')}",
                f"**Action:** {c.get('recommended_action', '')}",
                f"**Evidence:** {c.get('evidence_quote', '')}",
                "",
            ]

    if new_entry:
        lines += [
            "## 🟠 New entry needed",
            "_These items warrant a new KB entry within an existing domain._",
            "",
        ]
        for c in new_entry:
            matches = c.get("kb_matches", [])
            domain = matches[0]["kb_id"][0] if matches else "?"
            lines += [
                f"### {c.get('item_title', 'Untitled')} → Domain {domain}",
                f"**Action:** {c.get('recommended_action', '')}",
                f"**Evidence:** {c.get('evidence_quote', '')}",
                "",
            ]

    if update_entry:
        lines += [
            "## 🟡 Update existing entry",
            "_These items should trigger an update to one or more existing KB entries._",
            "",
        ]
        for c in update_entry:
            matches = c.get("kb_matches", [])
            affected = ", ".join(m["kb_id"] for m in matches)
            lines += [
                f"### {c.get('item_title', 'Untitled')} → {affected}",
                f"**Action:** {c.get('recommended_action', '')}",
                f"**Evidence:** {c.get('evidence_quote', '')}",
            ]
            for m in matches:
                lines.append(f"- **{m['kb_id']}** ({m['confidence']}): {m['rationale']}")
            lines.append("")

    if not action_count:
        lines += ["## ✅ No action required", "", "All monitored sources checked. No KB updates needed this cycle.", ""]

    lines += [
        "---",
        "",
        "_Generated by Workflow 2 (source-driven monitoring). Human review required before any KB changes._",
        "_Review each item, decide action (Approve / Reject / Modify), close issue when done._",
    ]

    return "\n".join(lines)


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
        report = generate_report(run_date, [], [], {})
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

    for i in range(0, len(all_items), BATCH_SIZE):
        batch = all_items[i:i + BATCH_SIZE]
        print(f"  Classifying batch {i // BATCH_SIZE + 1} ({len(batch)} items)...")
        results = classify_batch(batch, client)
        all_classifications.extend(results)
        if i + BATCH_SIZE < len(all_items):
            time.sleep(2)  # avoid rate limiting

    print(f"  Classified {len(all_classifications)} item(s)")

    # Generate report
    report = generate_report(run_date, all_items, all_classifications, source_counts)

    # Write outputs
    out_path = OUTPUT_DIR / f"{run_date}.md"
    out_path.write_text(report)
    reports_path = REPORTS_DIR / f"monitoring_{run_date}.md"
    reports_path.write_text(report)

    # Write structured JSON alongside the markdown
    json_path = OUTPUT_DIR / f"{run_date}.json"
    json_path.write_text(json.dumps({
        "run_date": run_date,
        "items_reviewed": len(all_items),
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

    # Exit with non-zero if action items found (signals workflow to open issue)
    if action_count > 0:
        sys.exit(2)  # special exit code: "completed with action items"


if __name__ == "__main__":
    main()
