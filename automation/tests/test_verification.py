"""Verification must cover the whole entry and preserve failed/unresolved checks."""

import json
import runpy
import sys
import time
from pathlib import Path
from types import SimpleNamespace

import pytest

import automation_engine as engine


def response(value, stop_reason="end_turn"):
    return SimpleNamespace(stop_reason=stop_reason, content=[
        SimpleNamespace(type="text", text=json.dumps(value)),
    ])


def claim(text="A factual claim"):
    return {"claim": text, "location": "Layer 4", "claim_type": "date",
            "search_query": text}


def assessment(status="verified", **overrides):
    return {"status": status, "original_value": "A factual claim",
            "verified_value": "A factual claim", "source": None, "source_url": None,
            "confidence": "low", "action_required": False, "notes": "Assessment",
            **overrides}


def mock_messages(monkeypatch, *replies):
    pending = iter(replies)
    prompts = []

    def create(client, model, prompt, effort):
        prompts.append(prompt)
        value = next(pending)
        if isinstance(value, Exception):
            raise value
        return value

    monkeypatch.setattr(engine, "_create_message", create)
    return prompts


def test_claim_after_old_cutoff_reaches_extraction_and_verification(tmp_path, monkeypatch):
    late_claim = "The regulation takes effect on 1 January 2030."
    entry = tmp_path / "a2-model-drift.mdx"
    content = "Introductory prose.\n" * 300 + "\n## Layer 4\n" + late_claim
    entry.write_text(content)
    prompts = mock_messages(monkeypatch, response([claim(late_claim)]), response(assessment()))

    results = engine.VerificationEngine(None).verify_entry(entry)

    assert content in prompts[0]
    assert late_claim in prompts[1]
    assert results[0].entry_id == "A2"
    assert results[0].status == "verified"


@pytest.mark.parametrize("reply", [
    RuntimeError("API unavailable"), response([], "max_tokens"), response([], "refusal"),
    response({}), response(["not a claim"]), response([{"claim": "missing location"}]),
    SimpleNamespace(stop_reason="end_turn", content=[SimpleNamespace(type="text", text="oops")]),
])
def test_failed_extraction_is_an_incomplete_check(sample_mdx_path, monkeypatch, reply):
    mock_messages(monkeypatch, reply)
    (result,) = engine.VerificationEngine(None).verify_entry(sample_mdx_path)
    assert result.status == "incomplete"
    assert result.action_required
    assert result.claim_location == "entire entry"


def test_valid_empty_extraction_remains_distinct_from_failure(sample_mdx_path, monkeypatch):
    mock_messages(monkeypatch, response([]))
    assert engine.VerificationEngine(None).verify_entry(sample_mdx_path) == []


@pytest.mark.parametrize("bad_reply", [
    RuntimeError("API unavailable"), response({}, "max_tokens"), response({}, "refusal"),
    response([]), response(assessment(status="unknown")),
    response(assessment(action_required="false")),
    response(assessment(status="corrected", verified_value=None)),
])
def test_one_failed_claim_does_not_drop_the_rest(sample_mdx_path, monkeypatch, bad_reply):
    mock_messages(monkeypatch, response([claim("First"), claim("Second")]),
                  bad_reply, response(assessment()))
    results = engine.VerificationEngine(None).verify_entry(sample_mdx_path)
    assert [r.status for r in results] == ["incomplete", "verified"]


@pytest.mark.parametrize("status", ["flagged", "unverifiable", "corrected"])
def test_unresolved_assessment_cannot_opt_out_of_review(sample_mdx_path, monkeypatch, status):
    mock_messages(monkeypatch, response([claim()]), response(assessment(status)))
    (result,) = engine.VerificationEngine(None).verify_entry(sample_mdx_path)
    assert result.status == status
    assert result.action_required is True


@pytest.mark.parametrize(("reply", "expected_status"), [
    (RuntimeError("extraction unavailable"), "failed"),
    (response([claim()]), "awaiting_review"),
])
def test_orchestrator_persists_review_and_run_status(
    sample_mdx_path, tmp_path, monkeypatch, reply, expected_status,
):
    reports = tmp_path / "reports"
    reports.mkdir()
    monkeypatch.setattr(engine, "KNOWLEDGE_BASE_PATH", sample_mdx_path.parent)
    monkeypatch.setattr(engine, "REPORTS_PATH", reports)
    mock_messages(monkeypatch, reply, response(assessment("unverifiable")))
    orchestrator = engine.AutomationOrchestrator(require_api=False)
    orchestrator.verifier = engine.VerificationEngine(None)

    run = orchestrator.run(mode="verify")

    assert run.status == expected_status
    assert len(run.human_review_items) == 1
    saved = json.loads(next(reports.glob("run_*.json")).read_text())
    assert saved["status"] == expected_status
    review = next(reports.glob("human_review_*.md")).read_text()
    assert "Investigate / retry" in review
    report = next(reports.glob("verification_*.md")).read_text()
    assert "all checked claims verified accurate" not in report
    assert "no live sources retrieved" in report
    if expected_status == "failed":
        assert "Incomplete checks: 1" in report
        assert "extraction unavailable" in review
    else:
        assert "Flags: 1" in report


def test_empty_report_does_not_claim_verified_accuracy():
    report = engine.ReportGenerator().generate_verification_report([])
    assert "Claims assessed: 0" in report
    assert "all checked claims verified accurate" not in report


def test_cli_exits_nonzero_after_writing_failed_run_reports(
    sample_mdx_path, tmp_path, monkeypatch,
):
    workdir = tmp_path / "automation"
    workdir.mkdir()
    monkeypatch.chdir(workdir)
    monkeypatch.setattr(sys, "argv", ["automation_engine.py", "--mode", "verify"])
    monkeypatch.setattr(time, "sleep", lambda _: None)

    def unavailable(**kwargs):
        raise RuntimeError("offline API failure")

    client = SimpleNamespace(beta=SimpleNamespace(messages=SimpleNamespace(create=unavailable)))
    monkeypatch.setattr(engine.anthropic, "Anthropic", lambda: client)
    with pytest.raises(SystemExit) as exc:
        runpy.run_path(str(Path(engine.__file__).resolve()), run_name="__main__")
    assert exc.value.code == 1
    record = json.loads(next((workdir / "reports").glob("run_*.json")).read_text())
    assert record["status"] == "failed"
    assert list((workdir / "reports").glob("human_review_*.md"))
