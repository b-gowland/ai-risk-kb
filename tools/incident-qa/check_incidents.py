#!/usr/bin/env python3
"""Wording and sourcing check for the "## Incident examples" sections.

Deterministic, no model involved. For every paragraph under an entry's
"## Incident examples" heading it reports:

  CLOSER     an aphorism-style closer or contrast ("The lesson:", "is not a
             control until", "not X but Y", "isn't X. It's Y").
  NO_SOURCE  the paragraph does not end with a dated source in parentheses,
             for example "(AP reporting, September 2026)".

Warning-only by default: it prints every hit and exits 0, because existing
entries have hits (when it was added in November 2026: 2 closers, and 53 of
107 paragraphs without a closing dated source). Pass --strict to exit 1 on
any hit once they are cleared.

Usage:
  python3 tools/incident-qa/check_incidents.py docs
  python3 tools/incident-qa/check_incidents.py --strict docs
  python3 tools/incident-qa/check_incidents.py --self-test
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

HEADING = re.compile(r"^##\s+Incident examples\s*$", re.IGNORECASE)
SECTION_END = re.compile(r"^(#{1,2}\s|---\s*$)")

CLOSER_PATTERNS = [
    ("lesson-label", re.compile(r"\bThe (lesson|takeaway|moral|point|upshot)( here)?:", re.IGNORECASE)),
    ("not-a-control-until", re.compile(r"\bis not a control until\b", re.IGNORECASE)),
    ("not-x-but-y", re.compile(r"\bnot (?:just |merely |simply |only )?[^,.;:()]{1,40},? but (?:rather )?(?:a |an |the )?\w", re.IGNORECASE)),
    ("isnt-x-its-y", re.compile(r"\b(?:is not|isn't|was not|wasn't) [^.]{1,80}\.\s+(?:It|This|That)(?: is|'s| was)\b", re.IGNORECASE)),
]

# A dated source in parentheses at the very end of the paragraph: the last
# parenthesised group must contain a year from 1900 to 2099.
TRAILING_PARENS = re.compile(r"\(([^()]*(?:\([^()]*\)[^()]*)*)\)[.\s]*$")
YEAR = re.compile(r"\b(19|20)\d{2}\b")


def incident_paragraphs(text: str):
    """Yield (line_number, paragraph) for each paragraph in incident sections."""
    lines = text.splitlines()
    inside = False
    buf: list[str] = []
    start = 0
    for i, line in enumerate(lines, 1):
        if HEADING.match(line):
            inside = True
            buf = []
            continue
        if not inside:
            continue
        if SECTION_END.match(line):
            if buf:
                yield start, " ".join(buf)
            inside = False
            buf = []
            continue
        if line.strip():
            if not buf:
                start = i
            buf.append(line.strip())
        elif buf:
            yield start, " ".join(buf)
            buf = []
    if inside and buf:
        yield start, " ".join(buf)


def check_paragraph(para: str) -> list[tuple[str, str]]:
    hits = []
    for name, pat in CLOSER_PATTERNS:
        m = pat.search(para)
        if m:
            hits.append(("CLOSER", f"{name}: \"{m.group(0)}\""))
    m = TRAILING_PARENS.search(para)
    if not m or not YEAR.search(m.group(1)):
        hits.append(("NO_SOURCE", "does not end with a dated source in parentheses"))
    return hits


def check_tree(root: Path):
    results = []
    files = sorted(root.rglob("*.mdx")) + sorted(root.rglob("*.md")) if root.is_dir() else [root]
    for path in files:
        for line, para in incident_paragraphs(path.read_text(encoding="utf-8")):
            for kind, detail in check_paragraph(para):
                results.append((path, line, kind, detail))
    return results


def self_test() -> int:
    good = "**X (2024):** Something happened. (Court record, March 2024)"
    cases = {
        good: [],
        good + "\n": [],
        "**X:** Something happened. The lesson: check things. (Reuters, 2024)": ["CLOSER"],
        "**X:** A policy is not a control until someone enforces it. (Reuters, 2024)": ["CLOSER"],
        "**X:** The failure was not technical, but organisational. (Reuters, 2024)": ["CLOSER"],
        "**X:** The gap isn't the model. It's the process. (Reuters, 2024)": ["CLOSER"],
        "**X:** Something happened.": ["NO_SOURCE"],
        "**X:** Something happened. (Reuters)": ["NO_SOURCE"],
        "**X:** Something (in 2020) happened and ended badly.": ["NO_SOURCE"],
        "**X:** Something happened. (Moffatt v. Air Canada, 2024 BCCRT 149; CBC News, February 2024)": [],
    }
    failed = 0
    for para, want in cases.items():
        got = sorted({k for k, _ in check_paragraph(para.strip())})
        if got != sorted(want):
            print(f"SELF-TEST FAIL: {para!r}: want {want}, got {got}")
            failed += 1
    doc = "## Incident examples\n\n**A (2024):** x. (Src, 2024)\n\n**B:** y.\n\n---\n\n## Next\n\nOutside.\n"
    paras = list(incident_paragraphs(doc))
    if [p for _, p in paras] != ["**A (2024):** x. (Src, 2024)", "**B:** y."]:
        print(f"SELF-TEST FAIL: section parsing gave {paras}")
        failed += 1
    print("self-test:", "FAIL" if failed else "OK")
    return 1 if failed else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="*", default=["docs"])
    ap.add_argument("--strict", action="store_true", help="exit 1 on any hit")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return self_test()

    results = []
    for p in args.paths:
        results += check_tree(Path(p))
    for path, line, kind, detail in results:
        print(f"{kind:9} {path}:{line}  {detail}")
    closers = sum(1 for r in results if r[2] == "CLOSER")
    unsourced = sum(1 for r in results if r[2] == "NO_SOURCE")
    print(f"\nIncident QA: {closers} closer hit(s), {unsourced} paragraph(s) without a closing dated source.")
    if results and args.strict:
        print("STRICT: failing")
        return 1
    if results:
        print("Warning only (run with --strict to fail on hits).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
