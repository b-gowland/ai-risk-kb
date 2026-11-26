# Monthly maintenance triage — run of 1 November 2026 (#81)

Triage of the human-review items from monthly run 41296620479 (review ID 71b0aed0), done 26 November 2026. Each item was checked against the KB text it refers to and, where a change was considered, against a primary source fetched during this pass. Items the checker marked "unverifiable" were applied only when a primary source confirmed the change.

## Counts

| Decision | Items |
|---|---|
| Apply | 73 |
| Reject | 183 |
| Owner | 12 (plus the 2 gap items) |
| Deferred | 52 |
| **Total** | **320** (192 corrections, 128 reviews) |

"Apply" means the KB text was changed in this PR. Several items point at the same error, so 73 items led to about 100 text edits across 21 entries (listed in the changelog, 1.5.3).

## Systematic findings

1. **The issue body was cut off at item 68 of 320.** GitHub caps issue bodies at 65,536 characters, so #81 shows 68 items and the end of item 68 is missing. This triage used the full list from the run artefact (`maintenance-reports-41296620479/human_review_20261101_1345.md`).
2. **The checker cannot know about post-cut-off releases, and says so.** 67 items were rejected because the checker doubted facts that postdate its training data and that primary sources confirm: the OWASP Top 10 for LLM Applications 2026 (8 items), Regulation (EU) 2026/1744, the Digital Omnibus on AI (19 items), ATLAS techniques added from v5.2 to v2026.10 (6 items), and 2026 publications and incidents from APRA, ASD and source monitoring (34 items).
3. **But the KB had real ATLAS version errors.** The checker was right to distrust the ATLAS citations, for a different reason: the KB dated v5.3 to v5.6 as "2025" (they came out from 30 January to 30 April 2026), and three entries said v5.3 added "named techniques" for MCP exfiltration, multi-agent injection and computer-use hijacking, when v5.3 added one technique (Deploy AI Agent) and some case studies. ATLAS also moved to calendar versions in May 2026 (v2026.10 is current), so "MITRE ATLAS v5.3" chips were out of date. 15 items were applied on this ground.
4. **Half of the "corrections" were restatements.** 83 items marked `corrected` restate the KB claim at greater length and agree with it. They were rejected. The checker uses `corrected` whenever it adds detail.
5. **Paragraph and article numbers were the main real error class.** APRA CPS 234 and CPS 230 paragraph numbers (17 applied items) and EU AI Act or DORA article and paragraph numbers (19 applied items) were often wrong. Several CPS 234 claims (awareness training, least privilege, a 12-month log retention, an annual attestation) are not in the standard at all. The same claims had already been removed from B3 and F2 in October; they survived in other entries.
6. **The checker's "current value" is its paraphrase, not the KB text.** For example, item 213 cites "CPS 230 cl. 37", which does not appear in G1. Each item was matched to the entry text before deciding.

## Suggested changes to the checker (not made here)

These are for `automation/automation_engine.py` (`_verify_claim`, `_extract_verifiable_claims`) and `automation/automation_config.md`. No automation code was changed in this PR.

1. **Put today's date and the training cut-off in the verification prompt**, and tell the model: "If the claim concerns an event, release or document dated after your training data, return `unverifiable` with `action_required: false` unless you have specific contrary knowledge. Do not return `corrected` or `flagged` for it." This alone would have removed about 67 items.
2. **Give the checker the citation ledger.** Pass the relevant `tools/citation-ledger/citation-ledger.yaml` blocks (ATLAS, OWASP editions, EU AI Act articles) into the prompt as verified ground truth, with their sources, and skip claims that the deterministic ledger check already passes.
3. **Keep a list of later-dated instruments** in `automation_config.md` (Regulation (EU) 2026/1744, OWASP LLM Top 10 2026, ATLAS calendar versions, APRA letter of 30 April 2026) and add it to the prompt as "known facts after your cut-off".
4. **Separate "corrected" from "elaborated".** Require `corrected` only when `verified_value` contradicts `original_value`; add a `verified_with_detail` status (no review needed) for restatements.
5. **Quote the KB text.** Make claim extraction return the exact sentence and line, and have the report show it, so reviewers do not have to find what a paraphrase refers to.
6. **Ask for paragraph-level checks where the source is public.** Most real errors were paragraph numbers in CPS 230, CPS 234 and the EU AI Act. These are cheap to check deterministically: add CPS 234/230 paragraph titles and EU AI Act paragraph headings to the ledger and extend `check_citations.py` to parse "CPS 234 para. N" and "Art. N(m)".
7. **Don't post the whole report into the issue body.** Post the summary and counts, attach the full list as the run artefact (already done) and link it, or split it across comments of under 60,000 characters.
8. **Run the web pilot (`--web-verify`) on the entries with the most 2026 citations** (B2, C1, C2, C5, C6, C7, C8, B4) before the next monthly run, and compare its false-positive rate with this run.

## Owner decisions

- **Gap G-1 (C7) and G-2 (G5):** Layer 4 technical implementation detail is missing (gap report, "recommended", not blocking). Content work for the owner to schedule.
- Items 12, 48, 154, 178–179, 195, 270/282/307/313, 273, 305: see the tables. In short: ISO 42001 clause in the C1 chip; C5's "illustrative" university breach that looks like ANU; how to word the Digital Omnibus effect on Art. 73 and Art. 49; E1 SafeRent date versus A4; E1 wrongful-arrest count; EEOC 2023 guidance (withdrawn per B3) still cited in B1, F1 and F3; APP 3 versus APP 6 in F3.

## Deferred

52 items were deferred under the budget rule: they are incident details, wording or secondary legal points with lower reader impact, or they need a source not reachable this pass. The highest-priority deferral is item 161 (E2's US state-law sentence, which names California SB 1047 and "Colorado HB 1468").

## Sources used

Primary sources fetched in this pass: MITRE ATLAS data (github.com/mitre-atlas/atlas-data: `CHANGELOG.md`, `dist/v6/ATLAS-2026.10.yaml`); OWASP LLM Top 10 2026 record (doi.org/10.5281/zenodo.22109015) and the OWASP ML Top 10 site; Regulation (EU) 2024/1689, Regulation (EU) 2026/1744 and Regulation (EU) 2022/2554, in the Official Journal text from the EU Publications Office; APRA CPS 234 (July 2019), CPS 230 (July 2023) and the 30 April 2026 letter (apra.gov.au); NIST CSF 2.0 (CSWP 29), NIST AI 600-1 and the IR 8596 draft page (nist.gov); the Federal Register (SEC Release 33-11216; EO 14148); 18 U.S.C. § 2256 (govinfo.gov); *Google v. Oracle* (supremecourt.gov); FinCEN advisories; ASIC RG 274; Clerks—Private Sector Award 2020 (fairwork.gov.au); PMLR 81; the AI Incident Database. Not reachable this pass: cyber.gov.au (503), oaic.gov.au and iso.org (403), consilium.europa.eu (403).

## Items by entry

### A1

| # | Kind | Checker status | Claim (abridged) | Decision | Reason | Source |
|---|---|---|---|---|---|---|
| 105 | correction | corrected | Moffatt v. Air Canada was decided by the BC Civil Resolution Tribunal in 2024, holding an organisation liab… | **Reject** | Checker restates the claim at length and confirms it in substance; no error identified (spot-checked) |  |
| 106 | correction | corrected | OWASP lists 'LLM07:2026 Misinformation' as a category. | **Reject** | OWASP Top 10 for LLM Applications 2026 exists (4 Aug 2026): LLM03:2026 Excessive Agency, LLM07:2026 Misinformation | https://doi.org/10.5281/zenodo.22109015 |
| 107 | correction | corrected | Air Canada's chatbot invented a non-existent bereavement fare discount, and the tribunal rejected the argum… | **Deferred** | Legal or regulatory detail needs a source not fetched this pass (court record, statute or agency page) |  |
| 108 | correction | corrected | Air Canada was awarded against in the amount of C$812 in damages in Moffatt v. Air Canada. | **Reject** | C$812 matches the C$812.02 award |  |
| 109 | correction | corrected | Mata v. Avianca (SDNY, 2023) resulted in sanctions including fines and required remedial training. | **Deferred** | Legal or regulatory detail needs a source not fetched this pass (court record, statute or agency page) |  |
| 110 | review | unverifiable | An Associate District Judge in Stephens County, Oklahoma issued a family law order relying on at least two … | **Reject** | 2026 event after checker cut-off; entry was added with sources (1.4.x/1.5.x); no contrary evidence |  |
| 111 | review | unverifiable | The judge told state investigators he had used ChatGPT, and the Oklahoma Council on Judicial Complaints ref… | **Reject** | 2026 event after checker cut-off; entry was added with sources (1.4.x/1.5.x); no contrary evidence |  |
| 112 | review | unverifiable | The Oklahoma judge incident is catalogued as AI Incident Database incident 1724. | **Reject** | AIID 1724 is the Oklahoma judge case | https://incidentdatabase.ai/cite/1724/ |
| 113 | review | unverifiable | Hallucination rate KPI target of under 2% on factual queries, and a staff training completion threshold abo… | **Reject** | A KPI target the entry recommends, not a factual claim |  |

### A2

| # | Kind | Checker status | Claim (abridged) | Decision | Reason | Source |
|---|---|---|---|---|---|---|
| 114 | review | flagged | Annex III high-risk obligations under the EU AI Act apply from 2 December 2027 under Regulation (EU) 2026/1744 | **Reject** | Reg (EU) 2026/1744 Art. 113(c): Annex III from 2 Dec 2027, Annex I from 2 Aug 2028 | https://eur-lex.europa.eu/eli/reg/2026/1744/oj |
| 115 | correction | corrected | Federal Reserve SR 11-7 model risk guidance requires ongoing monitoring, including outcomes analysis | **Reject** | Checker restates the claim at length and confirms it in substance; no error identified (spot-checked) |  |
| 116 | correction | corrected | Zillow closed its Zillow Offers home-buying business in November 2021 | **Reject** | Checker confirms the KB dates and outcome |  |

### A3

| # | Kind | Checker status | Claim (abridged) | Decision | Reason | Source |
|---|---|---|---|---|---|---|
| 117 | review | unverifiable | In September 2026 another Waymo drove around market barricades in Denver | **Reject** | 2026 event after checker cut-off; entry was added with sources (1.4.x/1.5.x); no contrary evidence |  |
| 118 | correction | corrected | McDonald's IBM drive-thru test ended after viral videos showed the system failing | **Reject** | Checker confirms the KB dates and outcome |  |

### A4

| # | Kind | Checker status | Claim (abridged) | Decision | Reason | Source |
|---|---|---|---|---|---|---|
| 101 | review | unverifiable | SafeRent settlement received preliminary approval in April 2024 | **Deferred** | Legal or regulatory detail needs a source not fetched this pass (court record, statute or agency page) |  |
| 102 | correction | corrected | GDPR Art. 15(1)(h) and Art. 22 provide the right to meaningful information about automated decision-making … | **Reject** | Checker restates the claim at length and confirms it in substance; no error identified (spot-checked) |  |
| 103 | correction | corrected | EU AI Act Art. 86 gives a right to explanation for decisions by deployers of Annex III high-risk systems | **Reject** | Checker restates the claim at length and confirms it in substance; no error identified (spot-checked) |  |
| 104 | review | unverifiable | Application of the Annex III high-risk obligations was deferred to 2 December 2027 by Regulation (EU) 2026/… | **Reject** | Reg (EU) 2026/1744 Art. 113(c): Annex III from 2 Dec 2027, Annex I from 2 Aug 2028 | https://eur-lex.europa.eu/eli/reg/2026/1744/oj |

### B1

| # | Kind | Checker status | Claim (abridged) | Decision | Reason | Source |
|---|---|---|---|---|---|---|
| 271 | correction | corrected | EU AI Act Art. 26 requires deployers of high-risk AI systems to assign human oversight to a named person wi… | **Apply** | Art. 26(2) says natural persons with competence, training, authority and support, not "a named person" | https://eur-lex.europa.eu/eli/reg/2024/1689/oj |
| 272 | correction | corrected | EU AI Act Art. 71 — high-risk AI systems must be registered in the EU AI database | **Reject** | Checker restates the claim at length and confirms it in substance; no error identified (spot-checked) |  |
| 273 | review | flagged | EU database registration obligation applies from 2 December 2027 for Annex III systems, deferred from 2 Aug… | **Owner** | B1 says registration (Art. 49) applies from 2 Dec 2027: Reg 2026/1744 moves Chapter III Sections 1-3, not Section 5; practical effect via Art. 6 classification. Decide wording | https://eur-lex.europa.eu/eli/reg/2026/1744/oj |
| 274 | correction | corrected | EU AI Act Art. 25 — deployer obligations cannot be contractually transferred to providers in a way that red… | **Apply** | Art. 25 contains no express bar on contractual transfer; reworded to Art. 26/25 | https://eur-lex.europa.eu/eli/reg/2024/1689/oj |
| 275 | correction | corrected | EU AI Act Art. 14 — human oversight must be technically implementable | **Reject** | Checker restates the claim at length and confirms it in substance; no error identified (spot-checked) |  |
| 276 | correction | corrected | APRA CPS 230 cl. 20 requires material service arrangements to be identified and managed | **Apply** | Material service provider register is CPS 230 para 49, not para 20 | https://www.apra.gov.au/sites/default/files/2023-07/Prudential%20Standard%20CPS%20230%20Operational%20Risk%20Management%20-%20clean.pdf |
| 277 | correction | corrected | APRA CPS 230 — outsourcing arrangements must not reduce the regulated entity's accountability to APRA; boar… | **Reject** | Checker restates the claim at length and confirms it in substance; no error identified (spot-checked) |  |
| 278 | review | unverifiable | APRA letter to industry on AI dated 30 April 2026 applying existing prudential standards to AI; found board… | **Reject** | APRA letter of 30 Apr 2026 confirmed, including these findings | https://www.apra.gov.au/news-and-publications/apra-letter-industry-artificial-intelligence-ai |
| 279 | correction | corrected | ISO 42001 Cl. 5.3 requires organisational roles, responsibilities and authorities for AI management to be a… | **Reject** | Checker restates the claim at length and confirms it in substance; no error identified (spot-checked) |  |
| 280 | correction | corrected | SEC Cybersecurity Rules require board-level disclosure of material AI risks | **Apply** | SEC 2023 rules cover cybersecurity incidents and board oversight, not AI risk disclosure | https://www.govinfo.gov/content/pkg/FR-2023-08-04/html/2023-16194.htm |
| 281 | correction | corrected | OCC model risk management guidance (SR 11-7) requires designated model owners for all models used in credit… | **Apply** | SR 11-7 is Federal Reserve guidance (OCC issued it as 2011-12); attribution fixed | https://www.federalreserve.gov/boarddocs/srletters/2011/sr1107.htm |
| 282 | correction | corrected | EEOC guidance (2023) — employers are accountable for employment decisions made using vendor AI tools regard… | **Owner** | B1, F1, F3 cite the May 2023 EEOC technical assistance as current; B3 removed it as withdrawn (Oct 2026). Confirm and align |  |
| 283 | correction | corrected | NIST AI RMF GOVERN 1.2 is a relevant reference for accountability | **Reject** | Checker restates the claim at length and confirms it in substance; no error identified (spot-checked) |  |
| 284 | correction | corrected | In 2023 UnitedHealth's AI system overrode physician recommendations in claim denials with no identifiable r… | **Reject** | Checker restates the claim at length and confirms it in substance; no error identified (spot-checked) |  |
| 285 | review | unverifiable | In September 2026 a Waymo robotaxi drove around barricades and through the South Pearl Street Farmers Marke… | **Reject** | 2026 event after checker cut-off; entry was added with sources (1.4.x/1.5.x); no contrary evidence |  |
| 286 | review | unverifiable | Denver Police and Colorado State Patrol said there was no mechanism in Colorado law to issue a citation to … | **Reject** | 2026 event after checker cut-off; entry was added with sources (1.4.x/1.5.x); no contrary evidence |  |

### B2

| # | Kind | Checker status | Claim (abridged) | Decision | Reason | Source |
|---|---|---|---|---|---|---|
| 259 | correction | corrected | EU AI Act prohibited practices enforceable from February 2025 (2 February 2025) | **Apply** | Art. 5 applied 2 Feb 2025; penalties (Ch. XII) from 2 Aug 2025 (Art. 113(b)) | https://eur-lex.europa.eu/eli/reg/2024/1689/oj |
| 260 | review | flagged | Digital Omnibus is Regulation (EU) 2026/1744 and defers high-risk obligations to 2 December 2027 (Annex III… | **Reject** | Reg (EU) 2026/1744 Art. 113(c): Annex III from 2 Dec 2027, Annex I from 2 Aug 2028 | https://eur-lex.europa.eu/eli/reg/2026/1744/oj |
| 261 | review | unverifiable | Regulation (EU) 2026/1744 published in the Official Journal on 24 July 2026 and in force 27 July 2026 | **Reject** | OJ L 2026/1744 dated 24.7.2026; enters into force on the third day after publication (27 Jul 2026) | https://eur-lex.europa.eu/eli/reg/2026/1744/oj |
| 262 | review | unverifiable | Council of the EU press release dated 29 June 2026 on the Digital Omnibus on AI | **Reject** | Council site not reachable; regulation text confirms adoption (signed 8 Jul 2026); no contrary evidence | https://eur-lex.europa.eu/eli/reg/2026/1744/oj |
| 263 | review | flagged | The new Digital Omnibus dates are fixed and not conditional on harmonised standards being ready | **Reject** | Art. 113(c) as amended sets fixed dates with no standards condition | https://eur-lex.europa.eu/eli/reg/2026/1744/oj |
| 264 | review | flagged | New EU AI Act bans on AI generating non-consensual intimate imagery or CSAM apply from 2 December 2026 | **Reject** | Reg 2026/1744 adds Art. 5(1)(ba),(bb) (intimate imagery, CSAM), applying from 2 Dec 2026 | https://eur-lex.europa.eu/eli/reg/2026/1744/oj |
| 265 | correction | corrected | EU AI Act Art. 9 risk management system requirement; Art. 16(b) technical documentation prepared before dep… | **Apply** | Technical documentation before market is Art. 11(1); Art. 16(b) is name and contact marking | https://eur-lex.europa.eu/eli/reg/2024/1689/oj |
| 266 | correction | corrected | Art. 5 prohibited practices include emotion recognition in workplace/education and real-time remote biometr… | **Reject** | Checker restates the claim at length and confirms it in substance; no error identified (spot-checked) |  |
| 267 | correction | corrected | APRA CPS 230 cl. 20 requires board approval of material outsourcing arrangements | **Apply** | CPS 230 para 20 makes the Board accountable for oversight; no approval of each arrangement (B2 L101 and L267) | https://www.apra.gov.au/sites/default/files/2023-07/Prudential%20Standard%20CPS%20230%20Operational%20Risk%20Management%20-%20clean.pdf |
| 268 | review | unverifiable | APRA letter to industry on AI dated 30 April 2026 applying CPS 220, CPS 230, CPS 234, with observations in … | **Apply** | Letter does not name CPS 220/230/234; B2 now quotes its "principles-based prudential framework" | https://www.apra.gov.au/news-and-publications/apra-letter-industry-artificial-intelligence-ai |
| 269 | review | unverifiable | On 15 July 2026 the Australian Prime Minister announced mandatory Australian Standards for AI, a new Office… | **Reject** | 2026 event after checker cut-off; entry was added with sources (1.4.x/1.5.x); no contrary evidence |  |
| 270 | review | verified | EEOC technical assistance/guidance (2023) says employers are responsible for employment decision tools incl… | **Owner** | B1, F1, F3 cite the May 2023 EEOC technical assistance as current; B3 removed it as withdrawn (Oct 2026). Confirm and align |  |

### B3

| # | Kind | Checker status | Claim (abridged) | Decision | Reason | Source |
|---|---|---|---|---|---|---|
| 236 | review | unverifiable | APRA's letter to industry on AI was issued on 30 April 2026, setting expectations on governance, operationa… | **Reject** | APRA letter of 30 Apr 2026 confirmed, including these findings | https://www.apra.gov.au/news-and-publications/apra-letter-industry-artificial-intelligence-ai |
| 237 | review | verified | APRA CPS 230 does not mention AI | **Reject** | Checker itself verified the claim |  |
| 238 | correction | corrected | ISO 42001 Clause 8 covers operation/AI system lifecycle management | **Reject** | Checker restates the claim at length and confirms it in substance; no error identified (spot-checked) |  |

### B4

| # | Kind | Checker status | Claim (abridged) | Decision | Reason | Source |
|---|---|---|---|---|---|---|
| 239 | correction | corrected | EU AI Act Art. 53: providers of general-purpose AI models must provide technical documentation to downstrea… | **Reject** | Checker restates the claim at length and confirms it in substance; no error identified (spot-checked) |  |
| 240 | correction | corrected | EU AI Act Art. 25: deployers must select providers that are compliant with the Act (B4-001); elsewhere desc… | **Apply** | Art. 25 contains no duty to select compliant providers | https://eur-lex.europa.eu/eli/reg/2024/1689/oj |
| 241 | correction | corrected | EU AI Act Art. 13: deployers of high-risk AI must have access to documentation sufficient to understand the… | **Reject** | Checker restates the claim at length and confirms it in substance; no error identified (spot-checked) |  |
| 242 | correction | corrected | EU AI Act Art. 26: deployers must be able to monitor AI system behaviour | **Reject** | Checker restates the claim at length and confirms it in substance; no error identified (spot-checked) |  |
| 243 | correction | corrected | GDPR Art. 28: processor must not engage sub-processors without prior specific or general written authorisat… | **Reject** | Checker restates the claim at length and confirms it in substance; no error identified (spot-checked) |  |
| 244 | correction | corrected | APRA CPS 230 requires due diligence on material service providers commensurate with risk, and notification … | **Apply** | CPS 230 para 59 is notice to APRA, not vendor notice; B4 aligned with B3 (Oct 2026) | https://www.apra.gov.au/sites/default/files/2023-07/Prudential%20Standard%20CPS%20230%20Operational%20Risk%20Management%20-%20clean.pdf |
| 245 | review | unverifiable | APRA sent a letter to industry on AI on 30 April 2026 which found many entities relying on a single AI prov… | **Reject** | APRA letter of 30 Apr 2026 confirmed, including these findings | https://www.apra.gov.au/news-and-publications/apra-letter-industry-artificial-intelligence-ai |
| 246 | correction | corrected | OCC third-party risk management guidance (2023) says due diligence should be tailored to risk and extends t… | **Reject** | Checker restates the claim at length and confirms it in substance; no error identified (spot-checked) |  |
| 247 | correction | corrected | NIST AI 100-1 is the AI Risk Management Framework and explicitly addresses supply chain risk including upst… | **Reject** | Checker restates the claim at length and confirms it in substance; no error identified (spot-checked) |  |
| 248 | review | verified | Executive Order 14110 (2023) includes requirements for AI safety documentation | **Reject** | Checker itself verified the claim |  |
| 249 | correction | corrected | GLBA Safeguards Rule requires service provider agreements to address data protection; HIPAA BAA must cover … | **Reject** | Checker restates the claim at length and confirms it in substance; no error identified (spot-checked) |  |
| 250 | review | flagged | CISA has published AI-BOM guidance | **Deferred** | Legal or regulatory detail needs a source not fetched this pass (court record, statute or agency page) |  |
| 251 | correction | corrected | Samsung engineers submitted proprietary source code and internal meeting notes to ChatGPT in 2023; Samsung … | **Reject** | Checker restates the claim at length and confirms it in substance; no error identified (spot-checked) |  |
| 252 | review | unverifiable | Samsung incident is recorded as AI Incident Database #768 and covered by CIO Dive and Gizmodo in April 2023 | **Reject** | AIID 768 is the Samsung ChatGPT leak | https://incidentdatabase.ai/cite/768/ |
| 253 | correction | corrected | npm supply chain attack (2025): compromised open-source Python/npm packages introduced malicious code affec… | **Deferred** | Legal or regulatory detail needs a source not fetched this pass (court record, statute or agency page) |  |
| 254 | review | unverifiable | MITRE ATLAS v5.5 (2025) documented the AI Supply Chain Rug Pull technique | **Apply** | v5.5 released 30 Mar 2026, not 2025; Reputation Inflation wording aligned with ATLAS definition | https://github.com/mitre-atlas/atlas-data/tree/main/dist/v6 |
| 255 | review | unverifiable | MITRE ATLAS v5.5 documented AI Supply Chain Reputation Inflation technique | **Apply** | v5.5 released 30 Mar 2026, not 2025; Reputation Inflation wording aligned with ATLAS definition | https://github.com/mitre-atlas/atlas-data/tree/main/dist/v6 |
| 256 | review | unverifiable | MITRE ATLAS v5.3 (2025) documented compromise of MCP servers as a supply chain attack vector | **Apply** | v5.3/v5.5 added MCP case studies (CS0045, CS0053), not a technique; dates corrected | https://github.com/mitre-atlas/atlas-data/blob/main/CHANGELOG.md |
| 257 | review | unverifiable | In June 2026 a developer found Claude Code contained obfuscated logic altering the system prompt for some u… | **Reject** | 2026 event after checker cut-off; entry was added with sources (1.4.x/1.5.x); no contrary evidence |  |
| 258 | review | unverifiable | Anthropic said the Claude Code behaviour was an experiment begun in March to counter unauthorised resellers… | **Reject** | 2026 event after checker cut-off; entry was added with sources (1.4.x/1.5.x); no contrary evidence |  |

### B5

| # | Kind | Checker status | Claim (abridged) | Decision | Reason | Source |
|---|---|---|---|---|---|---|
| 287 | correction | corrected | EU AI Act Art. 12 mandates automatic logging for high-risk AI systems, with logs enabling verification of c… | **Reject** | Checker restates the claim at length and confirms it in substance; no error identified (spot-checked) |  |
| 288 | correction | corrected | EU AI Act Art. 26(5) requires deployers to cooperate with market surveillance authorities and implies inves… | **Apply** | Art. 26(5) is monitoring and incident reporting; cooperation is Art. 26(12) | https://eur-lex.europa.eu/eli/reg/2024/1689/oj |
| 289 | correction | corrected | 12 months log retention is recommended for APRA-regulated entities under CPS 234 | **Apply** | CPS 234 sets no log retention period; "12 months recommended (CPS 234)" removed | https://www.apra.gov.au/sites/default/files/cps_234_july_2019_for_public_release.pdf |
| 290 | correction | corrected | GDPR-subject systems processing personal data require 12 months minimum log retention, subject to data mini… | **Apply** | GDPR sets no minimum log retention; storage limitation (Art. 5(1)(e)) applies | https://eur-lex.europa.eu/eli/reg/2016/679/oj |
| 291 | correction | corrected | NIST CSF IDENTIFY.AM is relevant jurisdiction reference for correlation/asset management | **Apply** | CSF identifiers are DE.CM, ID.AM and (CSF 2.0) GV.SC; "DETECT.CM"/"IDENTIFY.SC"/"IDENTIFY.AM" are not | https://nvlpubs.nist.gov/nistpubs/CSWP/NIST.CSWP.29.pdf |
| 292 | review | flagged | Digital Omnibus is Regulation (EU) 2026/1744 and delays Annex III high-risk obligations to 2 December 2027 … | **Reject** | Reg (EU) 2026/1744 Art. 113(c): Annex III from 2 Dec 2027, Annex I from 2 Aug 2028 | https://eur-lex.europa.eu/eli/reg/2026/1744/oj |
| 293 | correction | corrected | OWASP LLM Top 10 2025 and MITRE ATLAS document that standard application logs capture the tool call from a … | **Reject** | Checker restates the claim at length and confirms it in substance; no error identified (spot-checked) |  |

### C1

| # | Kind | Checker status | Claim (abridged) | Decision | Reason | Source |
|---|---|---|---|---|---|---|
| 10 | correction | corrected | MITRE ATLAS technique ID AML.T0020 is 'Training Data Poisoning' (the older ATLAS ID was AML.T0020 'Poison T… | **Reject** | AML.T0020 renamed "Training Data Poisoning" in v2026.07 | https://github.com/mitre-atlas/atlas-data/blob/main/CHANGELOG.md |
| 11 | correction | corrected | OWASP ML01 is the Machine Learning Top 10 identifier for data poisoning (in the OWASP ML Top 10, ML01 is In… | **Apply** | OWASP ML Top 10: data poisoning is ML02; ML01 is Input Manipulation | https://owasp.org/www-project-machine-learning-security-top-10/docs/ML02_2023-Data_Poisoning_Attack |
| 12 | correction | corrected | ISO 42001 Clause 6.3.1 is relevant to data poisoning (ISO/IEC 42001 clause 6.3 is 'Planning of changes'; ve… | **Owner** | "ISO 42001 Cl. 6.3.1" in C1 chip: 6.3 is Planning of changes and has no subclauses under the Harmonized Structure; iso.org text not reachable to confirm. Suggest Cl. 6.1.2/6.1.3 or Annex A | https://www.iso.org/standard/81230.html |
| 13 | correction | corrected | APRA CPS 234 cl. 15 requires information assets to be protected commensurate with criticality (and cl. 16 c… | **Apply** | CPS 234 para 15 is capability, para 16 third parties; controls commensurate with criticality are para 21 | https://www.apra.gov.au/sites/default/files/cps_234_july_2019_for_public_release.pdf |
| 14 | correction | corrected | EU AI Act Art. 10 sets data governance requirements for high-risk AI, including data integrity/bias examina… | **Apply** | Data governance practices are Art. 10(2); 10(3) is data quality | https://eur-lex.europa.eu/eli/reg/2024/1689/oj |
| 15 | correction | corrected | EU AI Act Art. 9 risk management for high-risk AI must address adversarial attacks | **Apply** | Adversarial attacks and data poisoning are in Art. 15(5), not Art. 9 | https://eur-lex.europa.eu/eli/reg/2024/1689/oj |
| 16 | correction | corrected | NIST Cyber AI Profile is designated IR 8596 and includes data pipeline integrity and access control for ML … | **Apply** | IR 8596 is an initial preliminary draft (16 Dec 2025), not a control catalogue | https://csrc.nist.gov/pubs/ir/8596/iprd |
| 17 | correction | corrected | NIST AI 600-1 (Generative AI Profile) explicitly addresses data poisoning and federated learning poisoning … | **Apply** | AI 600-1 names data poisoning (s2.9) but never mentions federated learning | https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf |
| 18 | correction | corrected | SR 11-7 model risk management guidance requires ongoing monitoring and documentation of training data sourc… | **Reject** | Checker restates the claim at length and confirms it in substance; no error identified (spot-checked) |  |
| 19 | review | flagged | ACSC Essential Eight application control and privileged access management (restrict administrative privileg… | **Deferred** | Deferred: lower reader impact; not verified at a primary source this pass |  |
| 20 | review | flagged | EU AI Act high-risk obligations apply from 2 December 2027 for Annex III systems and 2 August 2028 for Anne… | **Reject** | Reg (EU) 2026/1744 Art. 113(c): Annex III from 2 Dec 2027, Annex I from 2 Aug 2028 | https://eur-lex.europa.eu/eli/reg/2026/1744/oj |
| 21 | correction | corrected | Federated learning robust aggregation options: Krum selects the update closest to the majority; Bulyan; coo… | **Deferred** | Deferred: lower reader impact; not verified at a primary source this pass |  |
| 22 | review | flagged | Oil refinery predictive maintenance attack: attackers upload a malicious model component that disables safe… | **Deferred** | Deferred: lower reader impact; not verified at a primary source this pass |  |
| 23 | correction | corrected | Email spam filter poisoning: injecting labelled examples teaches the model to classify malicious emails as … | **Reject** | Checker restates the claim at length and confirms it in substance; no error identified (spot-checked) |  |
| 24 | review | unverifiable | MITRE ATLAS v5.2 and v5.4 (2025) document AI Agent Tool Data Poisoning technique | **Apply** | AML.T0099 added in v5.2 (Dec 2025); v5.4 did not add it | https://github.com/mitre-atlas/atlas-data/blob/main/CHANGELOG.md |
| 25 | review | unverifiable | MITRE ATLAS v5.4 (2025) documents 'Publish Poisoned AI Agent Tool' technique involving malicious plugins/MC… | **Apply** | Publish Poisoned AI Agent Tool added v5.4 (Feb 2026), now AML.T0115.002 since v2026.07 | https://github.com/mitre-atlas/atlas-data/blob/main/CHANGELOG.md |

### C2

| # | Kind | Checker status | Claim (abridged) | Decision | Reason | Source |
|---|---|---|---|---|---|---|
| 26 | review | flagged | OWASP ranks prompt injection first (LLM01) in both the 2025 and 2026 editions of its Top 10 for LLM Applica… | **Reject** | OWASP Top 10 for LLM Applications 2026 exists (4 Aug 2026): LLM03:2026 Excessive Agency, LLM07:2026 Misinformation | https://doi.org/10.5281/zenodo.22109015 |
| 27 | correction | corrected | EU AI Act Art. 15 requires high-risk AI systems to be resilient against attempts to alter their performance… | **Reject** | Checker restates the claim at length and confirms it in substance; no error identified (spot-checked) |  |
| 28 | correction | corrected | EU AI Act Art. 12 requires logging for high-risk AI systems, with a minimum 6-month log retention. | **Apply** | Six-month log retention is in Arts 19(1) and 26(6), not Art. 12 | https://eur-lex.europa.eu/eli/reg/2024/1689/oj |
| 29 | correction | corrected | EU AI Act Art. 9 requires a risk management system (cited as requiring red teaming/testing). | **Reject** | Checker restates the claim at length and confirms it in substance; no error identified (spot-checked) |  |
| 30 | correction | corrected | NIST Cyber AI Profile IR 8596 exists and maps to IDENTIFY.DE, PROTECT.DS and DETECT.CM functions. | **Apply** | IR 8596 builds on CSF 2.0 categories; "IDENTIFY.DE" does not exist; draft status stated | https://nvlpubs.nist.gov/nistpubs/CSWP/NIST.CSWP.29.pdf |
| 31 | review | flagged | DISR AI6 Practice 6 (Australia) recommends system prompt hardening controls. | **Deferred** | Deferred: lower reader impact; not verified at a primary source this pass |  |
| 32 | review | flagged | MITRE ATLAS v5.3 documents data exfiltration via MCP server as a distinct technique. | **Apply** | v5.3 added a case study (AML.CS0045), not a technique | https://github.com/mitre-atlas/atlas-data/blob/main/CHANGELOG.md |
| 33 | correction | corrected | MITRE ATLAS v5.6 added structured documentation of LLM jailbreak techniques in 2025. | **Apply** | AML.T0054 LLM Jailbreak added v4.5 (Oct 2023); v5.6 (Apr 2026) only updated it | https://github.com/mitre-atlas/atlas-data/blob/main/CHANGELOG.md |
| 34 | review | flagged | A 2024 AI customer service agent processing a PDF was injected and forwarded account details to an external… | **Deferred** | Deferred: lower reader impact; not verified at a primary source this pass |  |
| 35 | correction | corrected | Greshake et al. (2023), 'Not What You've Signed Up For', demonstrated resume screener manipulation via whit… | **Reject** | Checker restates the claim at length and confirms it in substance; no error identified (spot-checked) |  |
| 36 | correction | corrected | arXiv:2302.12173 demonstrated an LLM agent with web search hijacked via an attacker-controlled webpage, exf… | **Reject** | Checker restates the claim at length and confirms it in substance; no error identified (spot-checked) |  |
| 37 | review | unverifiable | SalesBleed (Zenity Labs) bypassed the Trusted URLs layer via URL/TLD parsing and exfiltrated CRM account da… | **Reject** | 2026 event after checker cut-off; entry was added with sources (1.4.x/1.5.x); no contrary evidence |  |
| 38 | review | unverifiable | SalesBleed was reported 1 June 2026, fixed and disclosed 24 September 2026, with Salesforce reporting no ex… | **Reject** | 2026 event after checker cut-off; entry was added with sources (1.4.x/1.5.x); no contrary evidence |  |
| 39 | correction | corrected | The EU AI Act applies extraterritorially to any system affecting EU users regardless of where the organisat… | **Reject** | Checker restates the claim at length and confirms it in substance; no error identified (spot-checked) |  |

### C3

| # | Kind | Checker status | Claim (abridged) | Decision | Reason | Source |
|---|---|---|---|---|---|---|
| 55 | review | unverifiable | In February 2026 Anthropic said three AI labs had run more than 16 million exchanges with its Claude models… | **Reject** | ATLAS case study AML.CS0056 (Model Distillation Campaigns Targeting Anthropic Claude, 23 Feb 2026) corroborates; checker cut-off | https://github.com/mitre-atlas/atlas-data/blob/main/CHANGELOG.md |
| 56 | review | unverifiable | Anthropic said three China-based AI labs (DeepSeek, Moonshot AI, MiniMax) ran more than 16 million exchange… | **Reject** | ATLAS case study AML.CS0056 (Model Distillation Campaigns Targeting Anthropic Claude, 23 Feb 2026) corroborates; checker cut-off | https://github.com/mitre-atlas/atlas-data/blob/main/CHANGELOG.md |
| 57 | review | unverifiable | Anthropic disclosure dated 23 February 2026, with reporting by Infosecurity Magazine. | **Reject** | ATLAS case study AML.CS0056 (Model Distillation Campaigns Targeting Anthropic Claude, 23 Feb 2026) corroborates; checker cut-off | https://github.com/mitre-atlas/atlas-data/blob/main/CHANGELOG.md |
| 58 | correction | corrected | NIST IR 8596 Cyber AI Profile was released as a preliminary draft in December 2025, applying CSF 2.0 to sec… | **Reject** | Checker restates the claim at length and confirms it in substance; no error identified (spot-checked) |  |
| 59 | correction | corrected | APRA CPS 234 covers information security capability, including protection of information assets such as ext… | **Reject** | CPS 234 does cover these information assets (paras 15, 21); checker restates it | https://www.apra.gov.au/sites/default/files/cps_234_july_2019_for_public_release.pdf |
| 60 | correction | corrected | Australian Privacy Act APP 11 requires security controls appropriate to prevent unauthorised access to pers… | **Reject** | Checker restates the claim at length and confirms it in substance; no error identified (spot-checked) |  |
| 61 | correction | corrected | MITRE ATLAS technique ID AML.T0005 and OWASP ML05 correspond to model theft/extraction; NIST AI RMF MEASURE… | **Reject** | C3 chip cites AML.T0005 with no name; ATLAS renamed it Replicate AI Model Behavior (v2026.10), which fits model theft; ledger updated | https://github.com/mitre-atlas/atlas-data/blob/main/CHANGELOG.md |

### C4

| # | Kind | Checker status | Claim (abridged) | Decision | Reason | Source |
|---|---|---|---|---|---|---|
| 62 | review | unverifiable | Arup incident logged as AI Incident Database #634 | **Reject** | AIID 634 is the Arup deepfake CFO scam | https://incidentdatabase.ai/cite/634/ |
| 63 | review | unverifiable | Norwegian financial group executives were lured into a video conference with a deepfake CEO instructing fun… | **Deferred** | Deferred: lower reader impact; not verified at a primary source this pass |  |
| 64 | correction | corrected | Deepfake videos of politicians were distributed during the 2024 EU elections to manipulate voter perception | **Reject** | Checker restates the claim at length and confirms it in substance; no error identified (spot-checked) |  |
| 65 | review | unverifiable | A family was extorted for $2,700 in an AI-generated missing-pet scam before their dog was found; a Florida … | **Deferred** | Deferred: lower reader impact; not verified at a primary source this pass |  |
| 66 | correction | corrected | A St Petersburg, Florida woman used AI-generated images in a false crime report (2024) | **Deferred** | Deferred: lower reader impact; not verified at a primary source this pass |  |
| 67 | review | flagged | A woman was convicted for using a ChatGPT-generated image in a false rape accusation | **Deferred** | Deferred: lower reader impact; not verified at a primary source this pass |  |
| 68 | review | flagged | A school incident involved AI-generated deepfake images targeting 21 female students at a single school | **Deferred** | Deferred: lower reader impact; not verified at a primary source this pass |  |
| 69 | review | flagged | MITRE ATLAS v5.6 explicitly categorises deepfake-assisted phishing as an attack technique | **Reject** | Deepfake-Assisted Phishing (AML.T0052.001) added in v5.6.0 | https://github.com/mitre-atlas/atlas-data/blob/main/CHANGELOG.md |
| 70 | review | unverifiable | Ahmedabad, India police arrested four individuals who used deepfake technology to manipulate Aadhaar identi… | **Deferred** | Deferred: lower reader impact; not verified at a primary source this pass |  |
| 71 | review | unverifiable | Providers of systems placed on the market before 2 August 2026 have until 2 December 2026 to meet Art. 50(2… | **Reject** | Reg 2026/1744 inserts Art. 111(4): Art. 50(2) by 2 Dec 2026 for systems on market before 2 Aug 2026 | https://eur-lex.europa.eu/eli/reg/2026/1744/oj |
| 72 | review | flagged | From 2 December 2026, Art. 5 prohibits AI systems generating non-consensual intimate imagery of identifiabl… | **Reject** | Reg 2026/1744 adds Art. 5(1)(ba),(bb) (intimate imagery, CSAM), applying from 2 Dec 2026 | https://eur-lex.europa.eu/eli/reg/2026/1744/oj |
| 73 | correction | corrected | EU PSD2 requires strong customer authentication on high-value transactions | **Deferred** | Deferred: lower reader impact; not verified at a primary source this pass |  |
| 74 | correction | corrected | APRA CPS 234 information security obligations apply to fraud prevention processes and require information s… | **Apply** | CPS 234 contains no awareness-training requirement; reworded to paras 14 and 19 | https://www.apra.gov.au/sites/default/files/cps_234_july_2019_for_public_release.pdf |
| 75 | correction | corrected | ASIC RG 274 and AFCA scheme rules recognise procedural controls as part of a reasonable fraud prevention fr… | **Apply** | RG 274 is product design and distribution obligations; not a fraud-control guide (C4 L113, L248) | https://asic.gov.au/regulatory-resources/find-a-document/regulatory-guides/rg-274-product-design-and-distribution-obligations/ |
| 76 | correction | corrected | FinCEN advisory FIN-2022-A001 on business email compromise extends to deepfake-enabled variants | **Apply** | FIN-2022-A001 is the kleptocracy advisory; email compromise advisory is FIN-2019-A005 | https://www.fincen.gov/resources/advisoriesbulletinsfact-sheets/advisories |
| 77 | correction | corrected | SEC cybersecurity disclosure rules became effective December 2023 and require reporting of material cyberse… | **Apply** | SEC rules effective 5 Sep 2023; incident disclosure from 18 Dec 2023 | https://www.govinfo.gov/content/pkg/FR-2023-08-04/html/2023-16194.htm |
| 78 | correction | corrected | SEC cybersecurity guidance recommends documented staff training programmes for social engineering including… | **Deferred** | Deferred: lower reader impact; not verified at a primary source this pass |  |
| 79 | correction | corrected | DORA requires social engineering including deepfake-enabled fraud to be covered in ICT risk management and … | **Deferred** | Deferred: lower reader impact; not verified at a primary source this pass |  |
| 80 | review | flagged | Detection tools Sensity AI, Intel FakeCatcher, Hive Moderation, Microsoft Video Authenticator were active a… | **Deferred** | Deferred: lower reader impact; not verified at a primary source this pass |  |

### C5

| # | Kind | Checker status | Claim (abridged) | Decision | Reason | Source |
|---|---|---|---|---|---|---|
| 40 | correction | corrected | APRA CPS 234 cl. 19 — controls over access to information assets | **Apply** | Access/implementation of controls is CPS 234 para 21, not 19 (policy framework) | https://www.apra.gov.au/sites/default/files/cps_234_july_2019_for_public_release.pdf |
| 41 | correction | corrected | APRA CPS 234 cl. 21 — detection and response capability required | **Apply** | Detect and respond is CPS 234 para 23; para 21 is implementation of controls | https://www.apra.gov.au/sites/default/files/cps_234_july_2019_for_public_release.pdf |
| 42 | correction | corrected | APRA CPS 234 requires security awareness training for all personnel with access to information assets as an… | **Apply** | CPS 234 contains no awareness-training requirement; reworded to paras 14 and 19 | https://www.apra.gov.au/sites/default/files/cps_234_july_2019_for_public_release.pdf |
| 43 | correction | corrected | NIS2 Art. 21 makes incident detection and response capabilities mandatory; it requires multi-factor authent… | **Reject** | Checker restates the claim at length and confirms it in substance; no error identified (spot-checked) |  |
| 44 | correction | corrected | NIS2 Directive effective October 2024 | **Reject** | NIS2 applied from 18 Oct 2024; "effective October 2024" is accurate |  |
| 45 | correction | corrected | SEC cybersecurity disclosure rules effective December 2023 | **Apply** | SEC rules effective 5 Sep 2023; incident disclosure from 18 Dec 2023 | https://www.govinfo.gov/content/pkg/FR-2023-08-04/html/2023-16194.htm |
| 46 | review | unverifiable | ASD has announced a staged transition from the Essential Eight to a new Essentials series (June 2026); the … | **Reject** | 2026 ASD publications after checker cut-off; cyber.gov.au unreachable this pass (503), search index lists the May 2026 PDF; no contrary evidence | https://www.cyber.gov.au/sites/default/files/2026-05/careful_adoption_of_agentic_ai_services.pdf |
| 47 | review | unverifiable | ASD's ACSC guidance 'Defending against AI-enabled cyber attacks' was published 6 July 2026, with editions f… | **Reject** | 2026 ASD publications after checker cut-off; cyber.gov.au unreachable this pass (503), search index lists the May 2026 PDF; no contrary evidence | https://www.cyber.gov.au/sites/default/files/2026-05/careful_adoption_of_agentic_ai_services.pdf |
| 48 | correction | corrected | Australian university breach of 200,000 records after AI-generated phishing emails mimicking official HR co… | **Owner** | C5 "Australian university breach 200,000 records (illustrative)" mirrors the 2018 ANU breach, which was not AI-generated; relabel clearly as hypothetical or replace |  |
| 49 | correction | corrected | North Korean operatives used LLMs for social engineering schemes targeting financial institutions (August 2… | **Deferred** | Deferred: lower reader impact; not verified at a primary source this pass |  |
| 50 | review | unverifiable | MITRE ATLAS v5.2 documents 'Generate Malicious Commands' as a distinct AI-enabled technique (v5.2.0, 2025) | **Reject** | Generate Malicious Commands (AML.T0102) added in v5.2.0, 24 Dec 2025 | https://github.com/mitre-atlas/atlas-data/blob/main/CHANGELOG.md |
| 51 | review | unverifiable | MITRE ATLAS v5.5 documents 'Machine Compromise' as a technique, including OS credential dumping (added v5.1… | **Apply** | AML.T0112 is compromise of a host via its AI components, not AI-driven exploitation; dates corrected | https://github.com/mitre-atlas/atlas-data/tree/main/dist/v6 |
| 52 | review | verified | NIST Cyber AI Profile IR 8596 exists as a framework for AI-related cybersecurity | **Reject** | Checker itself verified the claim |  |
| 53 | correction | corrected | FFIEC guidance requires security awareness training addressing current threats and strongly encourages zero… | **Deferred** | Deferred: lower reader impact; not verified at a primary source this pass |  |
| 54 | correction | corrected | Zero-trust is the ACSC-recommended architecture framework, and MFA is an Essential Eight control | **Deferred** | Deferred: lower reader impact; not verified at a primary source this pass |  |

### C6

| # | Kind | Checker status | Claim (abridged) | Decision | Reason | Source |
|---|---|---|---|---|---|---|
| 81 | review | flagged | MITRE ATLAS v5.3 documented data exfiltration via MCP server as a named technique (in 2025) | **Apply** | v5.3 added a case study; v5.4 (Feb 2026) added the poisoned-tool technique; years corrected | https://github.com/mitre-atlas/atlas-data/blob/main/CHANGELOG.md |
| 82 | review | unverifiable | MITRE ATLAS v5.4 documented the 'Publish Poisoned AI Agent Tool' technique, covering publishing poisoned MC… | **Apply** | v5.3 added a case study; v5.4 (Feb 2026) added the poisoned-tool technique; years corrected | https://github.com/mitre-atlas/atlas-data/blob/main/CHANGELOG.md |
| 83 | review | unverifiable | MITRE ATLAS technique ID AML.T0110 is 'AI Agent Tool Poisoning' | **Reject** | AML.T0110 is AI Agent Tool Poisoning (v5.5.0) | https://github.com/mitre-atlas/atlas-data/tree/main/dist/v6 |
| 84 | review | unverifiable | The current MITRE ATLAS version is v5.3 (with v5.4 following), as referenced in the framework chip | **Apply** | "ATLAS v5.3" chip replaced by AML.T0115.002 (ATLAS now on calendar versions, v2026.10 current) | https://github.com/mitre-atlas/atlas-data/tree/main/dist/v6 |
| 85 | correction | corrected | OWASP LLM03:2026 is titled 'Excessive Agency' | **Reject** | OWASP Top 10 for LLM Applications 2026 exists (4 Aug 2026): LLM03:2026 Excessive Agency, LLM07:2026 Misinformation | https://doi.org/10.5281/zenodo.22109015 |
| 86 | correction | corrected | NIST AI RMF GOVERN 6.1 covers policies and procedures addressing AI risks from third-party entities, includ… | **Reject** | Checker restates the claim at length and confirms it in substance; no error identified (spot-checked) |  |
| 87 | correction | corrected | EU AI Act Art. 9 risk management requirement is cited as requiring an MCP allowlist and vetting for high-ri… | **Apply** | Art. 9 does not require an MCP allowlist; reworded to "supports" Art. 9 | https://eur-lex.europa.eu/eli/reg/2024/1689/oj |
| 88 | correction | corrected | A minimum of 12 months log retention is recommended for financial services under APRA | **Apply** | CPS 234 sets no log retention period; "12 months recommended (CPS 234)" removed | https://www.apra.gov.au/sites/default/files/cps_234_july_2019_for_public_release.pdf |
| 89 | correction | corrected | GDPR Art. 32 requires appropriate technical security measures for personal data | **Reject** | Checker restates the claim at length and confirms it in substance; no error identified (spot-checked) |  |
| 90 | review | unverifiable | 'Careful Adoption of Agentic AI Services' was published by ASD's ACSC with CISA, NSA, CCCS, NCSC-NZ and NCS… | **Reject** | 2026 ASD publications after checker cut-off; cyber.gov.au unreachable this pass (503), search index lists the May 2026 PDF; no contrary evidence | https://www.cyber.gov.au/sites/default/files/2026-05/careful_adoption_of_agentic_ai_services.pdf |
| 91 | correction | corrected | NIST CSF categories 'IDENTIFY.SC' (supply chain) and 'DETECT.CM' (continuous monitoring) are cited as relev… | **Apply** | CSF identifiers are DE.CM, ID.AM and (CSF 2.0) GV.SC; "DETECT.CM"/"IDENTIFY.SC"/"IDENTIFY.AM" are not | https://nvlpubs.nist.gov/nistpubs/CSWP/NIST.CSWP.29.pdf |
| 92 | review | unverifiable | Garak LLM vulnerability scanner includes MCP scenarios | **Deferred** | Deferred: lower reader impact; not verified at a primary source this pass |  |

### C7

| # | Kind | Checker status | Claim (abridged) | Decision | Reason | Source |
|---|---|---|---|---|---|---|
| 1 | review | unverifiable | MITRE ATLAS v5.3 is a current version of the framework and documents the multi-agent prompt injection attac… | **Apply** | v5.3 added no multi-agent technique; chip now AML.T0143 and L1 text cites LLM Prompt Propagation (Oct 2026) | https://github.com/mitre-atlas/atlas-data/blob/main/CHANGELOG.md |
| 2 | correction | corrected | OWASP LLM03:2026 is 'Excessive Agency' | **Reject** | OWASP Top 10 for LLM Applications 2026 exists (4 Aug 2026): LLM03:2026 Excessive Agency, LLM07:2026 Misinformation | https://doi.org/10.5281/zenodo.22109015 |
| 3 | review | verified | NIST AI 600-1 is relevant to this risk (Generative AI Profile) | **Reject** | Checker itself verified the claim |  |
| 4 | correction | corrected | EU AI Act Art. 15 covers accuracy, robustness and cybersecurity, and is applicable to inter-agent validation | **Reject** | Checker restates the claim at length and confirms it in substance; no error identified (spot-checked) |  |
| 5 | correction | corrected | APRA CPS 234 (information security) is relevant to and recommends these controls in Australia | **Reject** | CPS 234 does cover these information assets (paras 15, 21); checker restates it | https://www.apra.gov.au/sites/default/files/cps_234_july_2019_for_public_release.pdf |
| 6 | correction | corrected | NIST CSF has a 'DETECT.CM' category (continuous monitoring) | **Apply** | CSF identifiers are DE.CM, ID.AM and (CSF 2.0) GV.SC; "DETECT.CM"/"IDENTIFY.SC"/"IDENTIFY.AM" are not | https://nvlpubs.nist.gov/nistpubs/CSWP/NIST.CSWP.29.pdf |
| 7 | review | unverifiable | A publication titled 'Careful Adoption of Agentic AI Services' was issued by ASD's ACSC with CISA, NSA, CCC… | **Reject** | 2026 ASD publications after checker cut-off; cyber.gov.au unreachable this pass (503), search index lists the May 2026 PDF; no contrary evidence | https://www.cyber.gov.au/sites/default/files/2026-05/careful_adoption_of_agentic_ai_services.pdf |
| 8 | review | flagged | MITRE ATLAS v5.3.0 (2025) documented indirect prompt injection in agentic pipelines as a named technique pr… | **Apply** | Incident rewritten: AML.T0143 LLM Prompt Propagation added v2026.10; v5.3 (Jan 2026) had no such technique | https://github.com/mitre-atlas/atlas-data/blob/main/CHANGELOG.md |
| 9 | review | flagged | In 2024 security researchers demonstrated that an injection in an early-stage document processing agent cou… | **Deferred** | Deferred: lower reader impact; not verified at a primary source this pass |  |

### C8

| # | Kind | Checker status | Claim (abridged) | Decision | Reason | Source |
|---|---|---|---|---|---|---|
| 93 | review | unverifiable | MITRE ATLAS v5.3 is a current version and documents computer-use agent hijacking as a named technique | **Apply** | Chip and text now cite AML.T0112.000 and the v5.3/v5.5 case studies; v5.3 added no computer-use technique | https://github.com/mitre-atlas/atlas-data/blob/main/CHANGELOG.md |
| 94 | review | unverifiable | MITRE ATLAS technique ID AML.T0134 is 'AI Targeted Cloaking' | **Reject** | AML.T0134 AI Targeted Cloaking added v2026.09 | https://github.com/mitre-atlas/atlas-data/tree/main/dist/v6 |
| 95 | review | unverifiable | MITRE ATLAS v5.3.0 was published in 2025 | **Apply** | v5.3.0 released 30 Jan 2026, not 2025 | https://github.com/mitre-atlas/atlas-data/blob/main/CHANGELOG.md |
| 96 | correction | corrected | OWASP LLM03:2026 is 'Excessive Agency' | **Reject** | OWASP Top 10 for LLM Applications 2026 exists (4 Aug 2026): LLM03:2026 Excessive Agency, LLM07:2026 Misinformation | https://doi.org/10.5281/zenodo.22109015 |
| 97 | correction | corrected | EU AI Act Art. 15 covers accuracy, robustness and cybersecurity, applicable to isolation and allowlist cont… | **Reject** | Checker restates the claim at length and confirms it in substance; no error identified (spot-checked) |  |
| 98 | correction | corrected | APRA CPS 234 requires security controls for all information assets, including AI agents | **Reject** | CPS 234 does cover these information assets (paras 15, 21); checker restates it | https://www.apra.gov.au/sites/default/files/cps_234_july_2019_for_public_release.pdf |
| 99 | review | unverifiable | 'Careful Adoption of Agentic AI Services' was published by ASD's ACSC with CISA, NSA, CCCS, NCSC-NZ and NCS… | **Reject** | 2026 ASD publications after checker cut-off; cyber.gov.au unreachable this pass (503), search index lists the May 2026 PDF; no contrary evidence | https://www.cyber.gov.au/sites/default/files/2026-05/careful_adoption_of_agentic_ai_services.pdf |
| 100 | correction | corrected | Security researchers demonstrated browser-operating agents redirected by webpage-embedded instructions to e… | **Reject** | Checker restates the claim at length and confirms it in substance; no error identified (spot-checked) |  |

### D1

| # | Kind | Checker status | Claim (abridged) | Decision | Reason | Source |
|---|---|---|---|---|---|---|
| 119 | review | flagged | EU AI Act Art. 10 high-risk obligations apply from 2 December 2027 (Annex III) and 2 August 2028 (Annex I) … | **Reject** | Reg (EU) 2026/1744 Art. 113(c): Annex III from 2 Dec 2027, Annex I from 2 Aug 2028 | https://eur-lex.europa.eu/eli/reg/2026/1744/oj |
| 120 | review | unverifiable | Regulation (EU) 2026/1744 inserted Art. 4a, replacing former Art. 10(5), permitting processing of special c… | **Reject** | Reg 2026/1744 inserts Art. 4a and deletes Art. 10(5) | https://eur-lex.europa.eu/eli/reg/2026/1744/oj |
| 121 | correction | corrected | EU AI Act Art. 10(2) requires training data to be relevant, representative, free of errors, and complete | **Apply** | Art. 10(2)/(3) numbering swapped; Art. 10(5) (not 10(4)) moved to Art. 4a by Reg 2026/1744 | https://eur-lex.europa.eu/eli/reg/2026/1744/oj |
| 122 | correction | corrected | EU AI Act Art. 10(3) requires training data to be subject to data governance practices including examinatio… | **Apply** | Art. 10(2)/(3) numbering swapped; Art. 10(5) (not 10(4)) moved to Art. 4a by Reg 2026/1744 | https://eur-lex.europa.eu/eli/reg/2026/1744/oj |
| 123 | correction | corrected | EU AI Act Art. 10(4) allows special category data processing for bias monitoring where strictly necessary | **Apply** | Art. 10(2)/(3) numbering swapped; Art. 10(5) (not 10(4)) moved to Art. 4a by Reg 2026/1744 | https://eur-lex.europa.eu/eli/reg/2026/1744/oj |
| 124 | correction | corrected | EU AI Act Art. 9(6) requires the risk management system to be updated continuously | **Apply** | Continuous iterative review is Art. 9(2); 9(6) is testing | https://eur-lex.europa.eu/eli/reg/2024/1689/oj |
| 125 | review | unverifiable | APRA issued a letter to industry on AI on 30 April 2026 expecting continuous validation of AI supporting cr… | **Reject** | APRA letter of 30 Apr 2026 confirmed, including these findings | https://www.apra.gov.au/news-and-publications/apra-letter-industry-artificial-intelligence-ai |
| 126 | correction | corrected | CFPB guidance (2023) states AI models in consumer finance must be explainable and auditable | **Reject** | Checker restates the claim at length and confirms it in substance; no error identified (spot-checked) |  |
| 127 | correction | corrected | SR 11-7 applies to all models used by bank holding companies and has explicit expectations for data quality… | **Reject** | Checker restates the claim at length and confirms it in substance; no error identified (spot-checked) |  |
| 128 | correction | corrected | Gender Shades was published in Proceedings of Machine Learning Research 81:1–15, 2018; MIT News February 2018 | **Apply** | Gender Shades is PMLR 81:77-91, not 81:1-15 | https://proceedings.mlr.press/v81/buolamwini18a.html |
| 129 | review | flagged | The Gender Shades research contributed to multiple wrongful arrest cases being re-examined | **Deferred** | Deferred: lower reader impact; not verified at a primary source this pass |  |
| 130 | correction | corrected | Amazon's resume screening AI downgraded applications from women, learned from male-dominated hiring pool, a… | **Reject** | Checker restates the claim at length and confirms it in substance; no error identified (spot-checked) |  |

### D2

| # | Kind | Checker status | Claim (abridged) | Decision | Reason | Source |
|---|---|---|---|---|---|---|
| 143 | review | unverifiable | Samsung incident is catalogued as AI Incident Database #768 and reported by CIO Dive and Gizmodo in April 2023 | **Reject** | AIID 768 is the Samsung ChatGPT leak | https://incidentdatabase.ai/cite/768/ |
| 144 | correction | corrected | Healthcare AI agent exposed sensitive medical patient data while processing healthcare records in September… | **Deferred** | Deferred: lower reader impact; not verified at a primary source this pass |  |
| 145 | review | unverifiable | The Attorney-General's Department released an exposure draft of the Privacy Amendment (Personal Data Protec… | **Reject** | 2026 event after checker cut-off; entry was added with sources (1.4.x/1.5.x); no contrary evidence |  |
| 146 | review | verified | The exposure draft does not include the Privacy Act Review proposal to make PIAs mandatory for high-privacy… | **Reject** | Checker itself verified the claim |  |
| 147 | correction | corrected | GDPR Art. 35 requires a DPIA where processing is likely to result in high risk; Art. 35(3) covers systemati… | **Reject** | Checker restates the claim at length and confirms it in substance; no error identified (spot-checked) |  |
| 148 | correction | corrected | GDPR Art. 29 and Art. 32(4) require employees to process data only on documented instructions of the contro… | **Reject** | Checker restates the claim at length and confirms it in substance; no error identified (spot-checked) |  |
| 149 | correction | corrected | EU AI Act Art. 10 requires high-risk AI systems to use data that is relevant, representative, and free from… | **Reject** | Checker restates the claim at length and confirms it in substance; no error identified (spot-checked) |  |
| 150 | correction | corrected | Australian APP 8 governs cross-border disclosure, APP 11 requires reasonable steps to protect personal info… | **Reject** | Checker restates the claim at length and confirms it in substance; no error identified (spot-checked) |  |
| 151 | correction | corrected | CCPA gives California consumers rights over personal information used in automated decision-making | **Reject** | Checker restates the claim at length and confirms it in substance; no error identified (spot-checked) |  |

### D3

| # | Kind | Checker status | Claim (abridged) | Decision | Reason | Source |
|---|---|---|---|---|---|---|
| 131 | correction | corrected | EU AI Act Art. 53 requires GPAI providers to comply with EU copyright law (the entry also says only provide… | **Apply** | Art. 53(1)(c),(d) copyright policy and training summary apply to all GPAI providers, not only systemic-risk ones | https://eur-lex.europa.eu/eli/reg/2024/1689/oj |
| 132 | review | flagged | Systems placed on the market before 2 August 2026 have until 2 December 2026 to comply with Art. 50, per Ar… | **Reject** | Reg 2026/1744 inserts Art. 111(4): Art. 50(2) by 2 Dec 2026 for systems on market before 2 Aug 2026 | https://eur-lex.europa.eu/eli/reg/2026/1744/oj |
| 133 | correction | corrected | C2PA is emerging as the EU implementation mechanism for Art. 50 synthetic content disclosure. | **Deferred** | Deferred: lower reader impact; not verified at a primary source this pass |  |
| 134 | review | unverifiable | The Australian Standards for AI were announced on 15 July 2026 by the Prime Minister, with legislation expe… | **Reject** | 2026 event after checker cut-off; entry was added with sources (1.4.x/1.5.x); no contrary evidence |  |
| 135 | correction | corrected | Australia has no text and data mining exception for commercial AI training, and the Australian Law Reform C… | **Reject** | Checker restates the claim at length and confirms it in substance; no error identified (spot-checked) |  |
| 136 | correction | corrected | US Copyright Office guidance (2023, 2024) states AI-generated content without sufficient human authorship i… | **Reject** | Checker restates the claim at length and confirms it in substance; no error identified (spot-checked) |  |
| 137 | correction | corrected | Oracle v. Google established that copyright in software APIs is enforceable. | **Apply** | Google v. Oracle (2021) held fair use and assumed, without deciding, copyrightability | https://www.supremecourt.gov/opinions/20pdf/18-956_d18f.pdf |
| 138 | correction | corrected | Authors Guild v. OpenAI and related cases (2023–2025) are defining the US framework on fair use for AI trai… | **Reject** | Checker restates the claim at length and confirms it in substance; no error identified (spot-checked) |  |
| 139 | correction | corrected | DMCA safe harbour does not apply to training data infringement. | **Reject** | Checker restates the claim at length and confirms it in substance; no error identified (spot-checked) |  |
| 140 | correction | corrected | GitHub Advanced Security/Copilot includes a code referencing feature that identifies when suggestions match… | **Reject** | Checker restates the claim at length and confirms it in substance; no error identified (spot-checked) |  |
| 141 | review | unverifiable | Documented 2025 case: AI tool generated short video clips described as nearly identical to sequences from a… | **Reject** | 2026 event after checker cut-off; entry was added with sources (1.4.x/1.5.x); no contrary evidence |  |
| 142 | review | flagged | Recommended minimum retention of 7 years for regulatory correspondence, contract documents, and financial m… | **Deferred** | Deferred: lower reader impact; not verified at a primary source this pass |  |

### E1

| # | Kind | Checker status | Claim (abridged) | Decision | Reason | Source |
|---|---|---|---|---|---|---|
| 178 | correction | corrected | The SafeRent settlement was $2.275M with final approval in December 2024 | **Owner** | E1 says SafeRent final approval December 2024; A4 (re-verified 14 Oct) says November 2024. Align E1 with A4's source |  |
| 179 | correction | corrected | SafeRent settlement was certified in April 2024 with final court approval in December 2024 | **Owner** | E1 says SafeRent final approval December 2024; A4 (re-verified 14 Oct) says November 2024. Align E1 with A4's source |  |
| 180 | correction | corrected | SafeRent's AI screening used housing voucher status as a proxy for race, disproportionately harming Black a… | **Deferred** | Deferred: lower reader impact; not verified at a primary source this pass |  |
| 181 | review | unverifiable | GAO-25-107196 is a source relevant to the SafeRent case | **Deferred** | Deferred: lower reader impact; not verified at a primary source this pass |  |
| 182 | correction | corrected | EU AI Act Article 86 gives a right to explanation when a high-risk AI system contributed to a decision sign… | **Reject** | Checker restates the claim at length and confirms it in substance; no error identified (spot-checked) |  |
| 183 | correction | corrected | EU AI Act Art. 10 requires high-risk AI training data to be representative and free from errors and bias, a… | **Reject** | Checker restates the claim at length and confirms it in substance; no error identified (spot-checked) |  |
| 184 | correction | corrected | EU AI Act Art. 10 and Recital 44 address accuracy and bias-free operation | **Reject** | Checker restates the claim at length and confirms it in substance; no error identified (spot-checked) |  |
| 185 | correction | corrected | EU AI Act Art. 62 requires providers of high-risk AI systems to cooperate with market surveillance authorities | **Apply** | Cooperation with authorities is Art. 21; Art. 62 is support for SMEs | https://eur-lex.europa.eu/eli/reg/2024/1689/oj |
| 186 | correction | corrected | EU AI Act Art. 9 risk management obligations include testing by qualified parties | **Reject** | Checker restates the claim at length and confirms it in substance; no error identified (spot-checked) |  |
| 187 | review | flagged | EU AI Act high-risk provisions for Annex III systems apply from 2 December 2027, deferred from 2 August 202… | **Reject** | Reg (EU) 2026/1744 Art. 113(c): Annex III from 2 Dec 2027, Annex I from 2 Aug 2028 | https://eur-lex.europa.eu/eli/reg/2026/1744/oj |
| 188 | correction | corrected | Colorado SB21-169 requires an external fairness audit for insurance AI systems, with annual external bias a… | **Deferred** | Legal or regulatory detail needs a source not fetched this pass (court record, statute or agency page) |  |
| 189 | correction | corrected | CFPB guidance on AI and credit (2022) requires lenders to be able to explain adverse actions, and the 2022 … | **Reject** | Checker restates the claim at length and confirms it in substance; no error identified (spot-checked) |  |
| 190 | review | flagged | AHRC guidance on automated decision-making (2023) recommends pre-deployment bias assessment | **Deferred** | Deferred: lower reader impact; not verified at a primary source this pass |  |
| 191 | correction | corrected | AHRC's Human Rights and Technology report recommends independent auditing for high-risk automated decisions | **Reject** | Checker restates the claim at length and confirms it in substance; no error identified (spot-checked) |  |
| 192 | review | unverifiable | APRA's letter to industry on AI (30 April 2026) found point-in-time, sample-based assurance ill-suited to A… | **Reject** | APRA letter of 30 Apr 2026 confirmed, including these findings | https://www.apra.gov.au/news-and-publications/apra-letter-industry-artificial-intelligence-ai |
| 193 | correction | corrected | ASIC RG 271 (internal dispute resolution) requires firms to monitor AI-driven complaint patterns for system… | **Deferred** | Legal or regulatory detail needs a source not fetched this pass (court record, statute or agency page) |  |
| 194 | correction | corrected | UK Home Office visa AI (2020) flagged applications from certain nationalities at higher rates than statisti… | **Deferred** | Legal or regulatory detail needs a source not fetched this pass (court record, statute or agency page) |  |
| 195 | correction | corrected | More than fourteen individuals have been wrongfully arrested in the US due to facial recognition misidentif… | **Owner** | E1 "more than fourteen" wrongful arrests: counts vary by source; choose a sourced figure |  |
| 196 | correction | corrected | Gender Shades study (Buolamwini & Gebru, PMLR 81:1–15, 2018) found higher error rates for darker-skinned in… | **Apply** | Gender Shades is PMLR 81:77-91, not 81:1-15 | https://proceedings.mlr.press/v81/buolamwini18a.html |

### E2

| # | Kind | Checker status | Claim (abridged) | Decision | Reason | Source |
|---|---|---|---|---|---|---|
| 152 | correction | corrected | EU AI Act Art. 5 prohibits manipulation of vulnerable persons, social scoring, and real-time biometric ID a… | **Deferred** | Deferred: lower reader impact; not verified at a primary source this pass |  |
| 153 | review | unverifiable | From 2 December 2026, Art. 5 (as amended by Regulation (EU) 2026/1744) prohibits AI systems generating non-… | **Reject** | Reg 2026/1744 adds Art. 5(1)(ba),(bb) (intimate imagery, CSAM), applying from 2 Dec 2026 | https://eur-lex.europa.eu/eli/reg/2026/1744/oj |
| 154 | review | unverifiable | Application dates for Art. 73 serious incident reporting deferred by Regulation (EU) 2026/1744 | **Owner** | E2 says Art. 73 dates were "deferred": Reg 2026/1744 does not amend Art. 73 dates; the effect follows from high-risk classification applying later. Decide wording | https://eur-lex.europa.eu/eli/reg/2026/1744/oj |
| 155 | review | flagged | Art. 50(2) machine-readable marking by providers applies 2 December 2026 for systems already on the market … | **Reject** | Reg 2026/1744 inserts Art. 111(4): Art. 50(2) by 2 Dec 2026 for systems on market before 2 Aug 2026 | https://eur-lex.europa.eu/eli/reg/2026/1744/oj |
| 156 | correction | corrected | GPAI Code of Practice (2025) treats red teaming as an explicit expected control for GPAI providers | **Deferred** | Deferred: lower reader impact; not verified at a primary source this pass |  |
| 157 | correction | corrected | EO 14110 requires dual-use foundation model providers to conduct red teaming before deployment | **Apply** | EO 14110 revoked by EO 14148 (20 Jan 2025); E2 and G4 described it as current | https://www.govinfo.gov/content/pkg/FR-2025-01-28/html/2025-01901.htm |
| 158 | correction | corrected | GDPR Art. 8 requires parental consent for children under 16 (member states may lower to 13) | **Reject** | Checker restates the claim at length and confirms it in substance; no error identified (spot-checked) |  |
| 159 | correction | corrected | DSA very large online platforms are defined as those with more than 45M EU users and face systemic risk ass… | **Reject** | Checker restates the claim at length and confirms it in substance; no error identified (spot-checked) |  |
| 160 | correction | corrected | AI-generated CSAM is explicitly included under the PROTECT Act | **Apply** | PROTECT Act predates generative AI; 18 USC 2256(8)(B) covers indistinguishable computer-generated images | https://www.govinfo.gov/link/uscode/18/2256 |
| 161 | correction | corrected | California SB 1047 and Colorado HB 1468 impose content safety obligations on AI developers and deployers | **Deferred** | High priority next pass: E2 cites California SB 1047 (vetoed Sept 2024 per checker) and "Colorado HB 1468" as imposing obligations; primary sources not fetched |  |
| 162 | review | flagged | Tasmanian man sentenced in Launceston Supreme Court on 26 March 2024 for possessing and accessing AI-genera… | **Deferred** | Deferred: lower reader impact; not verified at a primary source this pass |  |
| 163 | correction | corrected | Grok AI produced hateful content in July 2025; developer issued public apology and modified the model | **Reject** | Checker restates the claim at length and confirms it in substance; no error identified (spot-checked) |  |
| 164 | review | flagged | India's NIA filed a chargesheet on 14 May 2026 in the 10 November 2025 Red Fort car bombing that killed 11 … | **Reject** | 2026 event after checker cut-off; entry was added with sources (1.4.x/1.5.x); no contrary evidence |  |
| 165 | review | unverifiable | NIA chargesheet states an accused 'engineer' used ChatGPT and YouTube to research rockets and IEDs | **Reject** | 2026 event after checker cut-off; entry was added with sources (1.4.x/1.5.x); no contrary evidence |  |
| 166 | review | unverifiable | A 17-year-old from Sarthe, France was placed under formal investigation in 2025 for planning jihadist attac… | **Reject** | 2026 event after checker cut-off; entry was added with sources (1.4.x/1.5.x); no contrary evidence |  |
| 167 | review | unverifiable | AI Incident Database incident 1742 relates to chatbots used in attack planning | **Reject** | AIID 1742 is the Sarthe chatbot attack-planning case | https://incidentdatabase.ai/cite/1742/ |
| 168 | correction | corrected | Multiple legal cases (2023–2025) in US courts alleged AI chatbots reinforced teen suicidal ideation | **Deferred** | Deferred: lower reader impact; not verified at a primary source this pass |  |

### E3

| # | Kind | Checker status | Claim (abridged) | Decision | Reason | Source |
|---|---|---|---|---|---|---|
| 169 | correction | corrected | EU AI Act Art. 50(4): deployers must disclose deep fakes and AI-generated text published to inform the publ… | **Reject** | Checker restates the claim at length and confirms it in substance; no error identified (spot-checked) |  |
| 170 | review | unverifiable | Providers of generative systems placed on the market before 2 August 2026 have until 2 December 2026 to mee… | **Reject** | Reg 2026/1744 inserts Art. 111(4): Art. 50(2) by 2 Dec 2026 for systems on market before 2 Aug 2026 | https://eur-lex.europa.eu/eli/reg/2026/1744/oj |
| 171 | review | unverifiable | Australian Standards for AI announced by the Prime Minister on 15 July 2026, overseen by a new Office of AI… | **Reject** | 2026 event after checker cut-off; entry was added with sources (1.4.x/1.5.x); no contrary evidence |  |
| 172 | review | flagged | California AB 2655 was struck down in August 2025 as preempted by Section 230 (Kohls v. Bonta, E.D. Cal.); … | **Deferred** | Legal or regulatory detail needs a source not fetched this pass (court record, statute or agency page) |  |
| 173 | correction | corrected | FTC guidance on AI and deception (2023) indicates undisclosed AI personas may be deceptive under Section 5;… | **Reject** | Checker restates the claim at length and confirms it in substance; no error identified (spot-checked) |  |
| 174 | review | unverifiable | An AI-generated image of Barack Obama DJing in Arizona was shared widely, reaching millions of people | **Deferred** | Deferred: lower reader impact; not verified at a primary source this pass |  |
| 175 | correction | corrected | AI-generated deepfake videos of politicians were distributed during the 2024 EU elections to manipulate vot… | **Reject** | Checker restates the claim at length and confirms it in substance; no error identified (spot-checked) |  |
| 176 | correction | corrected | GDPR Art. 22 safeguards apply to automated decisions affecting individuals | **Reject** | Checker restates the claim at length and confirms it in substance; no error identified (spot-checked) |  |
| 177 | correction | corrected | APRA CPS 234 imposes security awareness training obligations | **Apply** | CPS 234 contains no awareness-training requirement; reworded to paras 14 and 19 | https://www.apra.gov.au/sites/default/files/cps_234_july_2019_for_public_release.pdf |

### F1

| # | Kind | Checker status | Claim (abridged) | Decision | Reason | Source |
|---|---|---|---|---|---|---|
| 308 | review | unverifiable | APRA's letter to industry on AI was issued on 30 April 2026 and applies existing prudential standards to AI. | **Reject** | APRA letter of 30 Apr 2026 confirmed, including these findings | https://www.apra.gov.au/news-and-publications/apra-letter-industry-artificial-intelligence-ai |
| 309 | review | unverifiable | The APRA letter found board oversight and assurance lagging AI adoption, and that boards were still buildin… | **Reject** | APRA letter of 30 Apr 2026 confirmed, including these findings | https://www.apra.gov.au/news-and-publications/apra-letter-industry-artificial-intelligence-ai |
| 310 | review | unverifiable | The APRA letter found point-in-time, sample-based assurance ill-suited to AI, with few entities continuousl… | **Reject** | APRA letter of 30 Apr 2026 confirmed, including these findings | https://www.apra.gov.au/news-and-publications/apra-letter-industry-artificial-intelligence-ai |
| 311 | correction | corrected | APRA CPS 234 imposes a security awareness training obligation. | **Apply** | CPS 234 contains no awareness-training requirement; reworded to paras 14 and 19 | https://www.apra.gov.au/sites/default/files/cps_234_july_2019_for_public_release.pdf |
| 312 | correction | corrected | US SR 11-7 model risk management guidance requires validation, ongoing monitoring, documentation of limitat… | **Reject** | Checker restates the claim at length and confirms it in substance; no error identified (spot-checked) |  |
| 313 | correction | corrected | EEOC technical assistance on AI in employment decisions (2023) says employers remain responsible for AI-ass… | **Owner** | B1, F1, F3 cite the May 2023 EEOC technical assistance as current; B3 removed it as withdrawn (Oct 2026). Confirm and align |  |
| 314 | review | unverifiable | In 2026 an Oklahoma judge acknowledged that an order he issued cited two non-existent cases found through C… | **Reject** | 2026 event after checker cut-off; entry was added with sources (1.4.x/1.5.x); no contrary evidence |  |

### F2

| # | Kind | Checker status | Claim (abridged) | Decision | Reason | Source |
|---|---|---|---|---|---|---|
| 315 | correction | corrected | Engineers submitted proprietary source code for bug fixing, code optimisation, and meeting transcription. | **Reject** | Checker restates the claim at length and confirms it in substance; no error identified (spot-checked) |  |
| 316 | review | unverifiable | The Samsung incident is catalogued as AI Incident Database #768 and reported by CIO Dive and Gizmodo in Apr… | **Reject** | AIID 768 is the Samsung ChatGPT leak | https://incidentdatabase.ai/cite/768/ |
| 317 | review | unverifiable | EU AI Act Art. 4 (AI literacy) is amended from 27 July 2026 by Regulation (EU) 2026/1744. | **Reject** | Reg 2026/1744 replaces Art. 4 ("take measures to support" AI literacy), in force 27 Jul 2026 | https://eur-lex.europa.eu/eli/reg/2026/1744/oj |
| 318 | correction | corrected | EU AI Act Art. 4 asks providers and deployers to take measures to support AI literacy; Art. 26 deployer obl… | **Reject** | Reg 2026/1744 replaces Art. 4 ("take measures to support" AI literacy), in force 27 Jul 2026 | https://eur-lex.europa.eu/eli/reg/2026/1744/oj |
| 319 | correction | corrected | GDPR Art. 28 requires a Data Processing Agreement for processors; Art. 29 / Art. 32(4) require processing o… | **Reject** | Checker restates the claim at length and confirms it in substance; no error identified (spot-checked) |  |
| 320 | correction | corrected | GDPR Art. 44–49 cover international data transfers, requiring Standard Contractual Clauses or equivalent fo… | **Reject** | Checker restates the claim at length and confirms it in substance; no error identified (spot-checked) |  |

### F3

| # | Kind | Checker status | Claim (abridged) | Decision | Reason | Source |
|---|---|---|---|---|---|---|
| 300 | correction | corrected | EU AI Act Art. 26 sets deployer obligations; using an AI system outside its intended purpose breaches these… | **Reject** | Checker restates the claim at length and confirms it in substance; no error identified (spot-checked) |  |
| 301 | correction | corrected | EU AI Act Annex IV requires technical documentation to include the intended purpose and the conditions unde… | **Deferred** | Deferred: lower reader impact; not verified at a primary source this pass |  |
| 302 | correction | corrected | EU AI Act Art. 25 requires reassessment for substantial modifications, and a change causing a general-purpo… | **Apply** | Reassessment after substantial modification is Art. 43(4); Art. 25(1) decides who becomes provider | https://eur-lex.europa.eu/eli/reg/2024/1689/oj |
| 303 | correction | corrected | For GPAI models, providers must document intended uses and prohibited uses; deployers are responsible for e… | **Reject** | Checker restates the claim at length and confirms it in substance; no error identified (spot-checked) |  |
| 304 | review | unverifiable | APRA issued a letter to industry on AI dated 30 April 2026 expecting continuous validation of AI supporting… | **Reject** | APRA letter of 30 Apr 2026 confirmed, including these findings | https://www.apra.gov.au/news-and-publications/apra-letter-industry-artificial-intelligence-ai |
| 305 | correction | corrected | Privacy Act APP 3 requires that personal information collected for one purpose is not used for an incompati… | **Owner** | F3 cites APP 3 for secondary use; APP 6 governs use and disclosure. OAIC returned 403, so not confirmed at source; likely a one-word fix |  |
| 306 | correction | corrected | SR 11-7 requires model documentation including purpose and appropriate use, use within validated range, new… | **Reject** | Checker restates the claim at length and confirms it in substance; no error identified (spot-checked) |  |
| 307 | correction | corrected | EEOC technical assistance on AI in employment states that AI must not be used beyond validated and document… | **Owner** | B1, F1, F3 cite the May 2023 EEOC technical assistance as current; B3 removed it as withdrawn (Oct 2026). Confirm and align |  |

### F4

| # | Kind | Checker status | Claim (abridged) | Decision | Reason | Source |
|---|---|---|---|---|---|---|
| 294 | correction | corrected | OWASP lists Excessive Agency as LLM03:2026 in the 2026 edition of the Top 10 for LLM Applications | **Reject** | OWASP Top 10 for LLM Applications 2026 exists (4 Aug 2026): LLM03:2026 Excessive Agency, LLM07:2026 Misinformation | https://doi.org/10.5281/zenodo.22109015 |
| 295 | review | unverifiable | A publication titled 'Careful Adoption of Agentic AI Services' was issued by ASD's ACSC with CISA, NSA, CCC… | **Reject** | 2026 ASD publications after checker cut-off; cyber.gov.au unreachable this pass (503), search index lists the May 2026 PDF; no contrary evidence | https://www.cyber.gov.au/sites/default/files/2026-05/careful_adoption_of_agentic_ai_services.pdf |
| 296 | review | flagged | In 2025 an AI agent at Meta gave inaccurate technical advice that led an employee to take actions causing a… | **Deferred** | Deferred: lower reader impact; not verified at a primary source this pass |  |
| 297 | review | unverifiable | ASD's ACSC published an alert 'Risks of AI misalignment to Australian organisations' on 24 September 2026 | **Reject** | 2026 ASD publications after checker cut-off; cyber.gov.au unreachable this pass (503), search index lists the May 2026 PDF; no contrary evidence | https://www.cyber.gov.au/sites/default/files/2026-05/careful_adoption_of_agentic_ai_services.pdf |
| 298 | review | unverifiable | ASD's ACSC reported an AI agent blocked by security controls on an organisation's public-facing website tha… | **Reject** | 2026 ASD publications after checker cut-off; cyber.gov.au unreachable this pass (503), search index lists the May 2026 PDF; no contrary evidence | https://www.cyber.gov.au/sites/default/files/2026-05/careful_adoption_of_agentic_ai_services.pdf |
| 299 | review | unverifiable | ASD found no indication of a broader threat or malicious targeting, and recommended strong authentication a… | **Reject** | 2026 ASD publications after checker cut-off; cyber.gov.au unreachable this pass (503), search index lists the May 2026 PDF; no contrary evidence | https://www.cyber.gov.au/sites/default/files/2026-05/careful_adoption_of_agentic_ai_services.pdf |

### G1

| # | Kind | Checker status | Claim (abridged) | Decision | Reason | Source |
|---|---|---|---|---|---|---|
| 209 | correction | corrected | DORA Art. 28 covers ICT third-party concentration risk management | **Apply** | DORA concentration risk is Art. 29; continuity-plan testing is Art. 11(6), not Art. 25 (tool testing) | https://eur-lex.europa.eu/eli/reg/2022/2554/oj |
| 210 | correction | corrected | DORA Art. 11 requires business continuity policies addressing ICT third-party disruption | **Reject** | Checker restates the claim at length and confirms it in substance; no error identified (spot-checked) |  |
| 211 | correction | corrected | DORA Art. 25 requires testing of continuity plans for significant ICT providers / ICT business continuity t… | **Apply** | DORA concentration risk is Art. 29; continuity-plan testing is Art. 11(6), not Art. 25 (tool testing) | https://eur-lex.europa.eu/eli/reg/2022/2554/oj |
| 212 | correction | corrected | APRA CPS 230 cl. 35 requires contracts with material service providers to include termination provisions an… | **Apply** | CPS 230 termination provisions are para 54(g), orderly exit para 56; there is no cl. 35 on contracts | https://www.apra.gov.au/sites/default/files/2023-07/Prudential%20Standard%20CPS%20230%20Operational%20Risk%20Management%20-%20clean.pdf |
| 213 | review | flagged | CPS 230 cl. 37 requires APRA-regulated entities not to place excessive reliance on individual service provi… | **Reject** | No "CPS 230 cl. 37" text exists in G1; nothing to change | https://www.apra.gov.au/sites/default/files/2023-07/Prudential%20Standard%20CPS%20230%20Operational%20Risk%20Management%20-%20clean.pdf |
| 214 | correction | corrected | CPS 220 operational risk management must address third-party concentration risk | **Apply** | Concentration risk is CPS 230 para 53(b), not CPS 220 | https://www.apra.gov.au/sites/default/files/2023-07/Prudential%20Standard%20CPS%20230%20Operational%20Risk%20Management%20-%20clean.pdf |
| 215 | correction | corrected | SR 11-7 model risk management guidance requires critical AI models to have documented fallback arrangements | **Reject** | Checker restates the claim at length and confirms it in substance; no error identified (spot-checked) |  |
| 216 | correction | corrected | Google Gemini API version deprecations forced migration, often with limited notice | **Reject** | Checker restates the claim at length and confirms it in substance; no error identified (spot-checked) |  |
| 217 | correction | corrected | NIST AI RMF has a MANAGE 4 function/category relevant to concentration risk | **Reject** | Checker restates the claim at length and confirms it in substance; no error identified (spot-checked) |  |

### G2

| # | Kind | Checker status | Claim (abridged) | Decision | Reason | Source |
|---|---|---|---|---|---|---|
| 226 | review | flagged | The SEC stopped defending its climate rules in 2025 and proposed rescinding them in May 2026 | **Reject** | 2026 event after checker cut-off; entry was added with sources (1.4.x/1.5.x); no contrary evidence |  |
| 227 | review | verified | California SB 253 faces a federal challenge and Scope 3 rules are still being finalised | **Reject** | Checker itself verified the claim |  |

### G3

| # | Kind | Checker status | Claim (abridged) | Decision | Reason | Source |
|---|---|---|---|---|---|---|
| 228 | correction | corrected | Most Modern Awards in Australia include a model consultation clause requiring 28 days' notice of significan… | **Apply** | Award consultation clause (e.g. Clerks Award cl. 38) sets no 28-day notice period | https://awards.fairwork.gov.au/MA000002.html |
| 229 | correction | corrected | Under the Fair Work Act 2009, a genuine redundancy requires that the employer could not reasonably redeploy… | **Reject** | Checker restates the claim at length and confirms it in substance; no error identified (spot-checked) |  |
| 230 | review | unverifiable | EU AI Act Art. 4 requires providers and deployers to take measures to support AI literacy of staff; softene… | **Reject** | Reg 2026/1744 replaces Art. 4 ("take measures to support" AI literacy), in force 27 Jul 2026 | https://eur-lex.europa.eu/eli/reg/2026/1744/oj |
| 231 | correction | corrected | CSRD social reporting standard (ESRS S1) includes disclosure of workforce management practices, including t… | **Reject** | Checker restates the claim at length and confirms it in substance; no error identified (spot-checked) |  |
| 232 | review | flagged | State-level US AI workforce legislation exists: California AB 1186 and Maryland HB 682; no federal AI-speci… | **Deferred** | Legal or regulatory detail needs a source not fetched this pass (court record, statute or agency page) |  |
| 233 | correction | corrected | AIIA and DISR voluntary AI Safety Standard treats workforce impact as a core ethical consideration (Australia) | **Reject** | Checker restates the claim at length and confirms it in substance; no error identified (spot-checked) |  |
| 234 | correction | corrected | In Australian redundancy disputes, FWC decisions consider whether the employer took reasonable steps to red… | **Reject** | Checker restates the claim at length and confirms it in substance; no error identified (spot-checked) |  |
| 235 | correction | corrected | AI-driven content moderation replaced contractor workforces in 2023–2024, significantly impacting contracto… | **Deferred** | Deferred: lower reader impact; not verified at a primary source this pass |  |

### G4

| # | Kind | Checker status | Claim (abridged) | Decision | Reason | Source |
|---|---|---|---|---|---|---|
| 197 | correction | corrected | Apollo Research findings (September 2025) confirmed that current frontier models exhibit deliberate decepti… | **Deferred** | Deferred: lower reader impact; not verified at a primary source this pass |  |
| 198 | correction | corrected | EU AI Act Art. 9 requires risk management including analysis of risks from intended purpose and foreseeable… | **Reject** | Checker restates the claim at length and confirms it in substance; no error identified (spot-checked) |  |
| 199 | correction | corrected | The GPAI Code of Practice (2025) includes specific expectations on agentic AI safety including minimal foot… | **Deferred** | Deferred: lower reader impact; not verified at a primary source this pass |  |
| 200 | correction | corrected | NIST AI RMF MANAGE 1.3 covers responses to AI risks including staged deployment as a mitigation approach | **Reject** | Checker restates the claim at length and confirms it in substance; no error identified (spot-checked) |  |
| 201 | correction | corrected | NIST AI 600-1 explicitly addresses minimal footprint, human-in-the-loop for irreversible actions, and kill … | **Apply** | AI 600-1 has no minimal-footprint, kill-switch or agentic provisions (G4 L91, L257) | https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf |
| 202 | correction | corrected | NIST Cyber AI Profile is designated IR 8596 and addresses security dimensions of agentic AI including acces… | **Reject** | Checker restates the claim at length and confirms it in substance; no error identified (spot-checked) |  |
| 203 | correction | corrected | EO 14110 safety requirements for dual-use foundation models extend to agentic capabilities (EO 14110 status… | **Apply** | EO 14110 revoked by EO 14148 (20 Jan 2025); E2 and G4 described it as current | https://www.govinfo.gov/content/pkg/FR-2025-01-28/html/2025-01901.htm |
| 204 | review | unverifiable | APRA's letter to industry on AI (30 April 2026) states that existing prudential standards (CPS 220, CPS 230… | **Apply** | Letter does not name CPS 220/230/234 and asks for "credible fallback processes", not "tested" | https://www.apra.gov.au/news-and-publications/apra-letter-industry-artificial-intelligence-ai |
| 205 | correction | corrected | APRA CPS 234 applies the principle of least privilege to information systems | **Apply** | CPS 234 does not mention least privilege; reworded to para 21 | https://www.apra.gov.au/sites/default/files/cps_234_july_2019_for_public_release.pdf |
| 206 | correction | corrected | ASIC has signalled interest in AI agent governance for financial services, with robo-advice and AI-driven t… | **Deferred** | Deferred: lower reader impact; not verified at a primary source this pass |  |
| 207 | correction | corrected | The DISR voluntary AI Safety Standard expects phased deployment and testing for high-risk AI systems | **Deferred** | Deferred: lower reader impact; not verified at a primary source this pass |  |
| 208 | correction | corrected | Anthropic's responsible scaling policy and OpenAI's safety practices include objective specification review… | **Deferred** | Deferred: lower reader impact; not verified at a primary source this pass |  |

### G5

| # | Kind | Checker status | Claim (abridged) | Decision | Reason | Source |
|---|---|---|---|---|---|---|
| 218 | review | flagged | OWASP ranks Excessive Agency third (LLM03:2026) in its 2026 Top 10 for LLM Applications, up from sixth (LLM… | **Reject** | OWASP Top 10 for LLM Applications 2026 exists (4 Aug 2026): LLM03:2026 Excessive Agency, LLM07:2026 Misinformation | https://doi.org/10.5281/zenodo.22109015 |
| 219 | review | flagged | OWASP LLM03:2026 Excessive Agency was LLM06 in the 2025 list. | **Reject** | OWASP Top 10 for LLM Applications 2026 exists (4 Aug 2026): LLM03:2026 Excessive Agency, LLM07:2026 Misinformation | https://doi.org/10.5281/zenodo.22109015 |
| 220 | correction | corrected | Privacy Act APP 6 (use and disclosure limitation) applies to agent-initiated data handling. | **Reject** | Checker restates the claim at length and confirms it in substance; no error identified (spot-checked) |  |
| 221 | review | unverifiable | 'Careful Adoption of Agentic AI Services' was published by ASD's ACSC with CISA, NSA, CCCS, NCSC-NZ and NCS… | **Reject** | 2026 ASD publications after checker cut-off; cyber.gov.au unreachable this pass (503), search index lists the May 2026 PDF; no contrary evidence | https://www.cyber.gov.au/sites/default/files/2026-05/careful_adoption_of_agentic_ai_services.pdf |
| 222 | review | unverifiable | OWASP's 2026 preface calls the move of Excessive Agency to LLM03:2026 the most consequential change on the … | **Reject** | 2026 edition confirmed; preface wording not checked, no evidence against the KB | https://doi.org/10.5281/zenodo.22109015 |
| 223 | review | flagged | An AI agent at Meta provided inaccurate technical advice that led an employee to take actions causing a sec… | **Deferred** | Deferred: lower reader impact; not verified at a primary source this pass |  |
| 224 | review | unverifiable | ASD's ACSC issued a high alert, 'Risks of AI misalignment to Australian organisations', on 24 September 2026. | **Reject** | 2026 ASD publications after checker cut-off; cyber.gov.au unreachable this pass (503), search index lists the May 2026 PDF; no contrary evidence | https://www.cyber.gov.au/sites/default/files/2026-05/careful_adoption_of_agentic_ai_services.pdf |
| 225 | review | unverifiable | In the ASD ACSC alert scenario, an agent whose task was blocked by security controls on an organisation's p… | **Reject** | 2026 ASD publications after checker cut-off; cyber.gov.au unreachable this pass (503), search index lists the May 2026 PDF; no contrary evidence | https://www.cyber.gov.au/sites/default/files/2026-05/careful_adoption_of_agentic_ai_services.pdf |
