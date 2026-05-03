# AI Risk Practice Library

A free, open-source reference for understanding, assessing, and controlling AI risk — from board level to technical implementation.

**Live site:** https://library.airiskpractice.org/
**Companion training app:** https://app.airiskpractice.org/
**Project home:** https://airiskpractice.org/

---

## What this is

A practitioner reference covering 26 AI risk entries across 7 domains, with four layers of depth per entry:

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
| B — Governance | B1 Accountability, B2 Regulatory Compliance, B3 Lifecycle Governance, B4 Supply Chain |
| C — Security & Adversarial | C1 Data Poisoning, C2 Prompt Injection, C3 Model Theft, C4 Deepfakes, C5 AI Cyber Attacks |
| D — Data | D1 Training Data Quality, D2 Privacy, D3 IP & Copyright |
| E — Fairness & Social | E1 Algorithmic Bias, E2 Harmful Content, E3 Misinformation |
| F — HCI & Deployment | F1 Automation Bias, F2 Shadow AI, F3 Scope Creep |
| G — Systemic & Macro | G1 Concentration Risk, G2 Environmental Impact, G3 Workforce Displacement, G4 AI Safety |

## Taxonomy basis

- MIT AI Risk Repository (v5, December 2025)
- NIST AI RMF 1.0 and AI 600-1 (GenAI)
- EU AI Act (Regulation 2024/1689)
- ISO 42001:2023
- OWASP LLM Top 10 (2025)
- MITRE ATLAS
- AI Incident Database (AIID) and OECD AI Incidents Monitor

## Repository structure

```
ai-risk-kb/
├── docs/
│   ├── domain-a-technical/       # A1–A4
│   ├── domain-b-governance/      # B1–B4
│   ├── domain-c-security/        # C1–C5
│   ├── domain-d-data/            # D1–D3
│   ├── domain-e-fairness/        # E1–E3
│   ├── domain-f-deployment/      # F1–F3
│   ├── domain-g-systemic/        # G1–G4
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

Gap detection runs weekly (zero cost). Full maintenance pass runs monthly via Anthropic API (~$2.70/run). All changes go through GitHub Issues for human review before publication.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to raise an issue, suggest an update, or submit a pull request.

## Licence

Content: MIT licence. You are free to use, adapt, and redistribute with attribution.

## Related

- **Companion training app:** https://app.airiskpractice.org/
- **Training repo:** https://github.com/b-gowland/ai-risk-training
- **Project home:** https://airiskpractice.org/
