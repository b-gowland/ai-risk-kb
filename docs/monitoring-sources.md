---
id: monitoring-sources
title: Monitoring Sources
sidebar_position: 4
---

# Monitoring sources

The knowledge base tracks a fixed set of sources that a scheduled job can check automatically. A source is listed here only if the automation polls it. The list is defined in [`automation/monitoring/poll-sources.py`](https://github.com/b-gowland/ai-risk-kb/blob/main/automation/monitoring/poll-sources.py).

## Sources polled weekly

Each source is checked every Monday at 10:00 UTC.

| Source | What it covers | How it is checked |
|--------|----------------|-------------------|
| [AI Incident Database](https://incidentdatabase.ai) | Real-world AI incidents, used for incident examples | RSS feed; reports are grouped so each incident appears once |
| [MITRE ATLAS](https://atlas.mitre.org) | Adversarial techniques, mitigations and case studies for AI systems | Release feed of the `mitre-atlas/atlas-data` GitHub repository |
| [OWASP Top 10 for LLM Applications](https://genai.owasp.org/llm-top-10/) | Vulnerability list for LLM applications | Watches the "Current release" line in the project's GitHub README, so a new edition is flagged |
| [MIT AI Risk Repository](https://airisk.mit.edu) | Taxonomy and database of AI risks | New posts on the repository's blog |
| [UK AI Security Institute](https://www.aisi.gov.uk) | Research and evaluations on frontier AI safety and security | Community-maintained RSS mirror of the AISI blog, because AISI publishes no feed |
| [NIST](https://www.nist.gov/news-events/news) | US standards and guidance, including the AI RMF and its profiles | NIST news RSS feed, filtered to AI-related items |
| [EU AI Office](https://digital-strategy.ec.europa.eu/en/policies/ai-office) | EU AI Act implementation, guidance and codes of practice | New news, library and event links on the AI Office page |
| [APRA](https://www.apra.gov.au/news-and-publications) | Australian prudential regulation, including CPS 230 and CPS 234 | New items in News and publications, filtered to AI, CPS 230/234, operational risk and cyber topics |

## How monitoring works

1. **Weekly poll.** The poller fetches each source and compares it with the last-seen state. The first poll of a new source only records what is already there, and entries older than 30 days are recorded without being reported. No AI model is involved in this step.
2. **Classification.** Claude classifies each new item against the knowledge base: new domain needed, new entry needed, update to a named entry, or no action.
3. **Human review.** If any item needs action, the workflow opens a GitHub issue labelled `human-review-required`. A maintainer decides what to change. Nothing in the knowledge base is edited automatically.
4. **Source health.** If a source fails three runs in a row, the workflow fails and opens an issue so the feed can be fixed or replaced.

A separate **monthly maintenance pass** (1st of the month) re-checks flagged claims in the entries and looks for content gaps. It also opens an issue when it finds something for human review. The claim check relies on the model's existing knowledge and has no web access, so recent developments still need a human to verify them.

## Sources that are not monitored

Sources without machine-readable access are not monitored. This includes sites that block or time out automated requests from the workflow's runners, and sites that load their content with JavaScript. They are not treated as monitoring sources. Entries may still cite them; a maintainer checks those citations by hand when the entry is next reviewed.
