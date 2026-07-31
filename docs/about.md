---
id: about
title: About This Project
sidebar_position: 2
---

# About this project

The AI Risk Practice Library is a free, open-source reference for understanding, assessing, and controlling AI risk across organisations of any size, in any industry. It is part of [AI Risk Practice](https://airiskpractice.org/) — a free, open-source AI risk literacy resource.

## Why it exists

Existing AI risk resources fall into two categories. Authoritative frameworks — NIST AI RMF, EU AI Act, MIT AI Risk Repository — are comprehensive but require significant expertise to apply. Practitioner summaries are accessible but often lack the depth needed to design and implement actual controls.

This knowledge base aims to bridge that gap: authoritative enough to be credible, accessible enough to be usable by a board member, and specific enough for a security engineer to implement from.

## Structure

**32 risk entries** are organised across **7 domains** (A through G), each with four layers of depth:

- **Layer 1 — Start here** — Plain English summary for any audience, with tabs for executives, project managers, and security analysts, plus a general-audience tab for readers arriving from the [training app](https://app.airiskpractice.org/)
- **Layer 2** — Practitioner overview with controls ownership, effort estimates, and go-live criteria — designed for risk managers, compliance leads, and project managers
- **Layer 3** — Full actionable controls with KPIs and jurisdiction notes — designed for risk practitioners and internal audit
- **Layer 4** — Technical implementation with code examples and tool references — designed for security analysts and engineers

## Taxonomy basis

Content draws on and cross-references:

- MIT AI Risk Repository (v5, December 2025)
- NIST AI RMF 1.0 and AI 600-1 (GenAI)
- EU AI Act (Regulation 2024/1689)
- ISO 42001:2023
- OWASP LLM Top 10 (2025)
- MITRE ATLAS
- AI Incident Database (AIID) and OECD AI Incidents Monitor
- Stanford HAI AI Index 2025

## Maintenance

This knowledge base is designed to be maintained through a combination of automated monitoring and human review. Gap detection runs weekly at zero cost, checking all 32 entries for schema violations and missing content. A full maintenance pass — verifying flagged claims and monitoring 8 external sources — runs monthly using the Anthropic API. All proposed changes are generated as GitHub Issues for human review before any content changes are applied.

All factual claims are verified against primary sources before publication. Claims that cannot be verified are flagged inline rather than silently included.

## Companion training app

Each risk entry includes a **scenario seed** — a structured situation used as the basis for the companion training app. The [AI Risk Practice](https://app.airiskpractice.org/) app is a free, choose-your-own-adventure trainer built around two doors: **At home** (personal AI risk — scams, deepfakes, chatbot harm, data exposure) and **At work** (AI risk in a job, from general staff through specialists). You are the person the situation is happening to; you make the calls and see what follows. The library is the reference layer behind the At Work scenarios, and more scenarios are added over time.

## Licence

Content is published under the MIT licence. Code is published under Apache 2.0. You are free to use, adapt, and redistribute — with attribution.

## Important disclaimer

This resource is provided for informational purposes only. It is not legal, regulatory, or professional advice. Risk ratings are starting points for assessment, not prescribed values. Consult qualified professionals before making compliance or legal decisions.

## Contributing

See the [Contributing guide](/docs/contributing) to raise an issue, suggest an update, or submit a pull request. For general questions or non-technical feedback: [hello@airiskpractice.org](mailto:hello@airiskpractice.org)
