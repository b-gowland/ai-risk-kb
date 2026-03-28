# AI Risk Knowledge Base — Automation Configuration & Runbook
# Version: 1.0 | Last updated: March 2026
#
# This file defines:
# 1. Automated maintenance schedule
# 2. Trigger conditions for automated review
# 3. Human review workflow
# 4. Escalation rules
# 5. Content quality gates

---

## AUTOMATION SCHEDULE

# All times UTC. Runs are idempotent — safe to re-run.

schedule:

  weekly:
    - name: full_maintenance_pass
      description: >
        Complete weekly pass — monitoring all sources, gap detection across all
        entries, and verification of all flagged claims. Runs every Sunday at
        02:00 UTC via GitHub Actions. Generates a GitHub Issue for human review
        if any action items are found.
      command: python automation_engine.py --mode full
      github_action: .github/workflows/weekly-full.yml
      output: reports/
      human_review_threshold: any_items_found
      notify: GitHub Issue (automatic)
      estimated_cost_per_run: $1.35–$2.45 USD
      estimated_annual_cost: $70–$130 USD

  manually_triggered:
    - name: single_entry_pass
      description: Run full maintenance on a single entry — useful after editing
      command: python automation_engine.py --mode single --entry {entry_id}
      github_action: .github/workflows/weekly-full.yml (workflow_dispatch with entry input)

  annually:
    - name: schema_review
      description: Review schema version for new fields needed
      type: human_initiated
      checklist:
        - New regulatory requirements not covered by existing fields?
        - New persona types identified by user feedback?
        - New automation use cases requiring new structured fields?
      output: schema/schema_review_{date}.md

---

## TRIGGER-BASED AUTOMATION

# These run outside the schedule when triggered by events

triggers:

  new_major_incident:
    description: >
      Triggered when a significant AI incident is identified (AIID severity
      high, or major media coverage of an AI failure)
    detection: Weekly monitoring run flags new_content_detected == true
              with severity == high
    action:
      - Run single-entry verification on affected entries
      - Generate draft incident example for human review
      - Flag entries whose next_review date should be brought forward
    command: python automation_engine.py --mode single --entry {affected_entry_id}
    human_review_required: true
    sla: 5 business days

  regulatory_change:
    description: >
      Triggered when a material regulatory change is detected —
      new effective date, new enforcement action, new guidance
    detection: Monthly regulatory monitoring flags recommended_action != none
    action:
      - Identify all entries referencing the changed regulation
      - Generate summary of required content updates for human review
      - Flag entries as stale if effective dates have changed
    human_review_required: true
    sla: 10 business days

  framework_update:
    description: >
      Triggered when a primary framework (NIST AI RMF, OWASP LLM Top 10,
      ISO 42001, EU AI Act guidance) publishes a new version
    detection: Quarterly framework monitoring
    action:
      - Check all framework_refs in all entries
      - Flag entries referencing superseded versions
      - Generate list of required updates for human review
    human_review_required: true
    sla: 20 business days

  entry_review_due:
    description: >
      Triggered when an entry's next_review date is within 30 days
    detection: Daily check of next_review fields in all entries
    action:
      - Run single-entry gap detection
      - Run single-entry verification pass
      - Generate review report for human reviewer
      - Update next_review date to next cycle on completion
    command: python automation_engine.py --mode single --entry {entry_id}
    human_review_required: true
    sla: next_review date

---

## HUMAN REVIEW WORKFLOW

# Every automation run that generates proposed changes produces a
# human_review_{date}.md file. The reviewer workflow is:

human_review_process:

  step_1_triage:
    description: Review the human_review_{date}.md file
    actions:
      - Review each proposed change
      - Mark each as: APPROVE | REJECT | MODIFY
      - Add notes where modification is needed
    time_estimate: 30-60 minutes per quarterly run

  step_2_apply:
    description: Apply approved changes to source entry files
    actions:
      - For each APPROVED change: update the relevant .md entry file
      - For each MODIFY change: apply the modified version
      - For each REJECT change: add a note explaining why to the entry's
        verify_flags field so it is not re-raised automatically
    time_estimate: 30-60 minutes per quarterly run

  step_3_validate:
    description: Run gap detection after applying changes
    command: python automation_engine.py --mode gap-check
    expected_result: No blocking gaps in updated entries
    time_estimate: 5 minutes

  step_4_version:
    description: Update version and metadata in changed entries
    actions:
      - Increment version field (patch version for corrections, minor for additions)
      - Update last_verified date
      - Calculate and set next_review date
      - Update status to "review" if material changes made, "published" if minor
    time_estimate: 10 minutes

  step_5_log:
    description: Record the review in the change log
    actions:
      - Add entry to CHANGELOG.md with: date, run_id, entries changed, nature of changes
      - Archive the automation run report to reports/archive/
    time_estimate: 5 minutes

  total_estimated_time_per_cycle:
    weekly: 15 minutes (monitoring review only, usually no changes)
    monthly: 30 minutes
    quarterly: 90-120 minutes
    annually: 3-4 hours

---

## CONTENT QUALITY GATES

# These gates are checked by automation on every entry before status
# can be set to "published". Entries that fail any blocking gate
# cannot be published.

quality_gates:

  blocking:
    - name: persona_hooks_complete
      check: all three what_this_means hooks are non-empty
      auto_fixable: true
      fix_method: DraftGenerator.generate_persona_hooks()

    - name: controls_summary_complete
      check: each control in controls_summary has owner_function,
             effort, definition_of_done, and pre_golive_required
      auto_fixable: true
      fix_method: DraftGenerator.generate_controls_summary()

    - name: layer3_owner_tags_complete
      check: all controls in layer_3 have non-empty owner_function
      auto_fixable: false
      fix_method: manual review required

    - name: no_open_verify_flags
      check: verify_flags is empty or all flags are resolved
      auto_fixable: false
      fix_method: run verification pass and resolve each flag

    - name: incidents_present
      check: at least one incident with verify_flag == false is documented
      auto_fixable: false
      fix_method: manual — requires sourcing a real documented incident

    - name: framework_refs_present
      check: at least two framework_refs are documented
      auto_fixable: false
      fix_method: manual review required

  recommended:
    - name: scenario_seed_complete
      check: all scenario_seed fields are non-empty
      auto_fixable: false

    - name: review_date_current
      check: next_review is in the future
      auto_fixable: true
      fix_method: set next_review to current date + 12 months

    - name: kpis_defined
      check: at least two KPIs defined in layer_3
      auto_fixable: false

---

## ESCALATION RULES

escalation:

  critical_finding:
    description: >
      A verification pass finds that a published claim is materially wrong
      (wrong figure, wrong date, wrong incident description)
    action:
      - Immediately set entry status to "review"
      - Generate correction for human approval
      - If correction is urgent (safety or legal implications): notify
        maintainer with 24-hour SLA
    examples:
      - Settlement figure is significantly wrong
      - Regulatory effective date has passed and entry still says "upcoming"
      - Named incident is found to be misattributed or fictional

  new_enforcement_action:
    description: >
      A monitoring run detects a significant AI enforcement action —
      a major regulatory fine, a landmark court decision — that should
      be added as an incident example
    action:
      - Run verification pass on the enforcement action details
      - Generate draft incident example for human review
      - If the action relates to a risk the taxonomy does not cover,
        flag for potential new entry consideration

  schema_limitation:
    description: >
      Automation run detects that a required type of information cannot
      be captured in the current schema
    action:
      - Document the limitation in schema/schema_issues.md
      - Flag for consideration in next schema version review

---

## CHANGELOG TEMPLATE

# Each entry in CHANGELOG.md should follow this format:

# ## [date] Run {run_id}
# **Entries changed:** C2, A1, B2
# **Change type:** verification_correction | content_addition | regulatory_update
# **Summary:** [brief description of what changed and why]
# **Human reviewer:** [initials or name]
# **Next review due:** [date for next scheduled review of changed entries]

---

## DEPENDENCIES

# The automation engine requires:
runtime:
  - Python 3.11+
  - anthropic SDK (pip install anthropic)
  - Standard library: json, re, hashlib, datetime, pathlib, argparse, dataclasses

# Optional for enhanced monitoring:
optional:
  - requests (for direct URL fetching)
  - PyYAML (for YAML entry parsing)
  - schedule (for running scheduled tasks without external scheduler)

# External services:
services:
  - Anthropic API key (set as ANTHROPIC_API_KEY environment variable)
  - Web search capability (via Claude claude-sonnet-4-6 tool use)

# To run locally:
quickstart: |
  export ANTHROPIC_API_KEY=your_key_here
  cd knowledge_base
  python automation/automation_engine.py --mode gap-check
  # Review output in automation/reports/

# To run on a schedule (using cron):
cron_examples: |
  # Weekly monitoring — Sunday 2am UTC
  0 2 * * 0 cd /path/to/knowledge_base && python automation/automation_engine.py --mode monitor

  # Monthly gap check — 1st of month 3am UTC
  0 3 1 * * cd /path/to/knowledge_base && python automation/automation_engine.py --mode gap-check

  # Quarterly verification — 1st of Jan/Apr/Jul/Oct 4am UTC
  0 4 1 1,4,7,10 * cd /path/to/knowledge_base && python automation/automation_engine.py --mode verify
