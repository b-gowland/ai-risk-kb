# AI Risk Practice Library

A free, open-source reference for understanding, assessing, and controlling AI risk — from board level to technical implementation.

**Live site:** https://library.airiskpractice.org/
**Companion training app:** https://app.airiskpractice.org/
**Project home:** https://airiskpractice.org/

---

## What this is

A practitioner reference covering 32 AI risk entries across 7 domains, with four layers of depth per entry:

| Layer | Audience | Content |
|-------|----------|---------|
| 1 — Start here | All audiences | Plain English summary, severity, key question, persona-specific tabs (Executive, PM, Analyst, Everyday) |
| 2 — Practitioner overview | Risk, compliance, PMs | Risk mechanism, controls ownership, effort, go-live criteria |
| 3 — Controls detail | Risk practitioners, audit | Full control descriptions, KPIs, jurisdiction notes |
| 4 — Technical implementation | Engineers, security analysts | Code examples, tool references, compliance implementation |

## Domains covered

| Domain | Entries |
|--------|---------|
| A — Technical | A1 Hallucination, A2 Model Drift, A3 Robustness, A4 Explainability |
| B — Governance | B1 Accountability, B2 Regulatory Compliance, B3 Lifecycle Governance, B4 Supply Chain, B5 Agentic Logging & Auditability Gaps |
| C — Security & Adversarial | C1 Data Poisoning, C2 Prompt Injection, C3 Model Theft, C4 Deepfakes, C5 AI-Enabled Cyber Attacks, C6 MCP Attack Surface, C7 Multi-Agent Trust & Prompt Injection Chains, C8 Computer-Use Agent Hijacking |
| D — Data | D1 Training Data Quality, D2 Privacy, D3 IP & Copyright |
| E — Fairness & Social | E1 Algorithmic Bias, E2 Harmful Content, E3 Misinformation |
| F — HCI & Deployment | F1 Automation Bias, F2 Shadow AI, F3 Scope Creep, F4 Irreversibility & Scope Creep in Autonomous Systems |
| G — Systemic & Macro | G1 Concentration Risk, G2 Environmental Impact, G3 Workforce Displacement, G4 AI Safety, G5 Excessive Agency & Uncontrolled Action Chains |

## Taxonomy basis

- MIT AI Risk Repository (v5, December 2025)
- NIST AI RMF 1.0 and AI 600-1 (GenAI)
- EU AI Act (Regulation 2024/1689)
- ISO 42001:2023
- OWASP LLM Top 10 (2026)
- MITRE ATLAS
- AI Incident Database (AIID) and OECD AI Incidents Monitor

## Repository structure

```
ai-risk-kb/
├── docs/
│   ├── domain-a-technical/       # A1–A4
│   ├── domain-b-governance/      # B1–B5
│   ├── domain-c-security/        # C1–C8
│   ├── domain-d-data/            # D1–D3
│   ├── domain-e-fairness/        # E1–E3
│   ├── domain-f-deployment/      # F1–F4
│   ├── domain-g-systemic/        # G1–G5
│   ├── how-to-use.md
│   ├── about.md
│   ├── schema.md
│   ├── contributing.md
│   └── changelog.md
├── automation/
│   └── scripts/                  # Weekly gap-check + monthly maintenance
└── .github/workflows/            # CI/CD and automation
```

## Maintenance

Gap detection runs weekly (zero cost). Full maintenance runs monthly via the Anthropic API; cost depends on entry length and the number of extracted claims. All changes require human review before publication.

Verification extracts claims from the complete entry. By default it assesses them using model training knowledge; opt-in web verification retrieves primary-source citation excerpts. Failed or malformed extraction/assessment responses are recorded as incomplete checks, retained in the review reports, and make the command exit nonzero after saving its reports. Flagged and unverifiable claims also enter the human review queue. Failed scheduled runs raise a failure issue; their reports remain available in the workflow artifacts. No KB content is changed automatically.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to raise an issue, suggest an update, or submit a pull request.

## Licence

Content: MIT licence. You are free to use, adapt, and redistribute with attribution.

## Related

- **Companion training app:** https://app.airiskpractice.org/
- **Training repo:** https://github.com/b-gowland/ai-risk-training
- **Project home:** https://airiskpractice.org/

### Opt-in web verification pilot

After setting `ANTHROPIC_API_KEY`, run from `automation/`:

```sh
uv run --frozen python automation_engine.py --mode single --entry A2 \
  --web-verify --web-max-claims 5 --web-searches-per-claim 2 --web-max-tokens 4096
```

The monthly workflow also exposes a manual `web_verify` switch, requiring a single entry. Scheduled runs keep their existing behavior. No live pilot is run as part of tests or PR validation.

Each searched claim uses one retrieval request and, when usable citations are returned, one evidence-assessment request. Defaults cap a run at five searched claims and two searches per claim, with a 4,096 output-token limit per web request. These are request limits, not a dollar budget: normal claim extraction and input tokens also cost money. Web requests disable SDK retries and the shared refusal fallback, and do not resume paused turns. Extra claims, failed searches, refusals and truncated responses are recorded as incomplete; remaining claims are not silently assessed from model knowledge.

The source allowlist lives in `automation/web_verification.py`. Repeated `--primary-domain nist.gov` options replace it for a scoped pilot. The allowlist bounds search sources; the model must still explain why selected evidence is primary and supports the particular claim. Short citation excerpts can be insufficient, in which case the result remains unverifiable. Domain membership alone never establishes accuracy.

JSON run records retain tool-returned URLs, citation excerpts, queries, retrieval timestamps, response IDs, token/search usage and selected evidence IDs. Human-review reports include the evidence even for supported claims. Search errors or exhausted limits make the command fail after reports are saved. Nothing changes KB content automatically.

API contract: [Anthropic web search documentation](https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-search-tool). Live provider behavior and retrieval quality still require a bounded pilot; the regressions use simulated API responses.
