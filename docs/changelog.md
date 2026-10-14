---
id: changelog
title: Changelog
sidebar_position: 6
---

# Changelog

All material changes to the knowledge base are documented here. Changes are version-controlled in the [GitHub repository](https://github.com/b-gowland/ai-risk-kb).

## [1.5.0] — October 2026

### Re-verified — A2, A3, A4, B3, C3, G2 (14 October 2026; closes #54)
Full reviews of the six entries overdue since 28 September 2026 (F2 was re-verified on 5 October). Next review April 2027.
- **A2 Model Drift:** PSI example code rewritten (it binned each sample separately, so its output was meaningless); thresholds described as conventions; covers drift in vendor-hosted LLMs; EU AI Act chip moved to Art. 72 (post-market monitoring); unsourced underwriting incident replaced with Zillow Offers (2021) and the GPT-4 behaviour-change study (2024)
- **A3 Robustness:** Waymo recall corrected (failures surfaced in real-world driving 2022–24, fix deployed before the 2025 filing); OOD example code now sets its threshold from validation data; ISO 42001 anchor corrected
- **A4 Explainability:** SafeRent final approval corrected to November 2024 and claims aligned with the case record; nH Predict now cites the Senate PSI report and the class action; RG 271 reference removed; adds CJEU *Dun & Bradstreet Austria* (2025), Regulation B and AU s 21P; SHAP sign convention made explicit
- **B3 Lifecycle Governance:** removed claims that CPS 230 mentions AI testing or requires vendor change notice; Art. 12 log retention moved to Arts 19 and 26(6); SR 11-7 attributed to the Federal Reserve; withdrawn EEOC guidance removed; checklist code no longer approves an empty checklist; illustrative incidents replaced with the GPT-4o rollback (2025) and Knight Capital (2012)
- **C3 Model Theft:** covers LLM distillation; trade-secret and CFAA statements corrected (*Van Buren*, 2021); NIST IR 8596 described as a preliminary draft; daily-cap and throttle bugs fixed in the example code; illustrative incidents replaced with Anthropic's distillation disclosure (2026) and Carlini et al. (2024)
- **G2 Environmental Impact:** current IEA figures replace the 2019 estimate; EU AI Act reference corrected (Art. 99 is penalties; energy documentation is Annex XI); SEC climate rule shown as stayed and proposed for rescission; Australian mandatory climate disclosure and California SB 253 described accurately
- B3, C3 and G2 gain the risk description and scenario discussion questions the schema requires
- Citation ledger: EU AI Act Art. 72 added

## [1.4.2] — October 2026

### Added — incidents from source monitoring (#61, #67)
- **A1 — Hallucination:** a judge's order citing non-existent cases (Oklahoma, 2026); F1 cross-references it
- **B1 — Accountability:** a driverless vehicle that Colorado law gave police no way to cite (Denver, 2026)
- **B4 — Supply Chain:** undisclosed detection logic in an AI coding tool, later removed by the vendor (Claude Code, 2026)
- **C2 — Prompt Injection:** Salesforce Agentforce exploited twice through the same public Web-to-Lead form (ForcedLeak 2025, SalesBleed 2026)
- **E2 — Harmful Content:** general-purpose chatbots used in attack planning (Delhi Red Fort NIA chargesheet, 2026; Sarthe, France, 2025)

### Changed — E2 Harmful Content
- E2-003 incident response now covers escalating credible threats of violence found in user conversations, with legal confirming the basis for referral before go-live

## [1.4.1] — October 2026

### Corrected — F2 Shadow AI (re-verified 5 October 2026)
- EU AI Act reference moved from Art. 26 (deployers of high-risk systems only) to Art. 4 as amended by Regulation (EU) 2026/1744
- APRA CPS 234: removed a reference to an "annual attestation", which CPS 234 does not require
- HIPAA, FTC Act and Fair Work Act notes reworded to match what each actually requires
- APP 8 note now distinguishes disclosure from use
- Samsung incident: restriction described accurately (company devices and networks, May 2023)
- Endpoint catalogue: added chatgpt.com, consumer Copilot and DeepSeek; fixed a domain-matching bug in the example code

### Changed — all entries
- "Layer 2 — Practitioner overview" renamed "Layer 2 — Overview"
- Entries with a practice scenario now link to it at the top of Layer 1, under its real title
- Tag pages removed from the sitemap

## [1.4.0] — May 2026

### Added — Agentic AI risk entries
Six new entries covering risks specific to agentic AI systems:
- **C6 — MCP Attack Surface** — security risks from Model Context Protocol server integrations, supply chain compromise, and response injection (MITRE ATLAS v5.3–v5.4)
- **C7 — Multi-Agent Trust & Prompt Injection Chains** — injection propagation through inter-agent trust relationships in multi-agent pipelines
- **C8 — Computer-Use Agent Hijacking** — visual prompt injection attacks against agents that operate browsers and desktop interfaces
- **F4 — Irreversibility & Scope Creep in Autonomous Systems** — irreversible actions and capability accumulation beyond intended scope (OWASP LLM06)
- **B5 — Agentic Logging & Auditability Gaps** — forensic and regulatory logging requirements for agentic systems (EU AI Act Art. 12)
- **G5 — Excessive Agency & Uncontrolled Action Chains** — enterprise-wide governance of autonomous agent capability (OWASP LLM06)

### Updated — Existing entries (MITRE ATLAS v5.0–v5.6 and monitoring queue)
- **C2 — Prompt Injection** — added MCP server data exfiltration technique (ATLAS v5.3), jailbreak documentation (ATLAS v5.6), new C2-006 MCP server trust boundary control
- **C4 — Deepfakes** — added pet/animal scam incidents, AI-generated evidence fabrication cases, school harassment pattern, Aadhaar identity document fraud
- **C1 — Data Poisoning** — added AI agent tool data poisoning (ATLAS v5.2/v5.4), poisoned MCP server supply chain technique (ATLAS v5.4)
- **C5 — AI-Enabled Cyber Attacks** — added Generate Malicious Commands (ATLAS v5.2), Machine Compromise techniques (ATLAS v5.1/v5.4/v5.5)
- **B4 — Supply Chain** — added AI Supply Chain Rug Pull, Reputation Inflation, and MCP server compromise (ATLAS v5.3–v5.5)
- **E3 — Misinformation** — added AI-generated celebrity impersonation incidents, OpenAI covert influence operation disruptions, Meta coordinated inauthentic behaviour cases
- **E1 — Algorithmic Bias** — added facial recognition wrongful arrest pattern with documentary source references
- **D3 — Intellectual Property** — added AI-generated audiovisual content copyright reproduction case

### Automation
- Workflow 2 source-driven monitoring operational — weekly polling of 14+ sources with AI-assisted classification
- Model updated to `claude-sonnet-4-6`

## [1.3.0] — May 2026

### Brand and domain
- Project renamed to **AI Risk Practice Library** — part of [airiskpractice.org](https://airiskpractice.org/)
- Live URL updated to [library.airiskpractice.org](https://library.airiskpractice.org/)
- All internal links updated to new domain
- Companion training app now at [app.airiskpractice.org](https://app.airiskpractice.org/)
- Fork everyday track now at [app.airiskpractice.org/#/everyday](https://app.airiskpractice.org/)

### Design
- Full visual re-skin: Playfair Display + DM Sans typography, amber accent, white background
- New hero copy: "References explain the risks. This explains what to do."
- Docusaurus upgraded 3.5.2 → 3.10.1

## [1.2.0] — May 2026

### Structure
- Layer 1 heading renamed from "Executive card" to **"Start here"** across all 26 entries — the previous name implied a single audience and excluded everyone who wasn't a board member
- Schema reference updated to reflect new heading name

### New content
- **Everyday tab** added to three entries linked from the [Fork everyday track](https://app.airiskpractice.org/):
  - **A1 — Hallucination**: plain language explanation of AI confident wrong answers, safe vs risky use patterns, link to Fork hallucination scenario
  - **C4 — Deepfakes**: plain language explanation of voice cloning scams, out-of-band verification, Scamwatch reporting, link to Fork deepfake scenario
  - **E1 — Algorithmic Bias**: plain language explanation of AI in hiring decisions, right to ask for reasons, link to Fork employment scenario
- These tabs are written in public voice with no jargon, framework codes, or practitioner vocabulary

### Fork everyday track connection
- A1, C4, and E1 entries now cross-link with the Fork everyday scenario app
- The Everyday tabs provide the knowledge base entry point for non-practitioner readers arriving from shared Fork scenario cards

## [1.1.0] — April 2026

### Content
- Completed all 26 risk entries — 9 additional entries fully drafted to L3+L4 depth (A2, A3, A4, B2, B3, B4, E2, E3, G2)
- All 26 entries now complete across all four layers
- AI Risk Training Module launched — all 26 interactive scenarios live, one per KB entry
- Training links added to all 26 entries (▶ Play this scenario)

### Training module
- 26 choose-your-own-adventure scenarios across all 7 domains
- Four personas per scenario (Executive, Project Manager, Analyst, Business User); three personas for C1, C2, C3
- Total training content: approximately 2–3 hours
- Scenarios grounded in real documented incidents with verified facts

## [1.0.0] — March 2026

Initial public release.

### Content
- 17 risk entries across 7 domains (A through G)
- All four layers drafted for all entries
- Persona-specific hooks (executive, project manager, security analyst) for all entries
- Controls summary with owner, effort, and definition of done for all entries
- Technical implementation with code examples for all entries
- Scenario seeds for all entries

### Verified claims
- SafeRent settlement figure: $2.275M (court-approved, November 2024)
- Arup deepfake incident: $25M loss, January 2024, finance worker (not engineer)
- Waymo recall: 1,212 vehicles, May 2025, gates/chains/barriers (not "thin or suspended")
- Workday lawsuit: filed 2023, Ninth Circuit ruling March 2025
- EU AI Act high-risk effective date: August 2, 2026 (Annex III)
- All EU AI Act effective dates confirmed against Article 113

### Frameworks referenced
- MIT AI Risk Repository v5 (December 2025)
- NIST AI RMF 1.0 and AI 600-1
- EU AI Act (Regulation 2024/1689)
- ISO 42001:2023
- OWASP LLM Top 10 (2025)
- MITRE ATLAS
- APRA CPS 230 (effective July 2025)
- APRA CPS 234
- Australian Privacy Act 1988

---

*This is a living document. Updates are triggered by material new incidents, regulatory changes, or new authoritative framework publications. Review cadence: annually at minimum.*
