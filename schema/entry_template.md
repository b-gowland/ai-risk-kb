# ENTRY TEMPLATE — AI Risk Knowledge Base
# Version: 1.0 | Schema: v0.2
# This template defines the mandatory structure for every risk entry.
# Automation systems read and write against this schema.
# All fields marked [REQUIRED] must be populated before status: published

---
# ============================================================
# METADATA BLOCK — machine-readable, drives automation
# ============================================================
entry_id: ""                    # [REQUIRED] e.g. C2 — immutable
entry_name: ""                  # [REQUIRED] e.g. Prompt Injection
domain_code: ""                 # [REQUIRED] A|B|C|D|E|F|G
domain_name: ""                 # [REQUIRED] e.g. Security & Adversarial
version: "1.0"                  # semver-lite — increment on material change
status: draft                   # draft | review | published | deprecated
last_verified: ""               # ISO date — set by verification automation
next_review: ""                 # ISO date — triggers automated review prompt
verify_flags: []                # list of claims requiring source confirmation
jurisdiction_scope:
  primary: []                   # AU | EU | US | UK | Global
  notes: ""

# ============================================================
# LAYER 1 — EXECUTIVE CARD
# Target: Board members, senior executives, audit committee
# Tone: Plain English. No jargon. Consequence-first.
# Length: headline + 80 word summary + 3 persona hooks (40 words each)
# Automation note: headline and severity_default are indexed for search
# ============================================================

layer_1:
  headline: ""
  # One sentence. Must answer: what is this risk and what can go wrong?
  # Must be understandable with zero AI background.

  plain_english_summary: ""
  # 80-100 words. Structure: what it is → how it happens → why it matters.
  # No technical terms. If you use a term a CFO wouldn't know, cut it.

  severity_default: ""          # Low | Medium | High | Critical
  # Starting point only — real assessments are context-dependent.

  key_question: ""
  # The one question a board member should ask about this risk.
  # Format: "Has our organisation...?" or "Can we demonstrate...?"

  what_this_means:
  # [REQUIRED FOR MVP] Each hook = 2-3 sentences max.
  # Anchor to the persona's actual situation, not generic risk language.

    executive: ""
    # Reading an audit report or board paper. Needs: what am I being asked
    # to approve or prioritise? What is the consequence of inaction?

    project_manager: ""
    # Waiting on a go-live sign-off. Needs: is this risk relevant to my
    # deployment? What should already be in place before I can proceed?

    security_analyst: ""
    # Implementing controls or reviewing a vendor. Needs: what is the
    # specific threat? Which control domain does this fall into?

# ============================================================
# LAYER 2 — PRACTITIONER OVERVIEW
# Target: Risk managers, compliance leads, informed non-specialists
# Tone: Structured, framework-aware, governance-oriented
# Automation note: likelihood_drivers and consequence_types are indexed
# for risk assessment matching
# ============================================================

layer_2:
  risk_description: ""
  # 200-300 words. Full risk description — mechanism, manifestation,
  # why it matters. May use technical terms but must define them inline.

  likelihood_drivers:
  # [REQUIRED] Specific conditions that increase likelihood this risk
  # materialises. Each item must be verifiable in an organisation.
    - ""

  consequence_types:
  # [REQUIRED] Typed consequences — used for risk register mapping
  # Format: Type (specific example)
    - ""

  affected_functions:
  # [REQUIRED] Business functions most exposed. Used for ownership routing.
    - ""

  controls_summary:
  # [REQUIRED FOR MVP] This block is what the PM persona reads.
  # Every control must have: owner, effort, and definition of done.
  # This is distinct from Layer 3 — Layer 3 is HOW, this is WHO/WHEN/DONE.
    - control_name: ""
      owner_function: ""        # Security | Technology | Risk | Legal | HR |
                                # Compliance | Procurement | Operations | All
      effort: ""                # Low (<1 week) | Medium (1-4 weeks) | High (>1 month)
      definition_of_done: ""    # One sentence. Observable, verifiable outcome.
      pre_golive_required: true # true = blocking | false = post-launch remediation ok
      layer_3_ref: ""           # Links to the detailed control in Layer 3

  regulatory_obligations:
    au:
      applicable: false
      key_requirements: []
      mandatory_controls: []
    eu:
      applicable: false
      key_requirements: []
      mandatory_controls: []
    us:
      applicable: false
      key_requirements: []
      mandatory_controls: []
    notes: ""

# ============================================================
# LAYER 3 — CONTROLS DETAIL
# Target: Risk practitioners, controls owners, internal audit
# Tone: Actionable, specific, implementation-oriented
# Automation note: control_type and owner_function are indexed for
# control mapping and gap analysis automation
# ============================================================

layer_3:
  mitigating_controls:
    - control_id: ""            # [REQUIRED] e.g. C2-001
      control_name: ""
      owner_function: ""        # [REQUIRED] Same enum as controls_summary above
      description: ""           # What to do and how — specific enough to act on
      control_type: ""          # preventive | detective | corrective
      implementation_effort: "" # Low | Medium | High
      effectiveness: ""         # Low | Medium | High
      pre_golive_required: true # Consistent with Layer 2 controls_summary
      layer_4_ref: ""           # Links to technical implementation in Layer 4

      jurisdiction_notes:
        au: ""                  # "Required under APRA CPS 230" | "Recommended" | null
        eu: ""
        us: ""

  kpis:
    - metric: ""
      target: ""
      frequency: ""             # Daily | Weekly | Monthly | Quarterly

# ============================================================
# LAYER 4 — TECHNICAL IMPLEMENTATION
# Target: Technical practitioners, architects, security engineers
# Tone: Precise, implementation-specific, tool-aware
# Automation note: tools_and_libraries is indexed for tech stack matching
# ============================================================

layer_4:
  technical_description: ""
  # How this risk manifests at the technical/system level.
  # Assumes ML/security engineering background.

  implementation_guidance:
    - topic: ""
      description: ""
      code_example: ""          # Pseudocode or pattern — null if not applicable
      tools_and_libraries: []

  compliance_implementation:
    au: []
    eu: []
    us: []

# ============================================================
# INCIDENTS
# Automation note: incidents are checked against AIID and OECD AIM
# on each verification run. verify_flag: true blocks publication.
# ============================================================

incidents:
  - incident_id: ""             # AIID-NNN or internal ref
    title: ""
    date: ""                    # Approximate: "2024-04" or "2024"
    description: ""             # Factual, citable, 2-3 sentences max
    harm_types: []              # financial | reputational | physical |
                                # privacy | rights | operational | safety
    source_url: ""
    verify_flag: false          # true = requires verification before publish
    jurisdiction: ""            # AU | EU | US | UK | Global | Other
    regulatory_action: false    # Was there enforcement or legal outcome?

# ============================================================
# FRAMEWORK REFERENCES
# Automation note: framework refs are checked against published framework
# versions on each verification run
# ============================================================

framework_refs:
  - framework: ""               # e.g. "NIST AI 600-1"
    reference: ""               # Specific article/section
    obligation_type: ""         # mandatory | voluntary | guidance
    jurisdiction: ""            # AU | EU | US | Global

# ============================================================
# SCENARIO SEED — future learning module use
# ============================================================

scenario_seed:
  context: ""
  trigger_event: ""
  complicating_factor: ""
  discussion_questions: []
  learning_objective: ""
  difficulty: ""                # Foundational | Intermediate | Advanced
  applicable_jurisdictions: []
