from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_mdx_entry() -> str:
    """Return content of a trimmed MDX entry for testing."""
    return (FIXTURES_DIR / "sample_entry.mdx").read_text()


@pytest.fixture
def sample_mdx_path(tmp_path: Path, sample_mdx_entry: str) -> Path:
    """Write a sample MDX entry to a temp directory mimicking the real layout."""
    entry_dir = tmp_path / "docs" / "domain-a-technical"
    entry_dir.mkdir(parents=True)
    entry_file = entry_dir / "a1-hallucination.mdx"
    entry_file.write_text(sample_mdx_entry)
    return entry_file
