"""No-network tests for bounded retrieval, evidence provenance and review gates."""

import json
from types import SimpleNamespace as NS

import pytest

import automation_engine as engine
import web_verification as web

URL = "https://www.nist.gov/primary-record"
CLAIM = {
    "claim": "A claim published after the model cutoff",
    "location": "Layer 4",
    "entry_id": "A1",
    "search_query": "primary source query",
}


def search_response(url=URL, *, citations=True, stop="end_turn", error=None):
    content = (
        {"type": "web_search_tool_result_error", "error_code": error}
        if error
        else [
            {"type": "web_search_result", "url": url, "title": "Primary record"},
        ]
    )
    citation = {
        "type": "web_search_result_location",
        "url": url,
        "title": "Primary record",
        "cited_text": "The original source states the relevant fact.",
    }
    return NS(
        stop_reason=stop,
        id="retrieval-1",
        model="test-model",
        usage=NS(input_tokens=20, output_tokens=10, server_tool_use=NS(web_search_requests=1)),
        content=[
            NS(type="server_tool_use", name="web_search", input={"query": "primary source query"}),
            NS(type="web_search_tool_result", content=content),
            NS(type="text", text="Retrieved finding.", citations=[citation] if citations else []),
        ],
    )


def assessment(**overrides):
    data = {
        "status": "verified",
        "original_value": CLAIM["claim"],
        "verified_value": CLAIM["claim"],
        "confidence": "high",
        "action_required": False,
        "notes": "The excerpt supports this claim.",
        "evidence_ids": ["S1"],
        "primary_source_reason": "NIST issued the original record.",
        **overrides,
    }
    return NS(stop_reason="end_turn", content=[NS(type="text", text=json.dumps(data))])


class Client:
    def __init__(self, *responses):
        self.responses = iter(responses)
        self.calls = []
        self.options = None
        self.beta = NS(messages=NS(create=self.create))

    def with_options(self, **options):
        self.options = options
        return self

    def create(self, **kwargs):
        self.calls.append(kwargs)
        result = next(self.responses)
        if isinstance(result, Exception):
            raise result
        return result


@pytest.fixture(autouse=True)
def no_wait(monkeypatch):
    monkeypatch.setattr(web.time, "sleep", lambda _: None)


def verifier(client, **config):
    return engine.VerificationEngine(client, web.WebVerificationConfig(**config))


def test_supported_claim_uses_tool_citations_and_retains_human_review():
    client = Client(search_response(), assessment(source_url="https://invented.example"))
    result = verifier(client)._verify_claim(CLAIM, "")
    assert result.status == "verified"
    assert result.action_required
    assert result.source_url == URL
    assert result.evidence[0]["excerpt"] == "The original source states the relevant fact."
    assert result.verification_basis == "web"
    assert result.verification_metadata["queries"] == ["primary source query"]
    assert result.verification_metadata["retrieval_usage"]["web_search_requests"] == 1
    assert client.options == {"max_retries": 0}
    tool = client.calls[0]["tools"][0]
    assert tool["max_uses"] == 2
    assert tool["type"] == "web_search_20260209"
    assert tool["allowed_callers"] == ["direct"]
    assert "nist.gov" in tool["allowed_domains"]
    assert client.calls[0]["max_tokens"] == 4096
    assert "tools" not in client.calls[1]
    assert "extra_body" not in client.calls[0]
    assert "betas" not in client.calls[0]


@pytest.mark.parametrize(
    "response",
    [
        search_response(citations=False),
        search_response(url="https://nist.gov.attacker.example/fake"),
        search_response(url="https://secondary.example/summary"),
    ],
)
def test_missing_or_disallowed_citations_cannot_verify(response):
    client = Client(response)
    result = verifier(client)._verify_claim(CLAIM, "")
    assert result.status == "unverifiable"
    assert result.source_url is None
    assert result.action_required
    assert len(client.calls) == 1


def test_citation_must_also_appear_in_actual_search_results():
    response = search_response()
    response.content[1].content = []
    result = verifier(Client(response))._verify_claim(CLAIM, "")
    assert result.status == "unverifiable"
    assert not result.evidence


@pytest.mark.parametrize(
    "response",
    [
        search_response(error="max_uses_exceeded"),
        search_response(error="unavailable"),
        search_response(stop="pause_turn"),
        search_response(stop="max_tokens"),
        search_response(stop="refusal"),
        RuntimeError("network failure"),
    ],
)
def test_failed_or_paused_search_stays_incomplete_without_retry(response):
    client = Client(response)
    result = verifier(client)._verify_claim(CLAIM, "")
    assert result.status == "incomplete"
    assert result.verification_basis == "web"
    assert len(client.calls) == 1
    assert result.verification_metadata["claim_number"] == 1


def test_budget_is_shared_across_entries_and_never_falls_back_to_model_knowledge(
    sample_mdx_path,
    monkeypatch,
):
    client = Client(search_response(), assessment())
    check = verifier(client, max_claims=1)
    monkeypatch.setattr(check, "_extract_verifiable_claims", lambda *_: [CLAIM])
    assert check.verify_entry(sample_mdx_path)[0].status == "verified"
    skipped = check.verify_entry(sample_mdx_path)[0]
    assert skipped.status == "incomplete"
    assert "budget exhausted" in skipped.notes
    assert len(client.calls) == 2


@pytest.mark.parametrize(
    "change",
    [
        {"evidence_ids": []},
        {"primary_source_reason": ""},
    ],
)
def test_missing_support_downgrades_assessment_to_unverifiable(change):
    result = verifier(Client(search_response(), assessment(**change)))._verify_claim(CLAIM, "")
    assert result.status == "unverifiable"
    assert result.action_required


def test_invented_evidence_id_is_incomplete_but_keeps_retrieved_evidence():
    result = verifier(Client(search_response(), assessment(evidence_ids=["S999"])))._verify_claim(
        CLAIM, ""
    )
    assert result.status == "incomplete"
    assert result.evidence[0]["url"] == URL
    assert result.verification_metadata["retrieval_usage"]["response_id"] == "retrieval-1"


def test_web_evidence_reaches_json_and_human_review(sample_mdx_path, tmp_path, monkeypatch):
    reports = tmp_path / "reports"
    reports.mkdir()
    monkeypatch.setattr(engine, "KNOWLEDGE_BASE_PATH", sample_mdx_path.parent)
    monkeypatch.setattr(engine, "REPORTS_PATH", reports)
    orchestrator = engine.AutomationOrchestrator(require_api=False)
    orchestrator.verifier = verifier(Client(search_response(), assessment()))
    monkeypatch.setattr(orchestrator.verifier, "_extract_verifiable_claims", lambda *_: [CLAIM])
    run = orchestrator.run(mode="verify")
    assert run.status == "awaiting_review"
    saved = json.loads(next(reports.glob("run_*.json")).read_text())
    assert saved["verification_results"][0]["evidence"][0]["url"] == URL
    review = next(reports.glob("human_review_*.md")).read_text()
    assert URL in review
    assert "The original source states the relevant fact." in review
    assert "Supporting IDs: S1" in review
    report = next(reports.glob("verification_*.md")).read_text()
    assert "web citation excerpts" in report
    assert "no live sources retrieved" not in report


@pytest.mark.parametrize(
    "config",
    [
        {"max_claims": 0},
        {"max_claims": 101},
        {"searches_per_claim": 6},
        {"max_tokens": 0},
        {"primary_domains": ()},
        {"primary_domains": ("https://nist.gov",)},
    ],
)
def test_invalid_limits_rejected_before_calls(config):
    with pytest.raises(ValueError):
        web.WebVerificationConfig(**config)


def test_real_sdk_serializes_tool_and_parses_citations_without_network():
    import anthropic
    import httpx2 as httpx

    def to_json(value):
        if isinstance(value, NS):
            return {k: to_json(v) for k, v in vars(value).items()}
        if isinstance(value, list):
            return [to_json(v) for v in value]
        if isinstance(value, dict):
            return {k: to_json(v) for k, v in value.items()}
        return value

    responses = iter([search_response(), assessment()])
    requests = []

    def respond(request):
        requests.append(json.loads(request.content))
        payload = to_json(next(responses))
        payload.update(
            id="msg_test",
            type="message",
            role="assistant",
            model=web.MODEL_OPUS,
            stop_sequence=None,
        )
        payload.setdefault("usage", {"input_tokens": 20, "output_tokens": 10})
        return httpx.Response(200, json=payload)

    with httpx.Client(transport=httpx.MockTransport(respond)) as http:
        client = anthropic.Anthropic(api_key="offline-test", http_client=http)
        result = verifier(client)._verify_claim(CLAIM, "")
    assert result.status == "verified"
    assert result.source_url == URL
    assert requests[0]["tools"][0]["max_uses"] == 2
    assert len(requests) == 2


def test_truncated_evidence_assessment_keeps_search_provenance():
    reply = assessment()
    reply.stop_reason = "max_tokens"
    result = verifier(Client(search_response(), reply))._verify_claim(CLAIM, "")
    assert result.status == "incomplete"
    assert result.evidence[0]["url"] == URL
    assert result.verification_metadata["retrieval_usage"]["web_search_requests"] == 1


@pytest.mark.parametrize(
    "args",
    [
        ["--mode", "gap-check", "--web-verify"],
        ["--mode", "verify", "--web-verify", "--web-max-claims", "0"],
        ["--mode", "verify", "--web-verify", "--primary-domain", "https://nist.gov"],
    ],
)
def test_cli_rejects_invalid_web_settings_before_client_creation(args):
    import subprocess
    import sys

    result = subprocess.run(
        [sys.executable, engine.__file__, *args], capture_output=True, text=True
    )
    assert result.returncode == 2
    assert "error:" in result.stderr
    assert "Starting automation run" not in result.stdout
