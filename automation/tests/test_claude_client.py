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
