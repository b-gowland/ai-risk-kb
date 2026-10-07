"""Replay publisher-linked AIID reports without duplicate tasks or lost evidence."""

from monitoring.review_report import generate_report, group_results, incident_key, link


def item(item_id, incident="1724", source="aiid"):
    return {"id": item_id, "source_id": source, "title": f"Article {item_id}",
            "url": f"https://publisher.example/{item_id}",
            "body_excerpt": f"Report (https://incidentdatabase.ai/cite/{incident}#8030)"}


def result(item_id, action="UPDATE_ENTRY"):
    return {"item_id": item_id, "action": action, "item_title": "Model title",
            "recommended_action": f"Review {item_id}", "evidence_quote": f"Evidence {item_id}",
            "kb_matches": [{"kb_id": "A1", "confidence": "high", "rationale": "Reason"}]}


def test_publisher_urls_group_by_incident_in_excerpt_and_preserve_sources(tmp_path):
    items = [item("a"), item("b"), item("c", incident="99")]
    results = [result("a"), result("b"), result("c")]
    report = generate_report("2099-01-01", items, results, {"aiid": 3}, docs_dir=tmp_path)
    assert "Review groups requiring action:** 2" in report
    assert report.count("### Article") == 2
    for source in items:
        assert source["url"] in report
        assert f"Evidence {source['id']}" in report
        assert f"Review {source['id']}" in report


def test_no_action_cannot_hide_conflicting_update(tmp_path):
    report = generate_report("2099-01-01", [item("a"), item("b")],
                             [result("a", "NO_ACTION"), result("b")], {}, docs_dir=tmp_path)
    assert "Review groups requiring action:** 1" in report
    assert "## 🟡 Update existing entry" in report
    assert "Recommendation (NO\\_ACTION)" in report
    assert "https://publisher.example/a" in report


def test_unrelated_or_ambiguous_reports_are_not_merged():
    items = [item("a", source="other"), item("b", source="other")]
    assert len(group_results(items, [result("a"), result("b")])) == 2
    ambiguous = item("c")
    ambiguous["body_excerpt"] += " https://incidentdatabase.ai/cite/99"
    assert incident_key(ambiguous) is None
    assert incident_key(item("d", incident="1724garbage")) is None


def test_incomplete_run_lists_unclassified_sources_instead_of_claiming_clean(tmp_path):
    report = generate_report("2099-01-01", [item("a"), item("b")],
                             [result("a", "NO_ACTION")], {}, docs_dir=tmp_path)
    assert "Items received:** 2" in report
    assert "Items reviewed:** 1" in report
    assert "Incomplete classification" in report
    assert "https://publisher.example/b" in report
    assert "does not establish that no updates are needed" in report


def test_failed_source_with_no_items_does_not_claim_clean(tmp_path):
    report = generate_report("2099-01-01", [], [], {},
                             {"nist": {"consecutive_failures": 2, "last_error": "timeout"}},
                             docs_dir=tmp_path)
    assert "timeout" in report
    assert "Review is incomplete" in report


def test_existing_framework_edition_is_visible_without_suppressing_action(tmp_path):
    entry_dir = tmp_path / "domain-a-technical"
    entry_dir.mkdir()
    (entry_dir / "a1-test.mdx").write_text(
        "Introduction\n" + "Unrelated content.\n" * 300 + "OWASP LLM Top 10 (2026) is cited here.\n"
    )
    source = {**item("a", source="owasp_llm"), "title": "OWASP LLM Top 10 2026 published"}
    report = generate_report("2099-01-01", [source], [result("a")], {}, docs_dir=tmp_path)
    assert "OWASP LLM Top 10 (2026) is cited here." in report
    assert "a1-test.mdx#L302" in report
    assert "Items requiring action:** 1" in report
    assert "not a finding that the item is already covered" in report


def test_source_links_cannot_insert_markup_or_unsafe_schemes():
    assert "javascript:" not in link("Read", "javascript:alert(1)")
    assert "%29" in link("Read", "https://example.org/a)bad")
    assert "\\[fake\\]" in link("[fake]", "https://example.org")

