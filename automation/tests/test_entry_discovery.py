from pathlib import Path

import automation_engine
from automation_engine import AutomationOrchestrator


def test_gap_check_discovers_nested_mdx_files_and_canonical_ids(
    tmp_path: Path,
    monkeypatch,
) -> None:
    docs_path = tmp_path / "docs"
    reports_path = tmp_path / "reports"
    reports_path.mkdir()

    for domain, entries in [
        ("domain-a-technical", ["a1-hallucination.mdx", "a2-bias.mdx"]),
        ("domain-b-governance", ["b1-accountability.mdx"]),
    ]:
        domain_dir = docs_path / domain
        domain_dir.mkdir(parents=True)
        for entry_name in entries:
            (domain_dir / entry_name).write_text(
                "---\n"
                "title: test\n"
                "next_review: 2099-01-01\n"
                "---\n\n"
                "## Layer 1 — Executive card\n\n"
                "<Tabs>\n"
                '  <TabItem value="executive" label="Executive / Board">\n'
                "  Executive hook.\n"
                "  </TabItem>\n"
                '  <TabItem value="pm" label="Project Manager">\n'
                "  PM hook.\n"
                "  </TabItem>\n"
                '  <TabItem value="analyst" label="Security Analyst">\n'
                "  Analyst hook.\n"
                "  </TabItem>\n"
                "</Tabs>\n\n"
                "## Layer 2 — Practitioner overview\n\n"
                "### Risk description\n\n"
                "### Likelihood drivers\n- One\n\n"
                "### Consequence types\n| Type | Example |\n|---|---|\n| A | B |\n\n"
                "### Affected functions\nTechnology\n\n"
                "### Controls summary\n\n"
                "| Control | Owner | Effort | Go-live? | Definition of done |\n"
                "|---|---|---|---|---|\n"
                "| Test | Technology | Low | Required | Done |\n\n"
                "## Layer 3 — Controls detail\n\n"
                "### A1-001 — Example control\n\n"
                "## Layer 4 — Technical implementation\n\n"
                "```python\nprint('ok')\n```\n\n"
                "## Incident examples\n\n"
                "**Example incident:** Example.\n",
            )

    (docs_path / "how-to-use.md").write_text("# How to use")

    monkeypatch.setattr(automation_engine, "KNOWLEDGE_BASE_PATH", docs_path)
    monkeypatch.setattr(automation_engine, "REPORTS_PATH", reports_path)

    orchestrator = AutomationOrchestrator(require_api=False)
    run = orchestrator.run(mode="gap-check")

    assert sorted(run.entries_processed) == ["A1", "A2", "B1"]


def test_parse_entry_id_from_hyphenated_filename() -> None:
    path = Path("docs/domain-a-technical/a1-hallucination.mdx")
    assert automation_engine.parse_entry_id(path) == "A1"
