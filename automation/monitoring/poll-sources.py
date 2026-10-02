#!/usr/bin/env python3
"""
Workflow 2 — Source-driven monitoring: poll-sources.py
=======================================================
Deterministic per-source poller. Fetches each source in SOURCES, diffs against
last-seen state, and writes monitoring-diff.json for classify.py to consume.

No LLM calls here. This is pure fetch-and-diff.

Source types:
  - rss:        RSS 2.0 / Atom / RDF feed; one item per new entry
                (optionally grouped, e.g. AIID reports -> one item per incident)
  - html_links: listing page without a feed; one item per new matching link
  - file_watch: a value extracted from a raw file (e.g. "Current release: 2026")
  - mit_airr:   MIT AI Risk Repository blog (fetches each new post for an excerpt)

Per-source options: `include` (regex over title + summary), `max_items`.

A source's first successful poll seeds its state without emitting items, so
adding a source never floods the classifier with its back catalogue.

Source health (last success, consecutive failures, last error) is tracked in
the state file and written to the diff. A fetch error, or a feed/page that
yields nothing parseable, counts as a failure.
  python poll-sources.py --health-check
exits 1 when any source has failed HEALTH_FAIL_THRESHOLD runs in a row.

State file: automation/monitoring/last-seen-state.json
Output:     automation/monitoring/monitoring-diff.json

Run:
  python automation/monitoring/poll-sources.py
"""

from __future__ import annotations

import hashlib
import html
import json
import re
import sys
import time
import urllib.request
import xml.etree.ElementTree as ET
from datetime import UTC, datetime, timedelta
from email.utils import parsedate_to_datetime
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse

# ============================================================
# PATHS
# ============================================================

REPO_ROOT = Path(__file__).resolve().parents[2]
MONITORING_DIR = REPO_ROOT / "automation" / "monitoring"
STATE_FILE = MONITORING_DIR / "last-seen-state.json"
OUTPUT_FILE = MONITORING_DIR / "monitoring-diff.json"

HEALTH_FAIL_THRESHOLD = 3
DEFAULT_MAX_ITEMS = 5
# Dated entries older than this are recorded as seen, not emitted, so a newly
# reachable or newly migrated feed never dumps its back catalogue.
DEFAULT_MAX_AGE_DAYS = 30
SEEN_KEYS_KEPT = 500


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


# ============================================================
# SOURCES
# ============================================================

AI_KW = (
    r"\bAI\b|artificial intelligence|machine learning|generative|\bLLMs?\b|agentic"
    r"|automated decision|algorithm"
)

SOURCES: list[dict] = [
    # Incidents
    {
        "id": "aiid", "name": "AI Incident Database", "type": "rss",
        "url": "https://incidentdatabase.ai/rss.xml",
        # The feed is per report; collapse reports to one item per incident.
        "group_by": r"/cite/(\d+)", "max_items": 15,
    },
    # Security frameworks
    {
        "id": "mitre_atlas", "name": "MITRE ATLAS", "type": "rss",
        "url": "https://github.com/mitre-atlas/atlas-data/releases.atom", "max_items": 3,
    },
    {
        "id": "owasp_llm", "name": "OWASP LLM Top 10", "type": "file_watch",
        "url": "https://raw.githubusercontent.com/GenAI-Security-Project/GenAI-LLM-Top10/main/README.md",
        "pattern": r"Current release:\s*([^\n]+)",
        "item_url": "https://genai.owasp.org/llm-top-10/",
    },
    # Research
    {
        "id": "mit_airr", "name": "MIT AI Risk Repository", "type": "mit_airr",
        "url": "https://airisk.mit.edu/blog", "max_items": 5,
    },
    {
        "id": "uk_aisi", "name": "UK AI Security Institute", "type": "rss",
        # Community-maintained mirror of the AISI blog (AISI publishes no feed).
        "url": "https://raw.githubusercontent.com/alan-turing-institute/ai-rss-feeds/main/feeds/aisi-blog.xml",
        "max_items": 5,
    },
    # Regulators and standards bodies
    {
        "id": "nist_ai_rmf", "name": "NIST AI RMF", "type": "rss",
        "url": "https://www.nist.gov/news-events/news/rss.xml",
        "include": AI_KW + r"|CAISI|RMF", "max_items": 5,
    },
    {
        "id": "eu_ai_office", "name": "EU AI Office", "type": "html_links",
        "url": "https://digital-strategy.ec.europa.eu/en/policies/ai-office",
        "link_pattern": r"^/en/(news|library|events)/[a-z0-9-]+$", "max_items": 5,
    },
    {
        "id": "apra", "name": "APRA", "type": "html_links",
        "url": "https://www.apra.gov.au/news-and-publications",
        "link_pattern": r"^/news-and-publications/[a-z0-9-]+$",
        "include": AI_KW + r"|CPS ?23[04]|operational risk|cyber", "max_items": 3,
    },
    {
        "id": "asic", "name": "ASIC", "type": "rss",
        "url": "https://newshub.asic.gov.au/feed/asic/media_en-au",
        "include": AI_KW, "max_items": 3,
    },
    {
        "id": "oaic", "name": "OAIC AI and Privacy", "type": "html_links",
        "url": "https://www.oaic.gov.au/news/media-centre",
        "link_pattern": r"^/news/media-centre/[a-z0-9-]+$",
        "include": AI_KW + r"|privacy act|ADM", "max_items": 3,
    },
    {
        "id": "cisa", "name": "CISA (incl. joint Five Eyes guidance)", "type": "rss",
        # cyber.gov.au (ACSC) and industry.gov.au (DISR) time out from GitHub
        # Actions runners. Joint AI guidance co-sealed by ASD's ACSC is published
        # by CISA too, so CISA news (AI-filtered) stands in for ACSC.
        "url": "https://www.cisa.gov/news.xml",
        "include": AI_KW, "max_items": 5,
    },
]


# ============================================================
# STATE
# ============================================================

def load_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except Exception:
            pass
    return {}


def save_state(state: dict) -> None:
    STATE_FILE.write_text(json.dumps(state, indent=2) + "\n")


def md5(text: str) -> str:
    return hashlib.md5(text.encode()).hexdigest()


# ============================================================
# FETCH + TEXT HELPERS
# ============================================================

HEADERS = {
    # Browser-compatible prefix: several AU government WAFs drop unknown agents.
    "User-Agent": "Mozilla/5.0 (compatible; ai-risk-kb-monitor/2.0; "
                  "+https://github.com/b-gowland/ai-risk-kb)",
    "Accept": "application/rss+xml, application/atom+xml, application/xml, text/html, */*",
}


class SourceError(Exception):
    """A source could not be fetched or yielded nothing usable."""


def fetch_bytes(url: str, timeout: int = 60) -> bytes:
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read()
    except Exception as exc:
        raise SourceError(f"fetch failed: {exc}") from exc


def fetch_text(url: str, timeout: int = 60) -> str:
    return fetch_bytes(url, timeout).decode("utf-8", errors="replace")


def clean_text(fragment: str, limit: int = 800) -> str:
    """Strip tags, unescape entities, collapse whitespace."""
    text = re.sub(r"<[^>]+>", " ", html.unescape(fragment or ""))
    return re.sub(r"\s+", " ", html.unescape(text)).strip()[:limit]


def to_iso_date(value: str) -> str:
    value = (value or "").strip()
    if not value:
        return ""
    try:
        return parsedate_to_datetime(value).date().isoformat()
    except (TypeError, ValueError, IndexError):
        pass
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).date().isoformat()
    except ValueError:
        m = re.match(r"\d{4}-\d{2}-\d{2}", value)
        return m.group(0) if m else ""


# ============================================================
# FEED PARSING
# ============================================================

def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1].lower()


def _child_text(entry: ET.Element, *names: str) -> str:
    for name in names:
        for child in entry:
            if _local(child.tag) == name:
                text = "".join(child.itertext()).strip()
                if text:
                    return text
    return ""


def _entry_link(entry: ET.Element) -> str:
    alternates = []
    for child in entry:
        if _local(child.tag) != "link":
            continue
        if child.get("href"):  # Atom
            if child.get("rel", "alternate") == "alternate":
                return child.get("href")
            alternates.append(child.get("href"))
        elif (child.text or "").strip():  # RSS / RDF
            return child.text.strip()
    return alternates[0] if alternates else ""


def parse_feed(data: bytes) -> list[dict]:
    """Parse RSS 2.0, Atom or RDF into dicts: key, title, url, date, summary."""
    try:
        root = ET.fromstring(data)
    except ET.ParseError:
        # Common publisher bug: bare '&' in titles/URLs. Escape and retry once.
        try:
            root = ET.fromstring(re.sub(rb"&(?!#?\w+;)", b"&amp;", data))
        except ET.ParseError as exc:
            entries = _parse_feed_leniently(data.decode("utf-8", errors="replace"))
            if entries:
                return entries
            raise SourceError(f"not a parseable feed: {exc}") from exc
    entries = []
    for el in root.iter():
        if _local(el.tag) not in ("item", "entry"):
            continue
        title = clean_text(_child_text(el, "title"), 300)
        url = _entry_link(el)
        guid = _child_text(el, "guid", "id") or url or title
        if not guid:
            continue
        entries.append({
            "key": md5(guid),
            "title": title,
            "url": url,
            "date": to_iso_date(_child_text(el, "pubdate", "published", "updated", "date")),
            "summary": clean_text(_child_text(el, "description", "summary", "encoded", "content")),
        })
    return entries


def _parse_feed_leniently(text: str) -> list[dict]:
    """Regex fallback for feeds that are not well-formed XML."""
    def tag(name: str, blob: str) -> str:
        pattern = rf"<{name}\b[^>]*>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</{name}>"
        m = re.search(pattern, blob, re.S | re.I)
        return m.group(1).strip() if m else ""

    entries = []
    for blob in re.findall(r"<item\b[^>]*>(.*?)</item>", text, re.S | re.I):
        url = clean_text(tag("link", blob), 500)
        guid = tag("guid", blob) or url
        if not guid:
            continue
        entries.append({
            "key": md5(guid),
            "title": clean_text(tag("title", blob), 300),
            "url": url,
            "date": to_iso_date(tag("pubDate", blob)),
            "summary": clean_text(tag("description", blob)),
        })
    return entries


class _LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[tuple[str, str]] = []
        self._href: str | None = None
        self._text: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self._href = dict(attrs).get("href")
            self._text = []

    def handle_data(self, data):
        if self._href is not None:
            self._text.append(data)

    def handle_endtag(self, tag):
        if tag == "a" and self._href is not None:
            self.links.append((self._href, clean_text("".join(self._text), 300)))
            self._href = None


def parse_links(page: str, base_url: str, link_pattern: str) -> list[dict]:
    """Unique links whose path matches link_pattern, with their anchor text."""
    parser = _LinkParser()
    parser.feed(page)
    found: dict[str, str] = {}
    for href, text in parser.links:
        absolute = urljoin(base_url, href).split("#", 1)[0].split("?", 1)[0].rstrip("/")
        if not re.search(link_pattern, urlparse(absolute).path, re.I):
            continue
        if absolute not in found or (text and not found[absolute]):
            found[absolute] = text
    return [{"key": url, "title": text or urlparse(url).path.rsplit("/", 1)[-1],
             "url": url, "date": "", "summary": ""} for url, text in found.items()]


# ============================================================
# DIFF
# ============================================================

def _item(source: dict, entry: dict, kind: str) -> dict:
    return {
        "source_id": source["id"],
        "type": kind,
        "id": entry["key"],
        "title": entry["title"] or "(untitled)",
        "url": entry["url"],
        "body_excerpt": entry["summary"],
        "release_date": entry["date"],
    }


def diff_entries(source: dict, entries: list[dict], sstate: dict, kind: str) -> list[dict]:
    """Return new entries as items and record them as seen.

    Entries filtered out by `include` or older than `max_age_days` are recorded
    as seen; new entries beyond
    `max_items` are left unseen so they are picked up on a later run.
    """
    # Legacy state: seen_guids (md5 of RSS guid) / seen_links (MIT AIRR paths).
    seen = set(sstate.get("seen", [])) | set(sstate.get("seen_guids", []))
    seeding = not seen and "seen" not in sstate

    group_re = re.compile(source["group_by"]) if source.get("group_by") else None
    groups: dict[str, list[dict]] = {}
    for entry in entries:
        gkey = entry["key"]
        if group_re:
            m = group_re.search(entry["url"]) or group_re.search(entry["key"])
            gkey = f"group:{m.group(1)}" if m else entry["key"]
        groups.setdefault(gkey, []).append(entry)

    include = re.compile(source["include"], re.I) if source.get("include") else None
    max_age = source.get("max_age_days", DEFAULT_MAX_AGE_DAYS)
    cutoff = (datetime.now(UTC) - timedelta(days=max_age)).date().isoformat()
    fresh: list[tuple[str, dict]] = []
    for gkey, members in groups.items():
        member_keys = {m["key"] for m in members}
        if gkey in seen or member_keys & seen:
            seen |= member_keys | {gkey}
            continue
        head = members[0]
        stale = bool(head["date"]) and head["date"] < cutoff
        if seeding or stale or (
            include and not include.search(f"{head['title']} {head['summary']}")
        ):
            seen |= member_keys | {gkey}
            continue
        fresh.append((gkey, head))

    fresh.sort(key=lambda pair: pair[1]["date"], reverse=True)
    cap = source.get("max_items", DEFAULT_MAX_ITEMS)
    emitted = fresh[:cap]
    if len(fresh) > cap:
        print(f"   ({len(fresh) - cap} more new item(s) deferred by max_items={cap})")
    for gkey, _head in emitted:
        seen |= {gkey} | {m["key"] for m in groups[gkey]}

    # Keep keys still present in the feed first, so trimming drops only old ones.
    live = {e["key"] for e in entries} | set(groups)
    sstate["seen"] = (sorted(seen & live) + sorted(seen - live))[:SEEN_KEYS_KEPT]
    sstate.pop("seen_guids", None)
    if seeding:
        print(f"   seeded state with {len(groups)} existing item(s); nothing emitted")
    return [_item(source, head, kind) for _, head in emitted]


# ============================================================
# SOURCE TYPES
# ============================================================

def poll_rss(source: dict, sstate: dict) -> list[dict]:
    entries = parse_feed(fetch_bytes(source["url"]))
    if not entries:
        raise SourceError("feed contained no entries")
    return diff_entries(source, entries, sstate, "rss_entry")


def poll_html_links(source: dict, sstate: dict) -> list[dict]:
    page = fetch_text(source["url"])
    entries = parse_links(page, source["url"], source["link_pattern"])
    if not entries:
        sample = sorted({urlparse(urljoin(source["url"], h)).path
                         for h in re.findall(r'href=["\']([^"\']+)', page)})
        raise SourceError(f"no links matched link_pattern (page layout changed?); page has "
                          f"{len(sample)} links, e.g. {sample[:8]}")
    return diff_entries(source, entries, sstate, "new_link")


def poll_file_watch(source: dict, sstate: dict) -> list[dict]:
    m = re.search(source["pattern"], fetch_text(source["url"]))
    if not m:
        raise SourceError("watched pattern not found")
    value = m.group(1).strip(" *_.`")  # drop markdown emphasis around the value
    previous = sstate.get("value")
    sstate["value"] = value
    if previous is None:
        print(f"   seeded value: {value!r}")
        return []
    if value == previous:
        return []
    return [{
        "source_id": source["id"],
        "type": "version_change",
        "id": md5(value),
        "title": f"{source['name']}: {previous} -> {value}",
        "url": source.get("item_url", source["url"]),
        "body_excerpt": f"{source['name']} now reports '{value}' (previously '{previous}').",
        "release_date": utc_now()[:10],
    }]


def poll_mit_airr(source: dict, sstate: dict) -> list[dict]:
    """MIT AIRR blog: diff post links, fetch each new post for title/excerpt."""
    index = fetch_text(source["url"])
    links: list[str] = []
    for link in re.findall(r'href=["\'](/blog/[a-z0-9][a-z0-9\-]+)["\']', index):
        if link not in links:
            links.append(link)
    if not links:
        raise SourceError("no blog post links found")

    if not sstate.get("seen_links"):
        sstate["seen_links"] = sorted(links)
        print(f"   seeded state with {len(links)} existing post(s); nothing emitted")
        return []
    seen = set(sstate["seen_links"])
    new_links = [link for link in links if link not in seen]
    items = []
    for link in new_links[: source.get("max_items", DEFAULT_MAX_ITEMS)]:
        url = f"https://airisk.mit.edu{link}"
        try:
            post = fetch_text(url)
        except SourceError:
            post = ""
        title_m = re.search(r"<h1[^>]*>(.*?)</h1>", post, re.S | re.I)
        title = clean_text(title_m.group(1), 300) if title_m else link
        excerpt = next(
            (clean_text(p) for p in re.findall(r"<p[^>]*>(.*?)</p>", post, re.S | re.I)
             if len(clean_text(p)) > 80),
            "New blog post. Check for taxonomy updates, new subdomains or dataset releases.",
        )
        date_m = re.search(r"\d{4}-\d{2}-\d{2}", post)
        items.append({
            "source_id": source["id"],
            "type": "blog_post",
            "id": link,
            "title": f"MIT AI Risk Repository: {title}",
            "url": url,
            "body_excerpt": excerpt,
            "release_date": date_m.group(0) if date_m else utc_now()[:10],
        })
        seen.add(link)
        time.sleep(1)
    sstate["seen_links"] = sorted(seen)[:SEEN_KEYS_KEPT]
    return items


POLLERS = {
    "rss": poll_rss,
    "html_links": poll_html_links,
    "file_watch": poll_file_watch,
    "mit_airr": poll_mit_airr,
}


def poll_source(source: dict, state: dict) -> list[dict]:
    """Poll one source, updating its state and health. Never raises."""
    sstate = state.setdefault(source["id"], {})
    health = sstate.setdefault("health", {"consecutive_failures": 0})
    try:
        items = POLLERS[source["type"]](source, sstate)
    except Exception as exc:
        health["consecutive_failures"] = health.get("consecutive_failures", 0) + 1
        health["last_error"] = str(exc)[:300]
        print(f"   [WARN] {source['id']}: {exc} "
              f"({health['consecutive_failures']} consecutive failure(s))")
        return []
    health.update(consecutive_failures=0, last_success=utc_now(), last_error=None)
    return items


def unhealthy_sources(state: dict) -> dict[str, dict]:
    return {
        s["id"]: state[s["id"]]["health"] for s in SOURCES
        if state.get(s["id"], {}).get("health", {}).get("consecutive_failures", 0)
        >= HEALTH_FAIL_THRESHOLD
    }


# ============================================================
# MAIN
# ============================================================

def main() -> None:
    state = load_state()

    if "--health-check" in sys.argv:
        bad = unhealthy_sources(state)
        for sid, health in bad.items():
            print(f"[health] {sid}: {health['consecutive_failures']} consecutive failures; "
                  f"last error: {health.get('last_error')}")
        if bad:
            print(f"[health] {len(bad)} source(s) failing — fix or replace their URLs "
                  f"in automation/monitoring/poll-sources.py")
            sys.exit(1)
        print("[health] all sources healthy")
        return

    print(f"[poll-sources] Starting run at {utc_now()}")
    all_new_items: list[dict] = []
    for source in SOURCES:
        print(f"\n── {source['name']} ({source['id']})")
        items = poll_source(source, state)
        print(f"   → {len(items)} new item(s)")
        all_new_items.extend(items)
        time.sleep(1)  # be polite to external servers

    output = {
        "run_date": utc_now()[:10],
        "run_timestamp": utc_now(),
        "total_new_items": len(all_new_items),
        "items": all_new_items,
        "source_health": {s["id"]: state[s["id"]]["health"] for s in SOURCES},
    }
    OUTPUT_FILE.write_text(json.dumps(output, indent=2) + "\n")
    save_state(state)

    failing = [sid for sid, h in output["source_health"].items() if h["consecutive_failures"]]
    print(f"\n[poll-sources] Complete. {len(all_new_items)} new item(s) across "
          f"{len(SOURCES)} sources; failing this run: {', '.join(failing) or 'none'}.")


if __name__ == "__main__":
    main()
