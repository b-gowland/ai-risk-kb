# Citation ledger (Tier 0)

Deterministic guard against the enumerable-fact failure mode — the one where a
framework ID (a MITRE ATLAS technique, an OWASP LLM entry, an EU AI Act article)
is cited confidently and *wrongly*, because it was written from memory rather
than checked. This is the failure class behind KB Issue #19 and the F-1 scenario
error (`AML.T0054` cited as indirect prompt injection when T0054 = LLM Jailbreak).

No LLM is involved. A YAML registry of verified IDs (`citation-ledger.yaml`) plus
an exact-match checker (`check_citations.py`). It is the cheapest, highest-yield
layer of the verification architecture in `AUTOMATION_VISION.md` (build step 0).

## Principle: checker, never oracle

Every ledger entry is `verified` (confirmed against a named authoritative source)
or `cannot_verify` (could not be confirmed — flagged for a human, **never given a
guessed value**). The ledger never asserts a value it cannot source. That is the
whole point: the tool that prevents Issue #19 must not reproduce it internally.

## What it checks

Two corpora, one ledger:
- **KB** (`ai-risk-kb/docs/**/*.mdx`) — parses `framework-chip` spans.
- **Scenarios** (`ai-risk-training/src/scenarios/*.js`) — parses `regulatory_tags`
  and framework IDs cited in prose.

Per-citation verdicts:
| Verdict | Meaning |
|---|---|
| `OK` | ID known; no name asserted, or asserted name matches the ledger. |
| `NAME_MISMATCH` | ID verified, but the asserted name disagrees — the F-1 class. |
| `CANNOT_VERIFY` | ID in ledger but value unconfirmed; human must check the source. |
| `UNKNOWN_ID` | ID not in the ledger — a typo, or the ledger needs extending. |

## Usage

```bash
pip install pyyaml

# advisory (report only, always exits 0):
python3 check_citations.py --ledger citation-ledger.yaml \
    ../../docs                       # KB
python3 check_citations.py --ledger citation-ledger.yaml \
    /path/to/ai-risk-training/src/scenarios   # scenarios (point at a local clone)

# enforce (exit 1 on NAME_MISMATCH or UNKNOWN_ID) — only once false-positives are known low:
python3 check_citations.py --ledger citation-ledger.yaml --strict ../../docs

# F-1 regression self-test:
python3 check_citations.py --self-test
```

## Advisory first (deliberate)

Ships in **advisory mode**: it reports, it does not block. Per the
`AUTOMATION_VISION` anti-pattern "don't ship blocking on day one" — validate on
real output first, then flip the CI workflow to `--strict` once the
false-positive rate is known. Nothing here auto-edits content.

## Extending / refreshing the ledger

- **New ID appears as `UNKNOWN_ID`** → verify its canonical value against the
  authoritative source, add it with `status: verified` and the source.
- **Refresh** (e.g. after an OWASP/ATLAS release) → re-verify, bump `verified_on`.
- Prefer citing **stable parent IDs** in prose (e.g. `AML.T0051`, not a volatile
  `.001` sub-ID); pin the precise sub-ID in the ledger where it can be checked.

## Open human-check flags from the first run (2026-06-28)

The checker is clean on name-consistency (0 `NAME_MISMATCH` across both corpora,
confirming the F-1 fix held). Two `CANNOT_VERIFY` flags need a human:

1. **`eu-ai-act article-29`** in `f2-shadow-ai.mdx` — cited as deployer
   obligations, but deployers are **Article 26**. Likely a miscitation; verify.
2. **`AML.T0054.003`** in `c2-prompt-injection.mdx` — a Jailbreak sub-technique
   whose name could not be confirmed this cycle. Check the live ATLAS matrix.

## Known limitations (prototype)

- The `.mdx` parser keys on `framework-chip` spans and AI-Act-labelled chips; a
  chip that *mixes* frameworks (e.g. "EU AI Act Art. 26 / GDPR Art. 29" in one
  span) could misattribute a number. Hardening: split mixed chips, or scope the
  Act-article regex to the substring after "EU AI Act".
- NIST AI RMF subcategory **titles** are not pinned — the checker confirms the
  function (govern/map/measure/manage) is valid and leaves subcategory-title
  verification to a human.
- The ledger is seeded to IDs **actually cited** across the two corpora, not the
  full frameworks. `UNKNOWN_ID` is the signal to extend it.
