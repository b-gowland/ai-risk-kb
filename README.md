# AI Risk Knowledge Base

A free, open-source reference for understanding, assessing, and controlling AI risk — from board level to technical implementation.

**Live site:** https://b-gowland.github.io/ai-risk-kb/

---

## What this is

A practitioner reference covering 17 AI risk categories across 7 domains, with four layers of depth per entry:

| Layer | Audience | Content |
|-------|----------|---------|
| 1 — Executive card | Board, executives | Plain English summary, severity, key question, persona-specific hooks |
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
│   ├── monitoring-sources.md
│   ├── contributing.md
│   └── changelog.md
├── automation/
│   ├── automation_engine.py      # Maintenance engine
│   └── automation_config.md      # Schedule and configuration
├── schema/
│   └── entry_template.md         # Entry schema v0.2
├── .github/workflows/
│   ├── deploy.yml                # Deploy to GitHub Pages
│   ├── weekly-monitor.yml        # Weekly incident monitoring
│   ├── monthly-gaps.yml          # Monthly gap detection
│   └── quarterly-verify.yml      # Quarterly fact-check
└── src/
    ├── pages/index.js            # Homepage
    └── css/custom.css            # Site styling
```

## Automated maintenance

The knowledge base is designed for automated maintenance with a human review gate. GitHub Actions workflows run:

- **Weekly** — check AIID and OECD AIM for new incidents
- **Monthly** — check regulatory sources and run gap detection
- **Quarterly** — fact-check all claims against primary sources

All proposed changes are generated as GitHub Issues for human review before being applied.

To run the automation locally:

```bash
export ANTHROPIC_API_KEY=your_key_here
cd automation
python automation_engine.py --mode gap-check     # Find content gaps
python automation_engine.py --mode monitor       # Check monitoring sources
python automation_engine.py --mode verify        # Fact-check claims
python automation_engine.py --mode full          # All of the above
python automation_engine.py --mode single --entry C2  # Single entry
```

## Running locally

```bash
git clone https://github.com/b-gowland/ai-risk-kb.git
cd ai-risk-kb
npm install
npm start
```

The site will be available at `http://localhost:3000/ai-risk-kb/`

## Contributing

See [CONTRIBUTING.md](docs/contributing.md) or the [contributing page](https://b-gowland.github.io/ai-risk-kb/docs/contributing) on the live site.

In brief: raise a GitHub Issue to report errors, suggest incidents, or propose new entries. Submit a pull request for content changes. All factual claims must be verifiable against primary sources.

## Licence

MIT licence. Free to use, adapt, and redistribute with attribution.

## Disclaimer

Provided for informational purposes only. Not legal, regulatory, or professional advice. Risk ratings are starting points for assessment, not prescribed values.

---

## Coming soon

**AI Risk Training Module** (`ai-risk-training`) — an interactive scenario-based learning tool using the scenario seeds embedded in each entry. Persona-based workplace scenarios, illustrated panels, multiple choice questions. Open source. [Watch this space.](https://github.com/b-gowland/ai-risk-training)
