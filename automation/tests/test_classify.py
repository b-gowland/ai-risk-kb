"""Classifier failures must surface (exit 1) so monitoring state is not advanced."""
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

CLASSIFY = Path(__file__).resolve().parents[1] / 'monitoring' / 'classify.py'
spec = importlib.util.spec_from_file_location('classify', CLASSIFY)
classify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(classify)

ITEMS = [{'id': 'a', 'title': 'A'}, {'id': 'b', 'title': 'B'}]


def fake_client(text, stop_reason='end_turn', exc=None, calls=None):
    def create(**kwargs):
        if calls is not None:
            calls.append(kwargs)
        if exc:
            raise exc
        # Thinking models lead with a thinking block before the text.
        return SimpleNamespace(stop_reason=stop_reason, stop_details=None, content=[
            SimpleNamespace(type='thinking', thinking=''),
            SimpleNamespace(type='text', text=text),
        ])
    return SimpleNamespace(beta=SimpleNamespace(messages=SimpleNamespace(create=create)))


def ok_response(ids=('a', 'b')):
    return json.dumps([{'item_id': i, 'action': 'NO_ACTION', 'kb_matches': []} for i in ids])


def test_parses_fenced_response_with_prose():
    text = 'Here you go:\n```json\n' + ok_response() + '\n```'
    assert len(classify.classify_batch(ITEMS, fake_client(text))) == 2


def test_request_uses_current_sonnet_with_fallbacks():
    calls = []
    classify.classify_batch(ITEMS, fake_client(ok_response(), calls=calls))
    (kwargs,) = calls
    assert kwargs['model'] == 'claude-sonnet-5-5'
    assert kwargs['extra_body'] == {'fallbacks': 'default'}
    assert 'temperature' not in kwargs


@pytest.mark.parametrize('client', [
    fake_client('', exc=RuntimeError('credit balance is too low')),
    fake_client(ok_response()[:-5], stop_reason='max_tokens'),
    fake_client('', stop_reason='refusal'),
    fake_client('not json at all'),
    fake_client(ok_response(ids=('a',))),
])
def test_batch_failures_raise(client):
    with pytest.raises((RuntimeError, ValueError)):
        classify.classify_batch(ITEMS, client)


def test_main_exits_1_when_a_batch_fails(tmp_path, monkeypatch):
    diff = tmp_path / 'diff.json'
    diff.write_text(json.dumps({'run_date': '2099-01-01', 'items': ITEMS}))
    monkeypatch.setattr(classify, 'DIFF_FILE', diff)
    monkeypatch.setattr(classify, 'OUTPUT_DIR', tmp_path)
    monkeypatch.setattr(classify, 'REPORTS_DIR', tmp_path)
    monkeypatch.setenv('ANTHROPIC_API_KEY', 'test')
    monkeypatch.setattr(classify.anthropic, 'Anthropic',
                        lambda **_: fake_client('', exc=RuntimeError('boom')))
    with pytest.raises(SystemExit) as excinfo:
        classify.main()
    assert excinfo.value.code == 1
    saved = json.loads((tmp_path / '2099-01-01.json').read_text())
    assert saved['items'] == ITEMS
    assert saved['items_received'] == 2
    assert saved['items_reviewed'] == 0
    assert saved['failed_batches'] == 1
    assert 'Incomplete classification' in (tmp_path / '2099-01-01.md').read_text()


def test_report_tolerates_malformed_matches():
    report = classify.generate_report('2099-01-01', ITEMS, [
        {'item_title': 'X', 'action': 'UPDATE_ENTRY', 'kb_matches': [{}]},
        {'item_title': 'Y', 'action': 'NEW_ENTRY', 'kb_matches': [{'confidence': 'low'}]},
    ], {})
    assert 'Update existing entry' in report


@pytest.mark.parametrize('rows', [
    [{'item_id': 'a', 'action': 'NO_ACTION', 'kb_matches': []}] * 2,
    json.loads(ok_response()) + [{'item_id': 'invented', 'action': 'NO_ACTION', 'kb_matches': []}],
    [{'item_id': 'a', 'action': 'UNKNOWN', 'kb_matches': []},
     {'item_id': 'b', 'action': 'NO_ACTION', 'kb_matches': []}],
    [{'item_id': 'a', 'action': 'NO_ACTION', 'kb_matches': None},
     {'item_id': 'b', 'action': 'NO_ACTION', 'kb_matches': []}],
])
def test_invalid_classifications_fail_instead_of_disappearing_from_report(rows):
    with pytest.raises(ValueError):
        classify.classify_batch(ITEMS, fake_client(json.dumps(rows)))
