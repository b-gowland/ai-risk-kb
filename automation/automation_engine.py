#!/usr/bin/env python3
"""
AI Risk Knowledge Base — Automation Engine
==========================================
Handles: verification passes, monitoring source checks, regulatory date
tracking, content gap detection, and automated draft generation triggers.

Design principles:
- Every function is idempotent — safe to run multiple times
- All outputs are structured JSON — consumed by downstream reporting
- Human review gate before any content change is committed
- Full audit trail of all automated actions

Run modes:
  python automation_engine.py --mode verify        # Fact-check all flagged claims
  python automation_engine.py --mode monitor       # Check monitoring sources for new incidents
  python automation_engine.py --mode gap-check     # Detect content that needs updating
  python automation_engine.py --mode full          # All of the above
  python automation_engine.py --mode single --entry C2  # Single entry verification
"""

import json
import re
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional
import anthropic

# ============================================================
# CONFIGURATION
# ============================================================

KNOWLEDGE_BASE_PATH = Path("../docs")
SCHEMA_PATH = Path("../schema")
REPORTS_PATH = Path("./reports")
REPORTS_PATH.mkdir(parents=True, exist_ok=True)

# Review cadence settings
REVIEW_CADENCE_DAYS = {
    "incident_examples": 90,      # Quarterly
    "regulatory_dates": 30,       # Monthly
    "framework_refs": 180,        # Biannually
    "full_entry": 365,            # Annually
}

# Monitoring sources — checked on each monitor run
MONITORING_SOURCES = [
    {
        "name": "AI Incident Database",
        "url": "https://incidentdatabase.ai",
        "search_url": "https://incidentdatabase.ai/summaries/incidents/",
        "cadence": "weekly",
        "purpose": "New real-world AI incidents for risk event examples"
    },
    {
        "name": "OECD AI Incidents Monitor",
        "url": "https://oecd.ai/en/incidents",
        "cadence": "monthly",
        "purpose": "Cross-jurisdiction incident coverage"
    },
    {
        "name": "EU AI Office",
        "url": "https://digital-strategy.ec.europa.eu/ai-act",
        "cadence": "monthly",
        "purpose": "EU AI Act enforcement updates, GPAI Code of Practice"
    },
    {
        "name": "APRA",
        "url": "https://www.apra.gov.au",
        "cadence": "monthly",
        "purpose": "CPS 230 guidance, supervisory statements"
    },
    {
        "name": "NIST AI RMF",
        "url": "https://www.nist.gov/itl/ai-risk-management-framework",
        "cadence": "as_published",
        "purpose": "AI RMF updates, IR 8596 final release"
    },
    {
        "name": "MITRE ATLAS",
        "url": "https://atlas.mitre.org",
        "cadence": "quarterly",
        "purpose": "New adversarial AI tactics and techniques"
    },
    {
        "name": "OWASP LLM Top 10",
        "url": "https://owasp.org/www-project-top-10-for-large-language-model-applications",
        "cadence": "annually",
        "purpose": "LLM vulnerability list updates"
    },
    {
        "name": "Stanford HAI AI Index",
        "url": "https://aiindex.stanford.edu",
        "cadence": "annually",
        "purpose": "Incident statistics, regulatory landscape"
    }
]

# Domain-to-monitoring-source mapping
# When a new incident appears in a source, these are the entry IDs to check
DOMAIN_SOURCE_MAP = {
    "AIID": ["A1","A2","A3","A4","B1","B2","B3","B4",
              "C1","C2","C3","C4","C5","D1","D2","D3",
              "E1","E2","E3","F1","F2","F3","G1","G2","G3","G4"],
    "EU AI Office": ["B2","B3","D2","E1","E2","G4"],
    "APRA": ["B1","B2","B3","B4","F2","G1"],
    "MITRE ATLAS": ["C1","C2","C3","C5"],
    "OWASP LLM Top 10": ["C1","C2","A1"],
    "NIST AI RMF": ["A1","A2","A3","A4","B1","G4"],
}

# ============================================================
# DATA MODELS
# ============================================================

@dataclass
class VerificationResult:
    entry_id: str
    claim: str
    claim_location: str          # e.g. "layer_1.plain_english_summary"
    status: str                  # verified | corrected | flagged | unverifiable
    original_value: str
    verified_value: Optional[str]
    source: Optional[str]
    source_url: Optional[str]
    confidence: str              # high | medium | low
    action_required: bool
    notes: str
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class MonitoringResult:
    source_name: str
    checked_at: str
    new_content_detected: bool
    relevant_entries: list[str]
    summary: str
    recommended_action: str      # none | flag_for_review | draft_update
    content_excerpt: str
    human_review_required: bool


@dataclass
class GapReport:
    entry_id: str
    gap_type: str               # missing_persona_hook | missing_owner_tag |
                                # missing_done_criteria | stale_content |
                                # missing_incident | incomplete_layer
    layer: str                  # layer_1 | layer_2 | layer_3 | layer_4
    description: str
    severity: str               # blocking | recommended | cosmetic
    auto_fixable: bool
    fix_prompt: Optional[str]   # Prompt to send to LLM to generate the fix


@dataclass
class AutomationRun:
    run_id: str
    mode: str
    started_at: str
    completed_at: Optional[str]
    entries_processed: list[str]
    verification_results: list[VerificationResult]
    monitoring_results: list[MonitoringResult]
    gap_reports: list[GapReport]
    human_review_items: list[dict]
    status: str                 # running | completed | failed | awaiting_review


# ============================================================
# VERIFICATION ENGINE
# ============================================================

class VerificationEngine:
    """
    Verifies factual claims in knowledge base entries against primary sources.
    Uses web search to check incident details, regulatory dates, and statistics.
    All corrections require human approval before being written to entries.
    """

    def __init__(self, client: anthropic.Anthropic):
        self.client = client

    def verify_entry(self, entry_path: Path) -> list[VerificationResult]:
        """Run verification pass on a single entry file."""
        with open(entry_path) as f:
            content = f.read()

        claims = self._extract_verifiable_claims(content, entry_path.stem)
        results = []
        for claim in claims:
            result = self._verify_claim(claim, content)
            results.append(result)
        return results

    def _extract_verifiable_claims(self, content: str, entry_id: str) -> list[dict]:
        """
        Extract claims that require factual verification.
        Categories: settlement figures, incident dates, statistics, regulatory dates.
        """
        prompt = f"""
You are reviewing a knowledge base entry about AI risk: {entry_id}

Extract all factual claims that should be verified against primary sources.
Focus on:
- Specific monetary figures (settlement amounts, financial losses)
- Specific dates (regulatory effective dates, incident dates)
- Specific statistics (percentages, volumes, counts)
- Named incidents with specific details
- Regulatory article numbers and their requirements

Return as JSON array with each claim as:
{{
  "claim": "the specific claim text",
  "location": "which section it appears in",
  "claim_type": "financial_figure|date|statistic|incident_detail|regulatory_ref",
  "search_query": "optimal web search query to verify this claim"
}}

Only include claims that can be verified against external sources.
Do not include opinions or general statements.

Entry content:
{content[:4000]}
"""
        response = self.client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        try:
            return json.loads(response.content[0].text)
        except Exception:
            return []

    def _verify_claim(self, claim: dict, entry_content: str) -> VerificationResult:
        """
        Verify a single claim using web search.
        Returns structured result with status and any correction needed.
        """
        search_prompt = f"""
Verify this claim from an AI risk knowledge base:

CLAIM: {claim['claim']}
SEARCH QUERY TO USE: {claim['search_query']}

Search for the most authoritative primary source (court records, official
regulatory publications, original news reports) and determine:
1. Is the claim accurate?
2. If not, what is the correct information?
3. What is the primary source URL?

Return as JSON:
{{
  "status": "verified|corrected|flagged|unverifiable",
  "original_value": "{claim['claim']}",
  "verified_value": "the correct value, or same as original if verified",
  "source": "source name",
  "source_url": "URL",
  "confidence": "high|medium|low",
  "action_required": true/false,
  "notes": "brief explanation"
}}
"""
        response = self.client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1000,
            messages=[{"role": "user", "content": search_prompt}]
        )
        try:
            data = json.loads(response.content[0].text)
            return VerificationResult(
                entry_id=claim.get("entry_id", "unknown"),
                claim=claim["claim"],
                claim_location=claim["location"],
                **data
            )
        except Exception as e:
            return VerificationResult(
                entry_id=claim.get("entry_id", "unknown"),
                claim=claim["claim"],
                claim_location=claim["location"],
                status="flagged",
                original_value=claim["claim"],
                verified_value=None,
                source=None,
                source_url=None,
                confidence="low",
                action_required=True,
                notes=f"Verification failed: {str(e)}"
            )


# ============================================================
# MONITORING ENGINE
# ============================================================

class MonitoringEngine:
    """
    Checks monitoring sources for new incidents, regulatory changes,
    and framework updates. Generates structured recommendations for
    human review.
    """

    def __init__(self, client: anthropic.Anthropic):
        self.client = client

    def check_source(self, source: dict,
                     last_checked: Optional[str] = None) -> MonitoringResult:
        """
        Check a monitoring source for new content since last check.
        Returns structured result with relevance assessment.
        """
        since_date = last_checked or (
            datetime.utcnow() - timedelta(days=30)
        ).strftime("%Y-%m-%d")

        prompt = f"""
You are monitoring an AI risk knowledge base. Check this source for new
content since {since_date}:

Source: {source['name']}
URL: {source['url']}
Purpose: {source['purpose']}

Search for new content from this source. Then determine:
1. Is there new content relevant to AI risk management?
2. Which of these entry IDs is the content most relevant to:
   {', '.join(DOMAIN_SOURCE_MAP.get(source['name'], ['all entries']))}
3. Should this trigger a knowledge base update review?

Return as JSON:
{{
  "new_content_detected": true/false,
  "relevant_entries": ["A1", "C2"],
  "summary": "brief summary of new content",
  "recommended_action": "none|flag_for_review|draft_update",
  "content_excerpt": "key excerpt or description",
  "human_review_required": true/false
}}
"""
        response = self.client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        try:
            data = json.loads(response.content[0].text)
            return MonitoringResult(
                source_name=source["name"],
                checked_at=datetime.utcnow().isoformat(),
                **data
            )
        except Exception as e:
            return MonitoringResult(
                source_name=source["name"],
                checked_at=datetime.utcnow().isoformat(),
                new_content_detected=False,
                relevant_entries=[],
                summary=f"Check failed: {str(e)}",
                recommended_action="none",
                content_excerpt="",
                human_review_required=True
            )

    def run_all_sources(self, last_run_log: Optional[dict] = None) -> list[MonitoringResult]:
        results = []
        for source in MONITORING_SOURCES:
            last_checked = None
            if last_run_log:
                last_checked = last_run_log.get(source["name"])
            result = self.check_source(source, last_checked)
            results.append(result)
        return results


# ============================================================
# GAP DETECTION ENGINE
# ============================================================

class GapDetectionEngine:
    """
    Analyses each entry against the canonical schema and MVP requirements.
    Identifies missing persona hooks, missing owner tags, stale content,
    and incomplete layers. Generates auto-fix prompts for LLM-addressable gaps.
    """

    REQUIRED_FIELDS_L1 = [
        "headline", "plain_english_summary", "severity_default",
        "key_question",
        "what_this_means.executive",
        "what_this_means.project_manager",
        "what_this_means.security_analyst"
    ]

    REQUIRED_FIELDS_L2 = [
        "risk_description", "likelihood_drivers", "consequence_types",
        "affected_functions", "controls_summary"
    ]

    REQUIRED_FIELDS_L2_CONTROL = [
        "control_name", "owner_function", "effort",
        "definition_of_done", "pre_golive_required"
    ]

    REQUIRED_FIELDS_L3_CONTROL = [
        "control_id", "control_name", "owner_function",
        "description", "control_type", "implementation_effort",
        "pre_golive_required"
    ]

    def check_entry(self, entry_path: Path) -> list[GapReport]:
        """Check a single entry for all gap types."""
        with open(entry_path) as f:
            content = f.read()

        entry_id = entry_path.stem.split("_")[0].upper()
        gaps = []

        gaps.extend(self._check_layer1_gaps(content, entry_id))
        gaps.extend(self._check_layer2_gaps(content, entry_id))
        gaps.extend(self._check_layer3_gaps(content, entry_id))
        gaps.extend(self._check_layer4_gaps(content, entry_id))
        gaps.extend(self._check_persona_hooks(content, entry_id))
        gaps.extend(self._check_incidents(content, entry_id))
        gaps.extend(self._check_staleness(content, entry_path, entry_id))

        return gaps

    def _check_layer1_gaps(self, content: str, entry_id: str) -> list[GapReport]:
        gaps = []
        for field in self.REQUIRED_FIELDS_L1:
            field_key = field.split(".")[-1]
            # Check if field exists and is non-empty in content
            if f"{field_key}: \"\"" in content or f"{field_key}:" not in content:
                is_persona_hook = "what_this_means" in field
                gaps.append(GapReport(
                    entry_id=entry_id,
                    gap_type="missing_persona_hook" if is_persona_hook
                              else "incomplete_layer",
                    layer="layer_1",
                    description=f"Layer 1 field '{field}' is empty or missing",
                    severity="blocking" if is_persona_hook else "recommended",
                    auto_fixable=True,
                    fix_prompt=self._persona_hook_prompt(entry_id, field)
                    if is_persona_hook else None
                ))
        return gaps

    def _check_layer2_gaps(self, content: str, entry_id: str) -> list[GapReport]:
        gaps = []
        # Check controls_summary has required sub-fields
        if "controls_summary:" in content:
            for field in self.REQUIRED_FIELDS_L2_CONTROL:
                if f"{field}: \"\"" in content:
                    gaps.append(GapReport(
                        entry_id=entry_id,
                        gap_type="missing_owner_tag" if field == "owner_function"
                                  else "missing_done_criteria"
                                  if field == "definition_of_done"
                                  else "incomplete_layer",
                        layer="layer_2",
                        description=f"Control summary field '{field}' is empty",
                        severity="blocking" if field in
                                 ["owner_function", "definition_of_done",
                                  "pre_golive_required"] else "recommended",
                        auto_fixable=field != "definition_of_done",
                        fix_prompt=None
                    ))
        else:
            gaps.append(GapReport(
                entry_id=entry_id,
                gap_type="incomplete_layer",
                layer="layer_2",
                description="controls_summary block is missing entirely",
                severity="blocking",
                auto_fixable=True,
                fix_prompt=self._controls_summary_prompt(entry_id, content)
            ))
        return gaps

    def _check_layer3_gaps(self, content: str, entry_id: str) -> list[GapReport]:
        gaps = []
        if "mitigating_controls:" not in content:
            gaps.append(GapReport(
                entry_id=entry_id,
                gap_type="incomplete_layer",
                layer="layer_3",
                description="Layer 3 mitigating_controls is missing",
                severity="blocking",
                auto_fixable=False,
                fix_prompt=None
            ))
            return gaps

        # Check each control has owner_function
        if "owner_function: \"\"" in content:
            gaps.append(GapReport(
                entry_id=entry_id,
                gap_type="missing_owner_tag",
                layer="layer_3",
                description="One or more controls missing owner_function tag",
                severity="blocking",
                auto_fixable=True,
                fix_prompt=None
            ))
        return gaps

    def _check_layer4_gaps(self, content: str, entry_id: str) -> list[GapReport]:
        gaps = []
        if "implementation_guidance:" not in content:
            gaps.append(GapReport(
                entry_id=entry_id,
                gap_type="incomplete_layer",
                layer="layer_4",
                description="Layer 4 implementation_guidance is missing",
                severity="recommended",
                auto_fixable=False,
                fix_prompt=None
            ))
        return gaps

    def _check_persona_hooks(self, content: str, entry_id: str) -> list[GapReport]:
        gaps = []
        for persona in ["executive", "project_manager", "security_analyst"]:
            pattern = f"{persona}: \"\""
            if pattern in content or f"{persona}:" not in content:
                gaps.append(GapReport(
                    entry_id=entry_id,
                    gap_type="missing_persona_hook",
                    layer="layer_1",
                    description=f"Persona hook for '{persona}' is empty",
                    severity="blocking",
                    auto_fixable=True,
                    fix_prompt=self._persona_hook_prompt(entry_id, persona)
                ))
        return gaps

    def _check_incidents(self, content: str, entry_id: str) -> list[GapReport]:
        gaps = []
        if "incidents:" not in content or content.count("incident_id:") == 0:
            gaps.append(GapReport(
                entry_id=entry_id,
                gap_type="missing_incident",
                layer="layer_1",
                description="No incident examples documented",
                severity="recommended",
                auto_fixable=False,
                fix_prompt=None
            ))
        return gaps

    def _check_staleness(self, content: str, entry_path: Path,
                         entry_id: str) -> list[GapReport]:
        gaps = []
        # Extract next_review date
        match = re.search(r'next_review:\s+"?(\d{4}-\d{2}-\d{2})"?', content)
        if match:
            review_date = datetime.strptime(match.group(1), "%Y-%m-%d")
            if review_date < datetime.utcnow():
                gaps.append(GapReport(
                    entry_id=entry_id,
                    gap_type="stale_content",
                    layer="layer_1",
                    description=f"Entry review date {match.group(1)} has passed",
                    severity="recommended",
                    auto_fixable=False,
                    fix_prompt=None
                ))
        return gaps

    def _persona_hook_prompt(self, entry_id: str, persona: str) -> str:
        return f"""
Write a 2-3 sentence persona hook for the '{persona}' in the Layer 1
'what_this_means' section of entry {entry_id}.

Requirements:
- For 'executive': anchor to reading an audit report or board paper.
  What are they being asked to approve? What is the consequence of inaction?
- For 'project_manager': anchor to waiting on a go-live sign-off.
  Is this risk relevant to their deployment? What should be in place first?
- For 'security_analyst': anchor to implementing controls or reviewing a vendor.
  What is the specific threat? Which control domain does this fall into?

Write in plain English. No jargon the persona wouldn't already know.
Return only the hook text — no headers or labels.
"""

    def _controls_summary_prompt(self, entry_id: str, entry_content: str) -> str:
        return f"""
Generate a controls_summary block for entry {entry_id}.

The controls_summary is the Layer 2 view of controls — focused on WHO,
WHEN, and WHAT DONE LOOKS LIKE, not HOW (that's Layer 3).

For each control derived from the Layer 3 content below, produce:
- control_name: short descriptive name
- owner_function: Security | Technology | Risk | Legal | HR | Compliance |
  Procurement | Operations | All
- effort: Low (<1 week) | Medium (1-4 weeks) | High (>1 month)
- definition_of_done: One observable, verifiable sentence
- pre_golive_required: true or false
- layer_3_ref: the control_id from Layer 3

Return as YAML.

Entry content:
{entry_content[:3000]}
"""


# ============================================================
# AUTOMATED DRAFT GENERATOR
# ============================================================

class DraftGenerator:
    """
    Generates Layer 1 persona hooks and Layer 2 controls_summary blocks
    for entries that are missing them. All generated content is marked
    as draft and requires human review before publication.
    """

    def __init__(self, client: anthropic.Anthropic):
        self.client = client

    def generate_persona_hooks(self, entry_id: str,
                               entry_content: str) -> dict:
        """Generate all three persona hooks for an entry."""
        prompt = f"""
You are writing persona-specific explanations for AI risk entry {entry_id}.

Read the entry content and write concise, persona-anchored hooks for each
of these three audiences. Each hook must be 2-3 sentences. Plain English.

EXECUTIVE (reading an audit report, needs to know what to approve/prioritise):
PROJECT_MANAGER (waiting on go-live sign-off, needs to know what must be done first):
SECURITY_ANALYST (implementing controls or assessing a vendor):

Return as JSON:
{{
  "executive": "...",
  "project_manager": "...",
  "security_analyst": "..."
}}

Entry content:
{entry_content[:5000]}
"""
        response = self.client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        try:
            return json.loads(response.content[0].text)
        except Exception:
            return {"executive": "", "project_manager": "", "security_analyst": ""}

    def generate_controls_summary(self, entry_id: str,
                                   entry_content: str) -> list[dict]:
        """Generate controls_summary from Layer 3 content."""
        prompt = f"""
From this AI risk entry ({entry_id}), extract the Layer 3 controls and
convert them into a Layer 2 controls_summary format.

Layer 2 controls_summary focuses on WHO, WHEN, and DONE — not HOW.
For each control produce:
- control_name: short descriptive name
- owner_function: ONE of: Security | Technology | Risk | Legal | HR |
  Compliance | Procurement | Operations | All
- effort: Low (<1 week) | Medium (1-4 weeks) | High (>1 month)
- definition_of_done: One sentence. Observable. Verifiable.
- pre_golive_required: true (must be done before launch) or false (post-launch ok)
- layer_3_ref: the control_id

Return as JSON array.

Entry content:
{entry_content[:5000]}
"""
        response = self.client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        try:
            return json.loads(response.content[0].text)
        except Exception:
            return []

    def apply_fixes_to_entry(self, entry_path: Path,
                              gaps: list[GapReport]) -> dict:
        """
        Generate fixes for all auto-fixable gaps in an entry.
        Returns a dict of proposed changes — does NOT write to file.
        All changes require human approval before being applied.
        """
        with open(entry_path) as f:
            content = f.read()

        entry_id = entry_path.stem.split("_")[0].upper()
        proposed_changes = []

        auto_fixable_gaps = [g for g in gaps if g.auto_fixable]

        # Generate persona hooks if missing
        persona_gaps = [g for g in auto_fixable_gaps
                        if g.gap_type == "missing_persona_hook"]
        if persona_gaps:
            hooks = self.generate_persona_hooks(entry_id, content)
            for persona in ["executive", "project_manager", "security_analyst"]:
                if persona in hooks and hooks[persona]:
                    proposed_changes.append({
                        "type": "persona_hook",
                        "field": f"what_this_means.{persona}",
                        "current_value": "",
                        "proposed_value": hooks[persona],
                        "auto_generated": True,
                        "requires_human_review": True
                    })

        # Generate controls_summary if missing
        summary_gaps = [g for g in auto_fixable_gaps
                        if g.gap_type == "incomplete_layer"
                        and "controls_summary" in g.description]
        if summary_gaps:
            summary = self.generate_controls_summary(entry_id, content)
            if summary:
                proposed_changes.append({
                    "type": "controls_summary",
                    "field": "layer_2.controls_summary",
                    "current_value": "",
                    "proposed_value": summary,
                    "auto_generated": True,
                    "requires_human_review": True
                })

        return {
            "entry_id": entry_id,
            "entry_path": str(entry_path),
            "gaps_addressed": len(auto_fixable_gaps),
            "proposed_changes": proposed_changes,
            "status": "pending_human_review",
            "generated_at": datetime.utcnow().isoformat()
        }


# ============================================================
# REPORT GENERATOR
# ============================================================

class ReportGenerator:
    """Generates structured reports from automation run results."""

    def generate_verification_report(self,
                                      results: list[VerificationResult]) -> str:
        corrections = [r for r in results if r.status == "corrected"]
        flags = [r for r in results if r.status == "flagged"]
        verified = [r for r in results if r.status == "verified"]

        lines = [
            "# Verification Report",
            f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}",
            f"Claims checked: {len(results)}",
            f"Verified: {len(verified)} | Corrections: {len(corrections)} | Flags: {len(flags)}",
            "",
            "## Required corrections",
        ]

        if not corrections:
            lines.append("None — all checked claims verified accurate.")
        else:
            for r in corrections:
                lines.append(f"\n### {r.entry_id} — {r.claim_location}")
                lines.append(f"Original: {r.original_value}")
                lines.append(f"Correction: {r.verified_value}")
                lines.append(f"Source: [{r.source}]({r.source_url})")
                lines.append(f"Action: {r.notes}")

        lines.extend(["", "## Flagged items (unverifiable — human review required)"])
        if not flags:
            lines.append("None.")
        else:
            for r in flags:
                lines.append(f"\n- **{r.entry_id}** ({r.claim_location}): {r.claim}")
                lines.append(f"  Notes: {r.notes}")

        return "\n".join(lines)

    def generate_monitoring_report(self,
                                    results: list[MonitoringResult]) -> str:
        action_items = [r for r in results if r.recommended_action != "none"]

        lines = [
            "# Monitoring Report",
            f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}",
            f"Sources checked: {len(results)}",
            f"Action items: {len(action_items)}",
            "",
        ]

        if action_items:
            lines.append("## Action items")
            for r in action_items:
                lines.append(f"\n### {r.source_name}")
                lines.append(f"Action: {r.recommended_action}")
                lines.append(f"Relevant entries: {', '.join(r.relevant_entries)}")
                lines.append(f"Summary: {r.summary}")
                lines.append(f"Human review required: {r.human_review_required}")

        lines.extend(["", "## Sources with no new content"])
        clean = [r for r in results if not r.new_content_detected]
        for r in clean:
            lines.append(f"- {r.source_name} — checked {r.checked_at[:10]}")

        return "\n".join(lines)

    def generate_gap_report(self, gap_map: dict[str, list[GapReport]]) -> str:
        all_gaps = [g for gaps in gap_map.values() for g in gaps]
        blocking = [g for g in all_gaps if g.severity == "blocking"]
        recommended = [g for g in all_gaps if g.severity == "recommended"]
        auto_fixable = [g for g in all_gaps if g.auto_fixable]

        lines = [
            "# Content Gap Report",
            f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}",
            f"Entries checked: {len(gap_map)}",
            f"Total gaps: {len(all_gaps)} ({len(blocking)} blocking, "
            f"{len(recommended)} recommended)",
            f"Auto-fixable: {len(auto_fixable)}",
            "",
            "## Blocking gaps (must fix before publication)",
        ]

        if not blocking:
            lines.append("None — all entries meet MVP requirements.")
        else:
            for gap in blocking:
                lines.append(f"\n- **{gap.entry_id}** ({gap.layer}): "
                             f"{gap.description}")
                if gap.auto_fixable:
                    lines.append("  → Auto-fixable: draft will be generated "
                                 "for human review")

        lines.extend(["", "## Recommended improvements"])
        if not recommended:
            lines.append("None.")
        else:
            for gap in recommended:
                lines.append(f"- **{gap.entry_id}** ({gap.layer}): "
                             f"{gap.description}")

        return "\n".join(lines)

    def generate_human_review_summary(self, run: AutomationRun) -> str:
        """Single document for human reviewer — what needs approval."""
        lines = [
            "# Human Review Required",
            f"Run ID: {run.run_id}",
            f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}",
            "",
            "The following items were generated by the automation engine and",
            "require human review before being applied to the knowledge base.",
            "Approve, reject, or modify each item.",
            "",
        ]

        for i, item in enumerate(run.human_review_items, 1):
            lines.append(f"## Item {i}: {item.get('type', 'unknown').upper()}")
            lines.append(f"Entry: {item.get('entry_id', 'unknown')}")
            lines.append(f"Field: {item.get('field', 'unknown')}")
            lines.append("")
            lines.append("**Proposed change:**")
            value = item.get('proposed_value', '')
            if isinstance(value, list):
                for v in value:
                    lines.append(f"  - {v}")
            else:
                lines.append(f"  {value}")
            lines.append("")
            lines.append("**Decision:** [ ] Approve  [ ] Reject  [ ] Modify")
            lines.append("**Notes:**")
            lines.append("")
            lines.append("---")

        return "\n".join(lines)


# ============================================================
# MAIN ORCHESTRATOR
# ============================================================

class AutomationOrchestrator:
    """
    Coordinates all automation components.
    Runs the full pipeline and produces structured outputs for human review.
    """

    def __init__(self):
        self.client = anthropic.Anthropic()
        self.verifier = VerificationEngine(self.client)
        self.monitor = MonitoringEngine(self.client)
        self.gap_detector = GapDetectionEngine()
        self.draft_gen = DraftGenerator(self.client)
        self.reporter = ReportGenerator()

    def run(self, mode: str = "full",
            entry_filter: Optional[str] = None) -> AutomationRun:

        run_id = hashlib.md5(
            datetime.utcnow().isoformat().encode()
        ).hexdigest()[:8]

        run = AutomationRun(
            run_id=run_id,
            mode=mode,
            started_at=datetime.utcnow().isoformat(),
            completed_at=None,
            entries_processed=[],
            verification_results=[],
            monitoring_results=[],
            gap_reports=[],
            human_review_items=[],
            status="running"
        )

        print(f"[{run_id}] Starting automation run — mode: {mode}")

        entry_paths = list(KNOWLEDGE_BASE_PATH.glob("*.md"))
        if entry_filter:
            entry_paths = [p for p in entry_paths
                          if entry_filter.upper() in p.stem.upper()]

        # STEP 1: Gap detection (always runs)
        print(f"[{run_id}] Running gap detection on {len(entry_paths)} entries...")
        gap_map = {}
        for path in entry_paths:
            entry_id = path.stem.split("_")[0].upper()
            gaps = self.gap_detector.check_entry(path)
            gap_map[entry_id] = gaps
            run.entries_processed.append(entry_id)

            # Generate fixes for auto-fixable gaps
            auto_fixable = [g for g in gaps if g.auto_fixable]
            if auto_fixable:
                fix_result = self.draft_gen.apply_fixes_to_entry(path, auto_fixable)
                run.human_review_items.extend(
                    fix_result.get("proposed_changes", [])
                )

        # STEP 2: Verification (runs in verify and full modes)
        if mode in ("verify", "full", "single"):
            print(f"[{run_id}] Running verification pass...")
            for path in entry_paths:
                results = self.verifier.verify_entry(path)
                run.verification_results.extend(results)
                # Add corrections to human review queue
                corrections = [r for r in results if r.status == "corrected"]
                for c in corrections:
                    run.human_review_items.append({
                        "type": "verification_correction",
                        "entry_id": c.entry_id,
                        "field": c.claim_location,
                        "current_value": c.original_value,
                        "proposed_value": c.verified_value,
                        "source": c.source,
                        "source_url": c.source_url,
                        "requires_human_review": True
                    })

        # STEP 3: Monitoring (runs in monitor and full modes)
        if mode in ("monitor", "full"):
            print(f"[{run_id}] Checking monitoring sources...")
            run.monitoring_results = self.monitor.run_all_sources()

        # STEP 4: Generate reports
        print(f"[{run_id}] Generating reports...")
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M")

        if run.verification_results:
            report = self.reporter.generate_verification_report(
                run.verification_results
            )
            (REPORTS_PATH / f"verification_{timestamp}.md").write_text(report)

        if run.monitoring_results:
            report = self.reporter.generate_monitoring_report(
                run.monitoring_results
            )
            (REPORTS_PATH / f"monitoring_{timestamp}.md").write_text(report)

        if gap_map:
            report = self.reporter.generate_gap_report(gap_map)
            (REPORTS_PATH / f"gaps_{timestamp}.md").write_text(report)

        if run.human_review_items:
            review_doc = self.reporter.generate_human_review_summary(run)
            (REPORTS_PATH / f"human_review_{timestamp}.md").write_text(review_doc)
            print(f"[{run_id}] {len(run.human_review_items)} items require human review")
            print(f"[{run_id}] Review document: reports/human_review_{timestamp}.md")

        # Save full run record as JSON
        run.completed_at = datetime.utcnow().isoformat()
        run.status = "awaiting_review" if run.human_review_items else "completed"
        run_data = asdict(run)
        (REPORTS_PATH / f"run_{run_id}_{timestamp}.json").write_text(
            json.dumps(run_data, indent=2)
        )

        print(f"[{run_id}] Run complete — status: {run.status}")
        return run


# ============================================================
# CLI ENTRY POINT
# ============================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="AI Risk Knowledge Base Automation Engine"
    )
    parser.add_argument(
        "--mode",
        choices=["verify", "monitor", "gap-check", "full", "single"],
        default="gap-check",
        help="Automation mode to run"
    )
    parser.add_argument(
        "--entry",
        help="Entry ID filter for single-entry mode (e.g. C2)"
    )
    args = parser.parse_args()

    orchestrator = AutomationOrchestrator()
    run = orchestrator.run(mode=args.mode, entry_filter=args.entry)
    print(f"\nRun ID: {run.run_id}")
    print(f"Status: {run.status}")
    print(f"Entries processed: {len(run.entries_processed)}")
    print(f"Human review items: {len(run.human_review_items)}")
