---
id: schema
title: Schema Reference
sidebar_position: 3
---

# Schema reference

Every entry in this knowledge base follows a structured schema — version 0.2. This page documents the schema for contributors, automation developers, and anyone building on the knowledge base content.

## Entry structure

Each entry is a Markdown file with YAML frontmatter and structured content sections.

### Frontmatter fields

```yaml
id: string                    # Unique identifier — e.g. c2-prompt-injection
title: string                 # Full entry title
sidebar_label: string         # Short label for navigation
tags: list[string]            # Searchable tags
last_verified: date           # ISO date of last fact-check pass
next_review: date             # ISO date triggering automated review
```

### Layer structure

| Layer | Heading | Audience | Key fields |
|-------|---------|----------|------------|
| 1 | `## Layer 1 — Executive card` | Board, executives | Headline, summary, severity badge, key question, persona tabs |
| 2 | `## Layer 2 — Practitioner overview` | Risk, compliance, PMs | Risk description, likelihood drivers, consequence types, controls summary table |
| 3 | `## Layer 3 — Controls detail` | Risk practitioners, audit | Full control descriptions, jurisdiction notes, KPIs |
| 4 | `## Layer 4 — Technical implementation` | Engineers, security analysts | Code examples, tool references, compliance implementation |

### Persona tabs (Layer 1)

Each entry includes three persona-specific hooks in a tabbed interface:

```mdx
<Tabs>
  <TabItem value="executive" label="Executive / Board">
  [2-3 sentences anchored to reading an audit report or board paper]
  </TabItem>
  <TabItem value="pm" label="Project Manager">
  [2-3 sentences anchored to a go-live sign-off decision]
  </TabItem>
  <TabItem value="analyst" label="Security Analyst">
  [2-3 sentences anchored to implementing controls or reviewing a vendor]
  </TabItem>
</Tabs>
```

### Controls summary table (Layer 2)

Every control in the controls summary must have these five fields:

| Field | Values | Notes |
|-------|--------|-------|
| Control | string | Short descriptive name |
| Owner | function name | Security, Technology, Risk, Legal, HR, Compliance, Procurement, Operations, All |
| Effort | Low / Medium / High | Low = &lt;1 week, Medium = 1–4 weeks, High = >1 month |
| Go-live? | Required / Post-launch badge | `required-golive` or `required-post` CSS class |
| Definition of done | string | One observable, verifiable sentence |

### Severity badges

```html
<span className="severity-badge severity-critical">Critical severity</span>
<span className="severity-badge severity-high">High severity</span>
<span className="severity-badge severity-medium">Medium severity</span>
<span className="severity-badge severity-low">Low severity</span>
```

Severity defaults are starting points — real assessments are context-dependent.

### Framework chips

```html
<span className="framework-chip">NIST AI 600-1</span>
<span className="framework-chip">EU AI Act Art. 15</span>
```

### Scenario seed (end of entry)

Every entry includes a scenario seed for training module use:

```
**Context:** [Organisational setting]
**Trigger event:** [What happens to initiate the scenario]
**Complicating factor:** [What makes resolution non-obvious]
**Discussion questions:** [3-5 questions]
**Difficulty:** Foundational | Intermediate | Advanced
**Jurisdictions:** [Applicable jurisdictions]
```

## Jurisdictional scope

Entries include jurisdiction notes on controls where obligations differ. The controlled vocabulary for jurisdictions is: AU, EU, US, UK, Global.

`Global` means the risk and controls apply without jurisdiction-specific framing.

## Verify flags

Claims that require verification before publication are flagged inline: `[VERIFY: description]`. The automation engine tracks these and clears them after a successful verification pass.

## Version history

| Version | Changes |
|---------|---------|
| v0.1 | Initial schema — four layers, incidents, framework refs, scenario seed |
| v0.2 | Added jurisdictional scope fields, controls_summary with owner/effort/done, persona hooks in Layer 1 |

## Full template

The complete entry template is available in the repository: [`schema/entry_template.md`](https://github.com/b-gowland/ai-risk-kb/blob/main/schema/entry_template.md)
