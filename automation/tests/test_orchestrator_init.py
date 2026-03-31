from automation_engine import AutomationOrchestrator


def test_gap_check_mode_can_run_without_anthropic_api_key(monkeypatch) -> None:
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    orchestrator = AutomationOrchestrator(require_api=False)

    assert orchestrator.client is None
    assert orchestrator.verifier is None
    assert orchestrator.monitor is None
    assert orchestrator.draft_gen is None
