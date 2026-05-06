diff --git a/README.md b/README.md
index 5454d00..aef2aae 100644
--- a/README.md
+++ b/README.md
@@ -8,7 +8,7 @@ A free, open-source reference for understanding, assessing, and controlling AI r
 
 ## What this is
 
-A practitioner reference covering 17 AI risk categories across 7 domains, with four layers of depth per entry:
+A practitioner reference covering 26 AI risk entries across 7 domains, with four layers of depth per entry:
 
 | Layer | Audience | Content |
 |-------|----------|---------|
@@ -59,14 +59,14 @@ ai-risk-kb/
 │   └── changelog.md
 ├── automation/
 │   ├── automation_engine.py      # Maintenance engine
-│   └── automation_config.md      # Schedule and configuration
+│   ├── automation_config.md      # Schedule and configuration
+│   ├── pyproject.toml            # Python project + tool config
+│   └── tests/                    # Automation regression tests
 ├── schema/
 │   └── entry_template.md         # Entry schema v0.2
 ├── .github/workflows/
-│   ├── deploy.yml                # Deploy to GitHub Pages
-│   ├── weekly-monitor.yml        # Weekly incident monitoring
-│   ├── monthly-gaps.yml          # Monthly gap detection
-│   └── quarterly-verify.yml      # Quarterly fact-check
+│   ├── deploy.yml                # Build + deploy site
+│   └── weekly-full.yml           # Weekly full maintenance run
 └── src/
     ├── pages/index.js            # Homepage
     └── css/custom.css            # Site styling
@@ -76,20 +76,23 @@ ai-risk-kb/
 
 The knowledge base is designed for automated maintenance with a human review gate. GitHub Actions workflows run:
 
-- **Weekly** — full maintenance pass: incident monitoring across all 14 sources, gap detection across all 17 entries, and verification of all flagged claims
+- **Weekly** — full maintenance pass: incident monitoring across 8 configured sources, gap detection across all 26 entries, and verification of flagged claims
 
 All proposed changes are generated as GitHub Issues for human review before being applied.
 
 To run the automation locally:
 
 ```bash
-export ANTHROPIC_API_KEY=your_key_here
 cd automation
-python automation_engine.py --mode gap-check     # Find content gaps
-python automation_engine.py --mode monitor       # Check monitoring sources
-python automation_engine.py --mode verify        # Fact-check claims
-python automation_engine.py --mode full          # All of the above
-python automation_engine.py --mode single --entry C2  # Single entry
+uv sync --dev
+uv run python automation_engine.py --mode gap-check
+
+# API-backed modes require ANTHROPIC_API_KEY
+export ANTHROPIC_API_KEY=your_key_here
+uv run python automation_engine.py --mode monitor
+uv run python automation_engine.py --mode verify
+uv run python automation_engine.py --mode full
+uv run python automation_engine.py --mode single --entry C2
 ```
 
 ## Running locally
