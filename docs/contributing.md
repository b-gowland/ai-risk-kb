---
id: contributing
title: Contributing
sidebar_position: 5
---

# Contributing

This is an open-source project and contributions are welcome. There are several ways to help.

## Reporting errors

If you find a factual error — a wrong settlement figure, an incorrect regulatory date, a misattributed incident — please raise a GitHub issue with:

- The entry ID (e.g. C2, E1)
- The specific claim that appears to be wrong
- The correct information with a primary source link

Accuracy is the highest priority. Every verified correction improves the resource for everyone.

## Suggesting new incidents

Real-world incident examples make abstract risks concrete. If you know of a documented AI incident that belongs in an entry, raise an issue with:

- The entry ID it relates to
- A brief description of the incident
- The date (approximate is fine)
- A primary source link (news article, court record, official report)

Incidents must be real and documented. Illustrative examples are already flagged as such in entries.

## Suggesting new entries

The taxonomy currently covers 17 risk categories across 7 domains. If you believe a material AI risk is absent or inadequately covered, raise an issue describing:

- The risk you believe is missing
- Why it is distinct from existing entries
- At least one documented real-world incident demonstrating the risk

New entries require editorial review before being added.

## Improving controls content

If you have practitioner experience implementing AI risk controls and believe the Layer 3 or Layer 4 content for an entry is incomplete, incorrect, or could be more actionable, pull requests are welcome.

Controls content must be:
- Specific enough to implement
- Referenced against a documented source or practice
- Reviewed against the entry template schema

## How to submit changes

1. Fork the repository on GitHub
2. Create a branch for your change (`git checkout -b fix/e1-saferent-figure`)
3. Make your changes following the entry template schema
4. Submit a pull request with a clear description of what changed and why
5. Reference any sources in the PR description

## Entry template

All entries follow the schema defined in [`schema/entry_template.md`](https://github.com/b-gowland/ai-risk-kb/blob/main/schema/entry_template.md). Please follow the template when contributing new or updated content. Consistency across entries is a core quality requirement.

## Standards

- All factual claims must be verifiable against primary sources
- Uncertain claims should be flagged with `[VERIFY]` inline rather than silently included
- Controls must be actionable — specific enough that a practitioner can implement them
- Persona hooks must be written for the specific persona, not as generic risk language
- No AI-generated content should be submitted without human review and verification

## Code of conduct

This project follows the [Contributor Covenant](https://www.contributor-covenant.org/) code of conduct. Be respectful, constructive, and focused on improving the resource for practitioners.

## Questions

Raise a GitHub issue or start a GitHub Discussion for questions about the project, scope, or contribution process.
