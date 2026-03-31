def test_sample_fixture_has_expected_sections(sample_mdx_entry: str) -> None:
    assert "## Layer 1 — Executive card" in sample_mdx_entry
    assert "## Layer 2 — Practitioner overview" in sample_mdx_entry
    assert "## Incident examples" in sample_mdx_entry
