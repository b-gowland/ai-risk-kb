# Contributing to ai-risk-kb

Thanks for your interest. This knowledge base is open source and free to use forever.

## How to contribute

**Corrections:** Open an issue describing the error and include a primary source link. Factual claims must be verifiable — secondary summaries are not sufficient.

**New entries or expansions:** Open an issue first to discuss scope before writing anything. All entries follow the four-layer schema in `docs/schema.md`. The bar is high — each layer has a defined audience and purpose.

**Automation or tooling improvements:** PRs welcome. Include a description of what the change does and why.

## Licence

This project is licensed under the [MIT licence](./LICENSE). Free to use, adapt, and redistribute with attribution.

## Standards

- All factual claims require a primary source (court filings, official reports, regulatory text, published research)
- No vendor marketing or undated claims
- Controls must be actionable and have a named owner role
- Run the gap check before submitting: `uv run python automation_engine.py --mode gap-check`
