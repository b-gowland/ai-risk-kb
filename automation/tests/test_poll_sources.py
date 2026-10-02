"""Feed parsing, diffing, seeding/migration and health tracking in poll-sources.py."""
# ruff: noqa: E501  (XML/HTML fixtures below keep realistic single-line entries)
import importlib.util
import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

POLL = Path(__file__).resolve().parents[1] / 'monitoring' / 'poll-sources.py'
spec = importlib.util.spec_from_file_location('poll_sources', POLL)
poll = importlib.util.module_from_spec(spec)
spec.loader.exec_module(poll)

RSS = b"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel><title>t</title>
<item><title>Report A &amp; more</title>
 <link>https://incidentdatabase.ai/cite/7#1</link><guid>https://incidentdatabase.ai/cite/7#1</guid><pubDate>Sun, 27 Sep 2026 10:00:00 GMT</pubDate>
 <description><![CDATA[<p>First <b>report</b></p>]]></description></item>
<item><title>Report B</title><link>https://incidentdatabase.ai/cite/7#2</link>
 <guid>https://incidentdatabase.ai/cite/7#2</guid><pubDate>Mon, 28 Sep 2026 10:00:00 GMT</pubDate></item>
<item><title>Report C</title><link>https://incidentdatabase.ai/cite/9#3</link>
 <guid>https://incidentdatabase.ai/cite/9#3</guid><pubDate>Tue, 29 Sep 2026 10:00:00 GMT</pubDate></item>
</channel></rss>"""

ATOM = b"""<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
<entry xml:lang="en"><id>tag:github.com,2008:Repository/1/v2026.09</id>
 <title>v2026.09</title>
 <link rel="alternate" type="text/html" href="https://github.com/mitre-atlas/atlas-data/releases/tag/v2026.09"/>
 <updated>2026-09-14T00:00:00Z</updated><content type="html">&lt;p&gt;New techniques&lt;/p&gt;</content></entry>
</feed>"""

RDF = b"""<?xml version="1.0"?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns="http://purl.org/rss/1.0/"
 xmlns:dc="http://purl.org/dc/elements/1.1/">
<item rdf:about="https://example.org/a"><title>RDF item</title><link>https://example.org/a</link>
 <dc:date>2026-09-01</dc:date></item></rdf:RDF>"""

PAGE = """<html><body>
<a href="/news-and-publications/apra-letter-on-artificial-intelligence">APRA letter on AI</a>
<a href="/news-and-publications/annual-report/?utm=x">Annual report</a>
<a href="/about">About</a>
<a href="https://www.apra.gov.au/news-and-publications/apra-letter-on-artificial-intelligence#x"></a>
</body></html>"""


def test_parse_rss_atom_rdf():
    rss = poll.parse_feed(RSS)
    assert [e['title'] for e in rss] == ['Report A & more', 'Report B', 'Report C']
    assert rss[0]['date'] == '2026-09-27'
    assert rss[0]['summary'] == 'First report'
    (atom,) = poll.parse_feed(ATOM)
    assert atom['url'].endswith('/tag/v2026.09')
    assert atom['date'] == '2026-09-14'
    assert atom['summary'] == 'New techniques'
    (rdf,) = poll.parse_feed(RDF)
    assert (rdf['title'], rdf['date']) == ('RDF item', '2026-09-01')


def test_unparseable_feed_is_a_source_error():
    with pytest.raises(poll.SourceError):
        poll.parse_feed(b'<html><body>not a feed')


def test_first_run_seeds_without_emitting_then_emits_new():
    source = {'id': 's', 'name': 'S', 'max_age_days': 36500}
    entries = poll.parse_feed(RSS)
    sstate = {}
    assert poll.diff_entries(source, entries[:2], sstate, 'rss_entry') == []
    new = poll.diff_entries(source, entries, sstate, 'rss_entry')
    assert [i['title'] for i in new] == ['Report C']
    assert poll.diff_entries(source, entries, sstate, 'rss_entry') == []


def test_group_by_collapses_reports_and_migrates_legacy_guids():
    source = {'id': 'aiid', 'name': 'AIID', 'group_by': r'/cite/(\d+)', 'max_age_days': 36500}
    entries = poll.parse_feed(RSS)
    # Legacy state: md5 of report guids already seen for incident 7 only.
    sstate = {'seen_guids': [poll.md5('https://incidentdatabase.ai/cite/7#1')]}
    new = poll.diff_entries(source, entries, sstate, 'rss_entry')
    assert [i['title'] for i in new] == ['Report C']  # incident 7 already known
    assert 'seen_guids' not in sstate and 'group:9' in sstate['seen']


def test_include_filter_and_max_items_defer_overflow():
    entries = [{'key': str(i), 'title': f'AI item {i}', 'url': '', 'summary': '',
                'date': f'2026-09-{10 + i}'} for i in range(4)]
    entries.append({'key': 'x', 'title': 'Annual report', 'url': '', 'summary': '', 'date': ''})
    source = {'id': 's', 'name': 'S', 'include': poll.AI_KW, 'max_items': 2,
              'max_age_days': 36500}
    sstate = {'seen': []}
    first = poll.diff_entries(source, entries, sstate, 'rss_entry')
    assert [i['title'] for i in first] == ['AI item 3', 'AI item 2']  # newest first
    second = poll.diff_entries(source, entries, sstate, 'rss_entry')
    assert [i['title'] for i in second] == ['AI item 1', 'AI item 0']  # deferred, not lost


def test_parse_links_filters_dedupes_and_keeps_anchor_text():
    links = poll.parse_links(PAGE, 'https://www.apra.gov.au/news-and-publications',
                             r'^/news-and-publications/[a-z0-9-]+$')
    assert [(link['title'], link['url']) for link in links] == [
        ('APRA letter on AI',
         'https://www.apra.gov.au/news-and-publications/apra-letter-on-artificial-intelligence'),
        ('Annual report', 'https://www.apra.gov.au/news-and-publications/annual-report'),
    ]


def test_file_watch_seeds_then_reports_change(monkeypatch):
    source = {'id': 'owasp_llm', 'name': 'OWASP LLM Top 10', 'type': 'file_watch',
              'url': 'u', 'pattern': r'Current release:\s*([^\n]+)'}
    readme = {'text': 'Current release: 2025\n'}
    monkeypatch.setattr(poll, 'fetch_text', lambda url, timeout=30: readme['text'])
    sstate = {}
    assert poll.poll_file_watch(source, sstate) == []
    readme['text'] = '**Current release: 2026 — published August 4, 2026.**\n'
    (item,) = poll.poll_file_watch(source, sstate)
    assert item['title'] == 'OWASP LLM Top 10: 2025 -> 2026 — published August 4, 2026'


def test_health_tracking_and_health_check(monkeypatch, tmp_path):
    source = {'id': 'dead', 'name': 'Dead', 'type': 'rss', 'url': 'u'}
    monkeypatch.setattr(poll, 'SOURCES', [source])
    monkeypatch.setattr(poll, 'fetch_bytes', lambda url, timeout=30: b'<html>moved</html>')
    state = {}
    for _ in range(poll.HEALTH_FAIL_THRESHOLD):
        assert poll.poll_source(source, state) == []
    health = state['dead']['health']
    assert health['consecutive_failures'] == poll.HEALTH_FAIL_THRESHOLD
    assert 'feed' in health['last_error']

    state_file = tmp_path / 'state.json'
    state_file.write_text(json.dumps(state))
    monkeypatch.setattr(poll, 'STATE_FILE', state_file)
    monkeypatch.setattr(poll.sys, 'argv', ['poll-sources.py', '--health-check'])
    with pytest.raises(SystemExit) as excinfo:
        poll.main()
    assert excinfo.value.code == 1

    monkeypatch.setattr(poll, 'fetch_bytes', lambda url, timeout=30: RSS)
    poll.poll_source(source, state)
    assert state['dead']['health']['consecutive_failures'] == 0


def test_registry_is_well_formed():
    ids = [s['id'] for s in poll.SOURCES]
    assert len(ids) == len(set(ids))
    for s in poll.SOURCES:
        assert s['type'] in poll.POLLERS
        assert s['url'].startswith('https://')
        if s['type'] == 'html_links':
            assert s['link_pattern'].startswith('^/')


def test_stale_entries_are_marked_seen_not_emitted():
    today = datetime.now(UTC).date()
    entries = [
        {'key': 'old', 'title': 'Old', 'url': '', 'summary': '',
         'date': (today - timedelta(days=poll.DEFAULT_MAX_AGE_DAYS + 5)).isoformat()},
        {'key': 'new', 'title': 'New', 'url': '', 'summary': '',
         'date': (today - timedelta(days=1)).isoformat()},
    ]
    sstate = {'seen': []}
    items = poll.diff_entries({'id': 's', 'name': 'S'}, entries, sstate, 'rss_entry')
    assert [i['title'] for i in items] == ['New']
    assert 'old' in sstate['seen']


def test_feed_with_bare_ampersand_is_recovered():
    feed = b'<rss><channel><item><title>AI & you</title><link>https://x/?a=1&b=2</link></item></channel></rss>'
    (entry,) = poll.parse_feed(feed)
    assert entry['title'] == 'AI & you'
    assert entry['url'] == 'https://x/?a=1&b=2'


def test_malformed_feed_falls_back_to_lenient_parser():
    feed = (b'<rss><channel><item><title>AI rules</title><link>https://x/a</link>'
            b'<description>line<br>break</description><pubDate>Mon, 28 Sep 2026 10:00:00 GMT</pubDate>'
            b'</item></channel></rss>')
    (entry,) = poll.parse_feed(feed)
    assert (entry['title'], entry['url'], entry['date']) == ('AI rules', 'https://x/a', '2026-09-28')
