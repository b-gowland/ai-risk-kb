#!/usr/bin/env python3
"""
Workflow 2 — Source-driven monitoring: poll-sources.py
=======================================================
Deterministic per-source poller. Reads monitoring-sources.md, fetches each
source using the appropriate strategy, diffs against last-seen state, and
writes monitoring-diff.json for classify.py to consume.

No LLM calls here. This is pure fetch-and-diff.

Strategies per source type:
  - github_releases: GitHub Releases API (OWASP, ATLAS)
  - github_changelog: clone --depth 1, parse CHANGELOG.md (MITRE ATLAS data repo)
  - rss_feed: fetch RSS/Atom feed, diff against last-seen entry GUIDs
  - html_index: fetch page, extract links/headings, diff against last snapshot
  - mit_airr: MIT AI Risk Repository blog index (quarterly, high signal)

State file: automation/monitoring/last-seen-state.json
Output:     automation/monitoring/monitoring-diff.json

Run:
  python automation/monitoring/poll-sources.py
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import tempfile
import time
import urllib.error
import urllib.request
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

# ============================================================
# PATHS
# ============================================================

REPO_ROOT = Path(__file__).resolve().parents[2]
MONITORING_DIR = REPO_ROOT / "automation" / "monitoring"
STATE_FILE = MONITORING_DIR / "last-seen-state.json"
OUTPUT_FILE = MONITORING_DIR / "monitoring-diff.json"
MONITORING_SOURCES_MD = REPO_ROOT / "docs" / "monitoring-sources.md"

MONITORING_DIR.mkdir(parents=True, exist_ok=True)


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


# ============================================================
# STATE MANAGEMENT
# ============================================================

def load_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except Exception:
            pass
    return {}


def save_state(state: dict) -> None:
    STATE_FILE.write_text(json.dumps(state, indent=2))


# ============================================================
# HTTP HELPERS
# ============================================================

HEADERS = {
    "User-Agent": "ai-risk-kb-monitor/1.0 (github.com/b-gowland/ai-risk-kb)",
    "Accept": "application/json, application/xml, text/html, */*",
}


def fetch_url(url: str, timeout: int = 30) -> str | None:
    """Fetch a URL and return text content, or None on failure."""
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
            charset = resp.headers.get_content_charset() or "utf-8"
            return raw.decode(charset, errors="replace")
    except Exception as exc:
        print(f"  [WARN] fetch failed for {url}: {exc}")
        return None


def fetch_json(url: str, timeout: int = 30) -> Any | None:
    """Fetch a URL and parse as JSON."""
    text = fetch_url(url, timeout)
    if text is None:
        return None
    try:
        return json.loads(text)
    except Exception as exc:
        print(f"  [WARN] JSON parse failed for {url}: {exc}")
        return None


# ============================================================
# SOURCE STRATEGIES
# ============================================================

def poll_github_releases(source_id: str, repo: str, state: dict) -> list[dict]:
    """
    Poll GitHub Releases API. Returns new releases since last-seen tag.
    repo: 'owner/repo'
    """
    url = f"https://api.github.com/repos/{repo}/releases?per_page=10"
    # Add auth header if available (avoids rate limiting)
    gh_token = os.environ.get("GITHUB_TOKEN", "")
    headers = {**HEADERS, "Accept": "application/vnd.github+json"}
    if gh_token:
        headers["Authorization"] = f"Bearer {gh_token}"

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as resp:
            releases = json.loads(resp.read())
    except Exception as exc:
        print(f"  [WARN] GitHub releases fetch failed for {repo}: {exc}")
        return []

    last_seen = state.get(source_id, {}).get("last_seen_tag", "")
    new_releases = []

    for rel in releases:
        tag = rel.get("tag_name", "")
        if tag == last_seen:
            break
        if rel.get("draft") or rel.get("prerelease"):
            continue
        new_releases.append({
            "source_id": source_id,
            "type": "release",
            "id": tag,
            "title": rel.get("name") or tag,
            "url": rel.get("html_url", ""),
            "body_excerpt": (rel.get("body") or "")[:1000],
            "release_date": rel.get("published_at", "")[:10],
        })

    if releases:
        # Update state to most recent tag
        state.setdefault(source_id, {})["last_seen_tag"] = releases[0].get("tag_name", "")

    return new_releases


def poll_mitre_atlas_changelog(source_id: str, state: dict) -> list[dict]:
    """
    Clone mitre-atlas/atlas-data at depth 1, parse CHANGELOG.md for new versions.
    Falls back to GitHub Releases API if clone fails.
    """
    last_seen_version = state.get(source_id, {}).get("last_seen_version", "")

    # Try GitHub Releases first (faster, no clone needed)
    items = poll_github_releases(source_id + "_releases", "mitre-atlas/atlas-data", state)
    # Map release tags to changelog-style entries
    results = []
    for item in items:
        results.append({
            "source_id": source_id,
            "type": "release",
            "id": item["id"],
            "title": f"MITRE ATLAS {item['id']}",
            "url": "https://atlas.mitre.org/updates/",
            "body_excerpt": item["body_excerpt"],
            "release_date": item["release_date"],
        })

    # Also try fetching CHANGELOG.md directly from GitHub
    changelog_url = "https://raw.githubusercontent.com/mitre-atlas/atlas-data/main/CHANGELOG.md"
    changelog_text = fetch_url(changelog_url)
    if changelog_text:
        # Parse version headers: ## vX.Y.Z or ## Version X.Y.Z
        versions = re.findall(
            r'^#{1,3}\s+(?:v|Version\s+)?(\d+\.\d+\.\d+)[^\n]*\n(.*?)(?=\n#{1,3}\s|\Z)',
            changelog_text, re.M | re.S
        )
        new_versions = []
        for ver, body in versions:
            if ver == last_seen_version:
                break
            new_versions.append({
                "source_id": source_id,
                "type": "changelog_entry",
                "id": f"atlas-v{ver}",
                "title": f"MITRE ATLAS v{ver}",
                "url": "https://atlas.mitre.org/updates/",
                "body_excerpt": body.strip()[:1000],
                "release_date": "",  # not always in changelog
            })

        if versions:
            state.setdefault(source_id, {})["last_seen_version"] = versions[0][0]

        # Deduplicate with release entries
        seen_ids = {r["id"] for r in results}
        for item in new_versions:
            if item["id"] not in seen_ids:
                results.append(item)

    return results


def poll_owasp_llm(source_id: str, state: dict) -> list[dict]:
    """
    Poll OWASP LLM Top 10 GitHub repo releases.
    Also checks for new documents in the llmtop10 releases.
    """
    items = poll_github_releases(source_id, "OWASP/www-project-top-10-for-large-language-model-applications", state)
    # Supplement: check the releases page via API
    if not items:
        # Try alternate repo slug
        items = poll_github_releases(source_id + "_alt", "OWASP/www-project-llm-ai-security", state)
    return items


def poll_rss_feed(source_id: str, url: str, state: dict) -> list[dict]:
    """
    Fetch an RSS or Atom feed, return new entries since last-seen GUIDs.
    """
    text = fetch_url(url)
    if not text:
        return []

    # Extract items — handle both RSS <item> and Atom <entry>
    item_pattern = re.compile(r'<(?:item|entry)>(.*?)</(?:item|entry)>', re.S)
    items_raw = item_pattern.findall(text)

    def extract(tag: str, blob: str) -> str:
        m = re.search(rf'<{tag}[^>]*>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</{tag}>', blob, re.S)
        return m.group(1).strip() if m else ""

    last_seen_guids = set(state.get(source_id, {}).get("seen_guids", []))
    new_items = []
    new_guids = []

    for raw in items_raw[:20]:  # cap at 20 per run
        guid = extract("guid", raw) or extract("id", raw) or extract("link", raw)
        if not guid:
            continue
        guid_hash = hashlib.md5(guid.encode()).hexdigest()
        new_guids.append(guid_hash)
        if guid_hash in last_seen_guids:
            continue

        title = extract("title", raw)
        link = extract("link", raw)
        pub_date = extract("pubDate", raw) or extract("published", raw) or extract("updated", raw)
        description = extract("description", raw) or extract("summary", raw) or extract("content", raw)

        new_items.append({
            "source_id": source_id,
            "type": "rss_entry",
            "id": guid_hash,
            "title": title,
            "url": link,
            "body_excerpt": re.sub(r'<[^>]+>', '', description)[:800],
            "release_date": pub_date[:10] if pub_date else "",
        })

    # Update state — keep last 100 GUIDs
    all_guids = new_guids + list(last_seen_guids)
    state.setdefault(source_id, {})["seen_guids"] = all_guids[:100]

    return new_items


def poll_mit_airr(source_id: str, state: dict) -> list[dict]:
    """
    Poll MIT AI Risk Repository blog for new posts.

    MIT AIRR publishes updates via blog posts at airisk.mit.edu/blog — this is
    the authoritative signal for taxonomy updates, new subdomains, and dataset
    releases. The April 2025 post ("new subdomain: multi-agent risks") is the
    canonical example of what we need to catch.

    Strategy: fetch the /blog index, extract post links and titles, diff against
    last-seen. For each new post, fetch the post itself to extract a meaningful
    excerpt for the classifier.
    """
    results = []
    blog_url = "https://airisk.mit.edu/blog"
    text = fetch_url(blog_url)
    if not text:
        return []

    # Extract blog post links — typically /blog/post-slug pattern
    post_links = re.findall(r'href=["\'](/blog/[a-z0-9][a-z0-9\-]+)["\']', text)
    # Deduplicate preserving order
    seen = set()
    unique_links = []
    for link in post_links:
        if link not in seen and link != "/blog":
            seen.add(link)
            unique_links.append(link)

    last_seen_links = set(state.get(source_id, {}).get("seen_links", []))
    new_links = [l for l in unique_links if l not in last_seen_links]

    for link in new_links[:5]:  # cap at 5 new posts per run
        full_url = f"https://airisk.mit.edu{link}"
        post_text = fetch_url(full_url)

        # Extract title
        title_m = re.search(r'<h1[^>]*>(.*?)</h1>', post_text or "", re.S | re.I)
        title = re.sub(r'<[^>]+>', '', title_m.group(1)).strip() if title_m else link

        # Extract first substantive paragraph as excerpt
        excerpt = ""
        if post_text:
            paras = re.findall(r'<p[^>]*>(.*?)</p>', post_text, re.S | re.I)
            for p in paras:
                clean = re.sub(r'<[^>]+>', '', p).strip()
                if len(clean) > 80:  # skip nav/short paras
                    excerpt = clean[:600]
                    break

        # Extract date if present
        date_m = re.search(r'(\d{4}-\d{2}-\d{2})', post_text or "")
        pub_date = date_m.group(1) if date_m else utc_now()[:10]

        results.append({
            "source_id": source_id,
            "type": "blog_post",
            "id": link,
            "title": f"MIT AI Risk Repository: {title}",
            "url": full_url,
            "body_excerpt": excerpt or "New blog post published. Check for taxonomy updates, new subdomains, or dataset releases.",
            "release_date": pub_date,
        })
        time.sleep(1)

    # Update state — store all seen links
    all_links = list(set(unique_links) | last_seen_links)
    state.setdefault(source_id, {})["seen_links"] = all_links[:200]

    return results


def poll_html_index(source_id: str, url: str, state: dict, link_pattern: str = None) -> list[dict]:
    """
    Fetch an HTML page, extract all links matching a pattern, diff against last-seen.
    Used for government/regulatory sites that don't have RSS.
    """
    text = fetch_url(url)
    if not text:
        return []

    # Extract all href values
    links = re.findall(r'href=["\']([^"\']+)["\']', text)
    if link_pattern:
        links = [l for l in links if re.search(link_pattern, l, re.I)]

    # Hash the set of links for change detection
    links_hash = hashlib.md5("|".join(sorted(set(links))).encode()).hexdigest()
    last_hash = state.get(source_id, {}).get("links_hash", "")

    results = []
    if links_hash != last_hash and last_hash:
        # Extract page title for context
        title_m = re.search(r'<title[^>]*>(.*?)</title>', text, re.S | re.I)
        page_title = re.sub(r'<[^>]+>', '', title_m.group(1)).strip() if title_m else url

        results.append({
            "source_id": source_id,
            "type": "page_update",
            "id": links_hash,
            "title": f"{page_title} — page updated",
            "url": url,
            "body_excerpt": f"Page content has changed. New or removed links detected. Review {url} for new guidance, consultations, or enforcement actions.",
            "release_date": utc_now()[:10],
        })

    state.setdefault(source_id, {})["links_hash"] = links_hash
    return results


def poll_aiid(source_id: str, state: dict) -> list[dict]:
    """
    Poll AI Incident Database for recent incidents via their API/RSS.
    """
    # AIID has a public RSS feed for new incidents
    rss_url = "https://incidentdatabase.ai/rss.xml"
    return poll_rss_feed(source_id, rss_url, state)


# ============================================================
# SOURCE REGISTRY
# Maps source_id → polling function call
# Derived from monitoring-sources.md categories
# ============================================================

def build_source_registry() -> list[dict]:
    """
    Returns the list of sources to poll, aligned with monitoring-sources.md.
    Each entry has: id, label, poll_fn (callable → list[dict])
    """
    return [
        # Incident databases
        {"id": "aiid", "label": "AI Incident Database"},
        {"id": "mit_incident_tracker", "label": "MIT AI Incident Tracker"},
        # Regulatory
        {"id": "eu_ai_office", "label": "EU AI Office"},
        {"id": "nist_ai_rmf", "label": "NIST AI RMF"},
        {"id": "apra", "label": "APRA"},
        {"id": "disr_ai_safety", "label": "DISR AI Safety"},
        # Security frameworks
        {"id": "mitre_atlas", "label": "MITRE ATLAS"},
        {"id": "owasp_llm", "label": "OWASP LLM Top 10"},
        # Academic / research
        {"id": "mit_airr", "label": "MIT AI Risk Repository"},
        # Industry
        {"id": "iapp", "label": "IAPP AI Governance Centre"},
        # AU-specific
        {"id": "oaic", "label": "OAIC AI and Privacy"},
        {"id": "acsc", "label": "ACSC AI Security"},
    ]


def poll_source(source_id: str, state: dict) -> list[dict]:
    """Dispatch to the right polling strategy for each source."""
    print(f"  Polling: {source_id}")
    try:
        if source_id == "aiid":
            return poll_aiid(source_id, state)
        elif source_id == "mit_incident_tracker":
            return poll_html_index(source_id, "https://airisk.mit.edu/ai-incident-tracker", state)
        elif source_id == "mitre_atlas":
            return poll_mitre_atlas_changelog(source_id, state)
        elif source_id == "owasp_llm":
            return poll_github_releases(source_id, "OWASP/www-project-top-10-for-large-language-model-applications", state)
        elif source_id == "mit_airr":
            return poll_mit_airr(source_id, state)
        elif source_id == "eu_ai_office":
            return poll_rss_feed(
                source_id,
                "https://digital-strategy.ec.europa.eu/en/policies/european-approach-artificial-intelligence/rss",
                state
            )
        elif source_id == "nist_ai_rmf":
            return poll_html_index(
                source_id,
                "https://www.nist.gov/system/files/rss-feeds/nist-news.xml",
                state,
                link_pattern=r"ai|artificial.intelligence|risk.management"
            )
        elif source_id == "apra":
            return poll_html_index(
                source_id,
                "https://www.apra.gov.au/news-and-publications/apra-releases",
                state,
                link_pattern=r"ai|artificial|technology|cps.?230|data"
            )
        elif source_id == "disr_ai_safety":
            return poll_html_index(
                source_id,
                "https://www.industry.gov.au/policies-and-initiatives/ai-safety",
                state
            )
        elif source_id == "iapp":
            return poll_rss_feed(
                source_id,
                "https://iapp.org/rss/news/",
                state
            )
        elif source_id == "oaic":
            return poll_html_index(
                source_id,
                "https://www.oaic.gov.au/privacy/privacy-guidance-for-organisations-and-government-agencies/artificial-intelligence",
                state
            )
        elif source_id == "acsc":
            return poll_html_index(
                source_id,
                "https://www.cyber.gov.au/resources-business-and-government/governance-and-user-education/artificial-intelligence",
                state
            )
        else:
            print(f"  [WARN] No polling strategy for {source_id}")
            return []
    except Exception as exc:
        print(f"  [ERROR] Polling failed for {source_id}: {exc}")
        return []


# ============================================================
# MAIN
# ============================================================

def main() -> None:
    print(f"[poll-sources] Starting run at {utc_now()}")
    print(f"[poll-sources] State file: {STATE_FILE}")

    state = load_state()
    sources = build_source_registry()

    all_new_items: list[dict] = []

    for source in sources:
        source_id = source["id"]
        label = source["label"]
        print(f"\n── {label} ({source_id})")
        items = poll_source(source_id, state)
        print(f"   → {len(items)} new item(s)")
        all_new_items.extend(items)
        time.sleep(1)  # be polite to external servers

    # Write output — always, even if no items found
    output = {
        "run_date": utc_now()[:10],
        "run_timestamp": utc_now(),
        "total_new_items": len(all_new_items),
        "items": all_new_items,
    }
    OUTPUT_FILE.write_text(json.dumps(output, indent=2))
    save_state(state)

    print(f"\n[poll-sources] Complete. {len(all_new_items)} new item(s) across {len(sources)} sources.")
    print(f"[poll-sources] Output: {OUTPUT_FILE}")
    print(f"[poll-sources] State:  {STATE_FILE}")


if __name__ == "__main__":
    main()
