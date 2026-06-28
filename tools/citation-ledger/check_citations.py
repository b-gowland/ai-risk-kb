#!/usr/bin/env python3
"""
check_citations.py — Tier-0 deterministic citation checker for AI Risk Practice.

Scans content for enumerable framework IDs (MITRE ATLAS techniques, OWASP LLM
Top 10, EU AI Act articles/annexes, ISO 42001 clauses, NIST AI RMF functions)
and verifies each against citation-ledger.yaml. No LLM in the loop.

Per-citation verdicts:
  OK            — ID known; no name asserted alongside it, or name matches ledger.
  NAME_MISMATCH — ID known and verified, but the asserted name disagrees with the
                  ledger. THIS IS THE F-1 CLASS (e.g. AML.T0054 labelled
                  "indirect prompt injection" when T0054 = "LLM Jailbreak").
  CANNOT_VERIFY — ID is in the ledger but its value was never confirmed; a human
                  must check it against the primary source.
  UNKNOWN_ID    — ID not in the ledger at all (typo, or ledger needs extending).

Exit code: 0 by default (ADVISORY — report only). With --strict, exit 1 if any
NAME_MISMATCH or UNKNOWN_ID is found. CANNOT_VERIFY never fails the build; it is
a standing human-review flag.

Usage:
  python3 check_citations.py --ledger citation-ledger.yaml PATH [PATH ...]
  python3 check_citations.py --ledger citation-ledger.yaml --strict ../../docs ../scenarios
  python3 check_citations.py --self-test          # runs the F-1 regression fixture
"""

import argparse
import os
import re
import sys

try:
    import yaml
except ImportError:
    sys.stderr.write("ERROR: PyYAML required. Install with: pip install pyyaml\n")
    sys.exit(2)

ROMAN = {"i": "i", "ii": "ii", "iii": "iii", "iv": "iv", "v": "v",
         "vi": "vi", "vii": "vii", "viii": "viii", "ix": "ix", "x": "x"}

# ---- ID extraction patterns -------------------------------------------------

RE_ATLAS   = re.compile(r"AML\.T\d{4}(?:\.\d{3})?")
RE_OWASP   = re.compile(r"\bLLM\d{2}\b")
RE_ART     = re.compile(r"(?:Article|Art\.?)\s*(\d+)", re.IGNORECASE)
RE_ANNEX   = re.compile(r"Annex\s+([IVXLC]+)", re.IGNORECASE)
RE_TAG_ART = re.compile(r"eu-ai-act-article-(\d+)")
RE_TAG_ANX = re.compile(r"eu-ai-act-annex-([ivxlc]+)")
RE_TAG_ISO = re.compile(r"iso-42001-(\d+)")
RE_TAG_NIST= re.compile(r"nist-ai-rmf-(govern|map|measure|manage)-[\d.]+")
RE_CHIP    = re.compile(r'framework-chip">([^<]+)</span>')


def norm(s):
    return re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).strip()


def name_matches(asserted, ledger_entry):
    """True if an asserted name is consistent with the ledger's canonical name
    or any alias. Lenient: subset match in either direction counts (handles
    'Indirect Prompt Injection' vs 'LLM Prompt Injection: Indirect')."""
    a = norm(asserted)
    if not a:
        return True  # no name asserted -> nothing to contradict
    candidates = [ledger_entry.get("name")] + (ledger_entry.get("aliases") or [])
    for c in candidates:
        c = norm(c)
        if not c:
            continue
        if a == c or a in c or c in a:
            return True
        # token-overlap fallback: majority of the shorter side's words present
        aw, cw = set(a.split()), set(c.split())
        if aw and cw:
            overlap = len(aw & cw) / min(len(aw), len(cw))
            if overlap >= 0.6:
                return True
    return False


# ---- citation model ---------------------------------------------------------

class Cite:
    def __init__(self, framework, cid, asserted_name, where):
        self.framework = framework
        self.cid = cid
        self.asserted_name = asserted_name
        self.where = where


def extract_from_chip(inner, where):
    """Parse one KB framework-chip's inner text into citations."""
    out = []
    if "MITRE ATLAS" in inner or RE_ATLAS.search(inner):
        for m in RE_ATLAS.finditer(inner):
            name = inner[m.end():].strip(" :-—|")
            out.append(Cite("mitre-atlas", m.group(0), name, where))
    if "OWASP" in inner.upper():
        for m in RE_OWASP.finditer(inner):
            name = inner[m.end():].strip(" :-—|")
            out.append(Cite("owasp-llm", m.group(0), name, where))
    if "EU AI ACT" in inner.upper() or "AI ACT" in inner.upper():
        for m in RE_ART.finditer(inner):
            out.append(Cite("eu-ai-act", "article-%s" % m.group(1), "", where))
        for m in RE_ANNEX.finditer(inner):
            out.append(Cite("eu-ai-act", "annex-%s" % m.group(1).lower(), "", where))
    return out


def extract_mdx(text, where):
    out = []
    for m in RE_CHIP.finditer(text):
        out.extend(extract_from_chip(m.group(1), where))
    # ATLAS IDs in prose outside chips (F-1 lives in prose)
    in_chip = set()
    for m in RE_CHIP.finditer(text):
        in_chip.update(range(m.start(), m.end()))
    for m in RE_ATLAS.finditer(text):
        if m.start() in in_chip:
            continue
        # capture a short trailing window as a possible asserted name
        tail = text[m.end():m.end() + 60]
        name = ""
        low = tail.lower()
        if "injection" in low or "jailbreak" in low or "poison" in low:
            name = tail.strip()
        out.append(Cite("mitre-atlas", m.group(0), name, where))
    return out


def extract_js(text, where):
    """Training scenarios: regulatory_tags + ATLAS IDs cited in prose."""
    out = []
    for m in RE_TAG_ART.finditer(text):
        out.append(Cite("eu-ai-act", "article-%s" % m.group(1), "", where))
    for m in RE_TAG_ANX.finditer(text):
        out.append(Cite("eu-ai-act", "annex-%s" % m.group(1), "", where))
    for m in RE_TAG_ISO.finditer(text):
        out.append(Cite("iso-42001", "clause-%s" % m.group(1), "", where))
    for m in RE_TAG_NIST.finditer(text):
        out.append(Cite("nist-ai-rmf", m.group(1), "", where))
    for m in RE_ATLAS.finditer(text):
        tail = text[m.end():m.end() + 70]
        low = tail.lower()
        name = tail.strip() if ("injection" in low or "jailbreak" in low) else ""
        out.append(Cite("mitre-atlas", m.group(0), name, where))
    for m in RE_OWASP.finditer(text):
        out.append(Cite("owasp-llm", m.group(0), "", where))
    return out


# ---- checking ---------------------------------------------------------------

def lookup(led, framework, cid):
    block = led.get(framework, {})
    if framework == "nist-ai-rmf":
        return block.get("functions", {}).get(cid)
    return block.get("ids", {}).get(cid)


def check_cite(c, led):
    entry = lookup(led, c.framework, c.cid)
    if entry is None:
        return "UNKNOWN_ID", "%s %s not in ledger" % (c.framework, c.cid)
    if entry.get("status") == "cannot_verify":
        return "CANNOT_VERIFY", entry.get("note", "unverified — check primary source")
    if c.asserted_name and not name_matches(c.asserted_name, entry):
        return "NAME_MISMATCH", "cited as '%s' but ledger says '%s'" % (
            c.asserted_name[:50], entry.get("name"))
    return "OK", entry.get("name")


def gather(paths):
    cites = []
    for p in paths:
        for root, _, files in os.walk(p):
            for fn in files:
                fp = os.path.join(root, fn)
                try:
                    text = open(fp, encoding="utf-8").read()
                except Exception:
                    continue
                if fn.endswith(".mdx") or fn.endswith(".md"):
                    cites += extract_mdx(text, fp)
                elif fn.endswith(".js") or fn.endswith(".jsx"):
                    cites += extract_js(text, fp)
    return cites


def run(ledger_path, paths, strict):
    led = yaml.safe_load(open(ledger_path, encoding="utf-8"))
    cites = gather(paths)
    buckets = {"OK": [], "NAME_MISMATCH": [], "CANNOT_VERIFY": [], "UNKNOWN_ID": []}
    for c in cites:
        verdict, detail = check_cite(c, led)
        buckets[verdict].append((c, detail))

    print("== Citation ledger check ==")
    print("scanned %d citation(s) across %d path(s)\n" % (len(cites), len(paths)))
    for v in ("NAME_MISMATCH", "UNKNOWN_ID", "CANNOT_VERIFY"):
        if buckets[v]:
            print("%s (%d):" % (v, len(buckets[v])))
            for c, detail in buckets[v]:
                print("  - %s %s  [%s]\n      %s" % (
                    c.framework, c.cid, os.path.relpath(c.where), detail))
            print()
    print("OK: %d   NAME_MISMATCH: %d   UNKNOWN_ID: %d   CANNOT_VERIFY: %d" % (
        len(buckets["OK"]), len(buckets["NAME_MISMATCH"]),
        len(buckets["UNKNOWN_ID"]), len(buckets["CANNOT_VERIFY"])))

    fail = bool(buckets["NAME_MISMATCH"] or buckets["UNKNOWN_ID"])
    if strict and fail:
        print("\nSTRICT: failing build on mismatch/unknown id.")
        return 1
    if fail:
        print("\nADVISORY: issues found above (build not failed; re-run with --strict to enforce).")
    return 0


SELF_TEST_FIXTURE = (
    "tools/citation-ledger/fixtures/f1_regression.mdx")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="*")
    ap.add_argument("--ledger", default=os.path.join(
        os.path.dirname(__file__), "citation-ledger.yaml"))
    ap.add_argument("--strict", action="store_true")
    ap.add_argument("--self-test", action="store_true",
                    help="Run the F-1 regression fixture; expects a NAME_MISMATCH.")
    args = ap.parse_args()

    if args.self_test:
        fx = os.path.join(os.path.dirname(__file__), "fixtures", "f1_regression.mdx")
        led = yaml.safe_load(open(args.ledger, encoding="utf-8"))
        cites = extract_mdx(open(fx, encoding="utf-8").read(), fx)
        verdicts = [check_cite(c, led)[0] for c in cites]
        print("self-test verdicts:", verdicts)
        if "NAME_MISMATCH" in verdicts:
            print("PASS — checker catches the F-1 class (T0054 mislabelled as indirect injection).")
            return 0
        print("FAIL — regression fixture did not trip a NAME_MISMATCH.")
        return 1

    if not args.paths:
        ap.error("provide one or more paths, or use --self-test")
    return run(args.ledger, args.paths, args.strict)


if __name__ == "__main__":
    sys.exit(main())
