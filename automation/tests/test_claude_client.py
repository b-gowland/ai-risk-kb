from types import SimpleNamespace

import pytest

from automation_engine import parse_json_from_response
from claude_client import message_kwargs


def response(text, stop_reason='end_turn'):
    return SimpleNamespace(stop_reason=stop_reason, stop_details=None, content=[
        SimpleNamespace(type='thinking', thinking=''),
        SimpleNamespace(type='text', text=text),
    ])


def test_parse_skips_thinking_blocks():
    assert parse_json_from_response(response('{"ok": true}')) == {'ok': True}


@pytest.mark.parametrize('stop_reason', ['refusal', 'max_tokens'])
def test_parse_rejects_unusable_responses(stop_reason):
    with pytest.raises(RuntimeError):
        parse_json_from_response(response('{"ok": true}', stop_reason))


def test_message_kwargs_have_no_sampling_params():
    kwargs = message_kwargs('claude-opus-5-5', 'hi', effort='high')
    assert kwargs['output_config'] == {'effort': 'high'}
    assert not {'temperature', 'top_p', 'top_k', 'thinking'} & kwargs.keys()


def test_real_sdk_sends_shared_kwargs_on_current_api_version():
    """Offline wire check: catches SDK major-version drift in the shared request shape."""
    import json

    import anthropic
    import httpx2 as httpx

    from claude_client import FALLBACK_BETA, MODEL_SONNET

    seen = []

    def respond(request):
        seen.append(request)
        return httpx.Response(200, json={
            'id': 'msg_test', 'type': 'message', 'role': 'assistant',
            'model': MODEL_SONNET, 'stop_reason': 'end_turn', 'stop_sequence': None,
            'content': [{'type': 'text', 'text': '[]'}],
            'usage': {'input_tokens': 1, 'output_tokens': 1},
        })

    with httpx.Client(transport=httpx.MockTransport(respond)) as http:
        client = anthropic.Anthropic(api_key='offline-test', http_client=http, max_retries=0)
        client.beta.messages.create(
            **message_kwargs(MODEL_SONNET, 'hi', effort='low', system='s')
        )
    request = seen[0]
    body = json.loads(request.content)
    assert body['fallbacks'] == 'default'
    assert body['output_config'] == {'effort': 'low'}
    assert not {'temperature', 'top_p', 'top_k', 'thinking'} & body.keys()
    assert FALLBACK_BETA in request.headers['anthropic-beta']
    assert request.headers['anthropic-version'] == '2026-10-21'
    assert request.headers['authorization'] == 'Bearer offline-test'
