# AI Risk Practice Library: notes for Claude

Free, open-source reference library on AI risk (library.airiskpractice.org):
32 risk entries across 7 domains, each in four layers from board summary to
technical implementation, mapped to NIST AI RMF, the EU AI Act, OWASP and
MITRE ATLAS.

Docusaurus 3, static build. Hosted on Cloudflare Pages (project
`ai-risk-library`), deployed by GitHub Actions (`.github/workflows/deploy.yml`)
on push to `main`. Companion sites: `b-gowland/ai-risk-training` (practice
scenarios, app.airiskpractice.org) and `b-gowland/ai-risk-baseline`
(governance baseline, baseline.airiskpractice.org). Cross-site standards are
in ai-risk-training's
[`docs/OPERATING_MODEL.md`](https://github.com/b-gowland/ai-risk-training/blob/main/docs/OPERATING_MODEL.md).

Start with [`README.md`](README.md) and [`CONTRIBUTING.md`](CONTRIBUTING.md);
the entry structure is in [`docs/schema.md`](docs/schema.md).

## Before you push

Run what CI runs:

- `npm ci && npm run build`. The config has `onBrokenLinks: 'throw'` and
  `onBrokenMarkdownLinks: 'throw'`, so a broken link fails the build.
- Citation ledger, strict: `pip install pyyaml`, then
  `python3 tools/citation-ledger/check_citations.py --strict --ledger tools/citation-ledger/citation-ledger.yaml docs`.
  A new framework ID needs a verified ledger entry, never a guessed one.
- Incident examples QA: `python3 tools/incident-qa/check_incidents.py docs`.
  Warning only for now; don't add new hits.
- If you touch `automation/`: `cd automation && uv run ruff check . && uv run pytest -q`.

## Rules that are easy to break

- **Plain language, Australian English.** Write for a practitioner who is not
  a specialist in every field the library covers. Avoid machine-writing
  patterns: "isn't X. It's Y" contrasts, "not X but Y", aphorism closers
  ("The lesson: ..."), filler intensifiers, signposting.
- **Sources for dated claims.** Every incident example ends with a dated source
  in parentheses, for example "(AP reporting, September 2026)". Legal and
  regulatory claims cite the primary text. Never claim a system is "compliant".
- **Invented names** must not belong to real organisations, and example
  domains and email addresses use `.example`.
- **Times:** don't type scenario lengths into "Practise this" lines. The app
  owns its times (ai-risk-training `src/engine/timing.js`).
- **Design tokens** follow the practice scenarios app and live in
  `src/css/custom.css`. Text and links must hold 4.5:1 in light and dark mode.
- **Privacy:** the site runs Plausible on the property shared with the app and
  the Baseline; the Privacy page is the app's (`/#/privacy`, linked from the
  footer). Add no new tracking or data collection. Fonts are self-hosted
  (`@fontsource` packages loaded by `src/fonts.js`): don't add Google Fonts or
  other third-party hosts.

## Hosting

- Don't change hosting, DNS or Cloudflare settings. List the change for the
  owner to make.
- `static/_headers` (security headers, `noindex` on `*.pages.dev`) must stay in
  the build.
- By hand, from any machine: `npm run deploy` (builds, then
  `wrangler pages deploy build --project-name=ai-risk-library --branch=main`).
  Normally the Actions workflow deploys; don't deploy from a branch.
- `.wrangler/` (local emulator state) is gitignored; never commit it.

## Keep work in the repo

Cloud containers can be rebuilt and lose anything not pushed (this happened in
November 2026). Commit plans and reviews to the repo, not scratch files, and
push work to a branch before stopping.
