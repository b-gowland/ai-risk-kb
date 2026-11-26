---
id: changelog
title: Changelog
sidebar_position: 6
---

# Changelog

All material changes to the knowledge base are documented here. Changes are version-controlled in the [GitHub repository](https://github.com/b-gowland/ai-risk-kb).

## [1.5.3] — November 2026

### Changed — site design and privacy
- Colours and fonts now follow the practice scenarios app: warm ground, ink text, one accent (#b0512b), Archivo, Newsreader and IBM Plex Mono. Link text now meets 4.5:1 contrast in light and dark mode (the old amber links were 3.2:1)
- Fonts are served from the site, so no visitor request goes to Google
- Footer links to the Privacy page (on the practice scenarios app, which covers all three sites) and to the practice scenarios and governance baseline; cross-site labels match the app
- Removed the leftover GitHub Pages deploy settings; `npm run deploy` now publishes to Cloudflare Pages

### Corrected
- "Practise this" lines no longer give scenario lengths, which the app now sets (A1, C4, D2, D3, E1, F1, F2)
- Invented email addresses in C2 and C7 now use `.example`
- About and How to use describe the app with its current tagline ("You decide, then see what follows")

### Added — checks
- `tools/incident-qa/check_incidents.py` flags aphorism-style closers and incident examples that don't end with a dated source. Runs in CI as a warning: 2 closers and 53 of 107 paragraphs without a closing dated source at the time it was added

### Corrected — monthly maintenance triage (#81)
Corrections from the 1 November automated check, each confirmed against the primary source. The full record, including the items rejected and deferred, is in `automation/reviews/2026-11-01-monthly-triage.md`.
- **MITRE ATLAS (B4, C1, C2, C5, C6, C7, C8):** release years corrected (v5.3 to v5.6 came out between January and April 2026, not 2025); claims that v5.3 added "named techniques" for MCP exfiltration and computer-use hijacking now describe the case studies it added; C6, C7 and C8 chips now cite technique IDs (AML.T0115.002, AML.T0143, AML.T0112.000) in place of "ATLAS v5.3"; C7 cites LLM Prompt Propagation (AML.T0143, October 2026); C5 Machine Compromise described as ATLAS defines it; C2 jailbreak entry dated to 2023
- **OWASP:** C1 chip corrected to ML02 (Data Poisoning Attack); ML01 is Input Manipulation
- **EU AI Act:** Art. 15(5), not Art. 9, names data poisoning (C1); Art. 10 paragraph numbers and the move of Art. 10(5) to Art. 4a (C1, D1); log retention cited to Arts 19 and 26(6) (C2); Art. 9(2) for continuous review (D1); Art. 21 for cooperation with authorities (E1); Art. 26(2) and 26(12) wording (B1, B5); Art. 25 and 43(4) claims aligned with the text (B1, B4, F3); Art. 11(1) for technical documentation (B2); Art. 53 copyright duties apply to all GPAI providers (D3); prohibited practices dated with penalties from August 2025 (B2)
- **APRA:** CPS 234 and CPS 230 paragraph numbers corrected (B1, B2, C1, C5, G1); CPS 234 no longer said to require awareness training, an annual attestation, least privilege or a 12-month log retention (B5, C4, C5, C6, E3, F1, G4); CPS 230 no longer said to require Board approval of outsourcing (B2); G4 describes the 30 April 2026 letter as written
- **Other:** NIST CSF identifiers given in CSF 2.0 form (B5, C2, C6, C7); NIST AI 600-1 no longer said to cover federated learning, minimal footprint or kill switches (C1, G4); NIST IR 8596 described as a preliminary draft (C1); DORA concentration risk cited to Art. 29 and continuity testing to Art. 11(6) (G1); modern award consultation clauses set no 28-day period (G3); FinCEN advisory number, ASIC RG 274 and SEC rule dates corrected (C4, C5); SEC rules no longer said to require AI risk disclosure (B1); EO 14110 shown as revoked in January 2025 (E2, G4); B2 describes the 30 April 2026 APRA letter as written; *Google v. Oracle* outcome (D3); Gender Shades page numbers (D1, E1); federal CSAM definition (E2)
- Citation ledger: ATLAS refreshed to v2026.10 (AML.T0005 renamed Replicate AI Model Behavior); AML.T0099, T0109, T0111, T0112, T0112.000, T0115.002 and T0143 added

## [1.5.2] — November 2026

### Added — incidents from source monitoring (#79)
- **B4 — Supply Chain:** a supplier's cloud application identities used to reach customer tenants (ConnectWise, 2026); C5 cross-references it
- **C4 — Deepfakes:** AI-voiced bank helpdesk calls used to copy bank cards, about €380,000 from some 170 victims (Netherlands, 2026); cross-reference to the Spanish campaign deepfake in E3
- **C5 — AI Cyber Attacks:** an open-source agentic penetration testing framework used in a state-aligned campaign against hundreds of organisations (Storm-0940 / ARTEX, 2026)
- **E2 — Harmful Content:** a lawsuit alleging ChatGPT failed to escalate a 15-year-old's suicide risk (*Habib v. OpenAI*, 2026)
- **E3 — Misinformation:** a party's campaign video deepfaking political rivals, now subject to criminal complaints (Spain, 2026)
- **F1 — Automation Bias:** two I-80 crashes in which drivers said Tesla Full Self-Driving was engaged, one with the driver asleep (California, 2026)
- **G4 — AI Safety:** an internal OpenAI model that used credentials it found to access and change a third party's systems during an evaluation; agents in a UK AISI cyber evaluation that targeted real people (2026); G5 cross-references both

### Not added from #79
- A3 entry for the Vallejo Tesla fatality: whether Full Self-Driving was engaged, and what it perceived, rests on the driver's account; no vehicle data has been published

## [1.5.1] — October 2026

### Added — incidents from source monitoring (#75)
- **D2 — Privacy:** an ambient AI scribe alleged to have recorded patients without consent and written consent statements into their charts (Sharp HealthCare / Abridge, 2025); police officers misusing licence plate recognition searches to stalk people, with no one reviewing the logs (Braselton, GA and Haines City, FL, 2025–2026)
- **F1 — Automation Bias:** a casino facial recognition match trusted over a valid driver's licence (Reno, 2023; *Killinger v. Jager*)
- **C5 — AI Cyber Attacks:** disclosed OT controller vulnerabilities reproduced and chained by an AI agent in about 30 minutes (Claroty Team82, 2026)

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
