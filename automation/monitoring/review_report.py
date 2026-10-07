"""Deterministic review reports: group known incidents without discarding evidence."""

from __future__ import annotations

import os
import re
from pathlib import Path
from urllib.parse import quote, urlsplit

DOCS_DIR = Path(__file__).resolve().parents[2] / "docs"
KB_REF = os.environ.get("GITHUB_SHA", "main")
if not re.fullmatch(r"[0-9a-f]{40}", KB_REF):
    KB_REF = "main"
ACTION_ORDER = ("NEW_DOMAIN_NEEDED", "NEW_ENTRY", "UPDATE_ENTRY", "NO_ACTION")
HEADINGS = {
    "NEW_DOMAIN_NEEDED": "## 🔴 New domain needed",
    "NEW_ENTRY": "## 🟠 New entry needed",
    "UPDATE_ENTRY": "## 🟡 Update existing entry",
    "NO_ACTION": "## No action recommended",
}


def text(value) -> str:
    """Keep feed/model text on one line and prevent it becoming report markup."""
    value = " ".join(str(value or "").split())
    return re.sub(r"([\\`*_{}\[\]<>#])", r"\\\1", value)


def link(label, url) -> str:
    try:
        parts = urlsplit(url or "")
        if parts.scheme in {"https", "http"} and parts.netloc:
            return f"[{text(label)}]({quote(url, safe=':/?&=%#@+~')})"
    except ValueError:
        pass
    return f"{text(label)} (source URL unavailable)"


def incident_key(item: dict) -> str | None:
    """AIID RSS uses publisher URLs; its incident URL lives in the excerpt."""
    if item.get("source_id") != "aiid":
        return None
    ids = set(re.findall(
        r"https?://incidentdatabase\.ai/cite/(\d+)(?=[/#?\s)]|$)",
        f"{item.get('url', '')} {item.get('body_excerpt', '')}",
    ))
    # Ambiguous excerpts are left separate rather than guessing an association.
    return f"aiid:{next(iter(ids))}" if len(ids) == 1 else None


def group_results(items: list[dict], classifications: list[dict]) -> list[list[tuple]]:
    by_id = {item["id"]: item for item in items}
    groups = {}
    for index, result in enumerate(classifications):
        item = by_id.get(result.get("item_id"), {})
        key = incident_key(item) or f"item:{index}"
        groups.setdefault(key, []).append((item, result))
    return list(groups.values())


def group_action(group: list[tuple]) -> str:
    # A no-action recommendation must never hide a conflicting action item.
    return min((r["action"] for _, r in group), key=ACTION_ORDER.index)


def kb_context(group: list[tuple], docs_dir: Path) -> list[str]:
    """Show bounded excerpts from matched entries for a human coverage check.

    Literal token/URL matches are context, not proof that an incident is covered.
    No model call, inferred facts, or automatic suppression of recommendations.
    """
    entry_ids = {m.get("kb_id", "").upper() for _, result in group
                 for m in result.get("kb_matches", []) if m.get("kb_id")}
    titles = " ".join(item.get("title", result.get("item_title", ""))
                      for item, result in group).lower()
    tokens = set(re.findall(r"[a-z0-9]{4,}", titles)) - {
        "that", "this", "with", "from", "says", "used", "using", "after", "into", "their",
    }
    urls = {item.get("url") for item, _ in group if item.get("url")}
    excerpts = []
    for path in sorted(docs_dir.glob("domain-*/*.mdx")):
        entry_id = path.stem.split("-", 1)[0].upper()
        if entry_id not in entry_ids:
            continue
        candidates = []
        content = path.read_text(encoding="utf-8").splitlines()
        body_start = 0
        if content and content[0] == "---":
            body_start = next((i + 1 for i, line in enumerate(content[1:], 1)
                               if line == "---"), 0)
        for number, line in enumerate(content[body_start:], body_start + 1):
            words = set(re.findall(r"[a-z0-9]{4,}", line.lower()))
            overlap = tokens & words
            exact_url = any(url in line for url in urls)
            # A year alone (or a frontmatter id/date) is not useful context.
            if not exact_url and not any(not word.isdigit() for word in overlap):
                continue
            score = len(overlap) + 10 * exact_url
            if score:
                candidates.append((score, number, line))
        for _, number, line in sorted(candidates, key=lambda c: (-c[0], c[1]))[:2]:
            url = (f"https://github.com/b-gowland/ai-risk-kb/blob/{KB_REF}/docs/"
                   f"{path.relative_to(docs_dir).as_posix()}#L{number}")
            excerpt = line[:350] + ("…" if len(line) > 350 else "")
            excerpts.append(f"- {link(entry_id, url)}: {text(excerpt)}")
    return excerpts


def generate_report(
    run_date: str,
    all_items: list[dict],
    classifications: list[dict],
    source_counts: dict[str, int],
    source_health: dict[str, dict] | None = None,
    *,
    docs_dir: Path = DOCS_DIR,
) -> str:
    groups = group_results(all_items, classifications)
    action_groups = sum(group_action(group) != "NO_ACTION" for group in groups)
    action_items = sum(c["action"] != "NO_ACTION" for c in classifications)
    classified_ids = {c.get("item_id") for c in classifications}
    missing = [item for item in all_items if item["id"] not in classified_ids]
    failing = {sid: health for sid, health in (source_health or {}).items()
               if health.get("consecutive_failures")}
    lines = [
        f"# Source monitoring report — {text(run_date)}", "",
        f"**Items received:** {len(all_items)}  ",
        f"**Items reviewed:** {len(classifications)}  ",
        f"**Items requiring action:** {action_items}  ",
        f"**Review groups requiring action:** {action_groups}  ",
        f"**No action:** {len(classifications) - action_items}  ", "",
        "Reports sharing an explicit AIID incident ID are grouped; all recommendations "
        "and source links are retained. Other items stay separate.", "",
        "**Sources with new items:**",
    ]
    lines += [f"- {text(sid)}: {count} new item(s)" for sid, count in sorted(source_counts.items())]
    if failing:
        lines += ["", "**Sources that failed to poll this run:**"]
        for sid, health in sorted(failing.items()):
            lines.append(f"- {text(sid)}: {health['consecutive_failures']} consecutive failure(s); "
                         f"last error: {text(health.get('last_error'))}")
    if missing:
        lines += ["", "## Incomplete classification — retry required", ""]
        lines += [f"- {link(item.get('title', item['id']), item.get('url'))}" for item in missing]

    for action in ACTION_ORDER:
        selected = [group for group in groups if group_action(group) == action]
        if not selected:
            continue
        lines += ["", HEADINGS[action], ""]
        for group in selected:
            first_item, first_result = group[0]
            title = first_item.get("title") or first_result.get("item_title", "Untitled")
            lines += [f"### {text(title)}", ""]
            key = incident_key(first_item)
            if key:
                incident_id = key.split(":")[1]
                lines += [link(f"AIID incident {incident_id}",
                               f"https://incidentdatabase.ai/cite/{incident_id}"), ""]
            for item, result in group:
                label = item.get("title") or result.get("item_title", "Untitled")
                lines += [f"- **Source:** {link(label, item.get('url'))}",
                          f"  **Recommendation ({text(result['action'])}):** "
                          f"{text(result.get('recommended_action'))}",
                          f"  **Evidence:** {text(result.get('evidence_quote'))}"]
                for match in result.get("kb_matches", []):
                    lines.append(f"  - **{text(match.get('kb_id', '?'))}** "
                                 f"({text(match.get('confidence', '?'))}): "
                                 f"{text(match.get('rationale'))}")
            context = kb_context(group, docs_dir)
            if context:
                lines += ["", "<details>",
                          "<summary>Compare with existing KB excerpts</summary>", "",
                          "Check whether an update is still needed. "
                          "These are text matches, not a finding that the item is already covered."]
                lines += context
                lines += ["", "</details>"]
            lines.append("")

    if not action_items and not missing and not failing:
        lines += ["## No action recommended for the classified items", ""]
    elif not action_items:
        lines += ["Review is incomplete; this report does not establish that "
                  "no updates are needed.", ""]
    lines += ["---", "",
              "_Generated by Workflow 2 (source-driven monitoring). "
              "Human review required before any KB changes._",
              "_Review each group, decide action (Approve / Reject / Modify), "
              "close issue when done._"]
    return "\n".join(lines)
