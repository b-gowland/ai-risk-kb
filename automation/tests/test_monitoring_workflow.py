"""Exercise the actual Actions shell block with controlled classifier exits."""
import os
import subprocess
import textwrap
from pathlib import Path

import pytest

WORKFLOW = Path(__file__).resolve().parents[2] / '.github/workflows/source-monitoring.yml'


@pytest.mark.parametrize('classifier_exit, expected_exit, action_items', [
    (0, 0, False), (2, 0, True), (1, 1, False), (7, 7, False),
])
def test_classifier_exit_handling(tmp_path, classifier_exit, expected_exit, action_items):
    workflow = WORKFLOW.read_text()
    step = workflow.split('      - name: Classify new items\n', 1)[1].split('\n      - name:', 1)[0]
    script = textwrap.dedent(step.split('        run: |\n', 1)[1])
    stub_dir = tmp_path / 'bin'
    stub_dir.mkdir()
    stub = stub_dir / 'python'
    stub.write_text(f'#!/bin/sh\nexit {classifier_exit}\n')
    stub.chmod(0o755)
    output = tmp_path / 'output'
    environment = tmp_path / 'environment'
    output.touch()
    environment.touch()
    result = subprocess.run(
        ['bash', '--noprofile', '--norc', '-eo', 'pipefail', '-c', script],
        env={**os.environ, 'PATH': f'{stub_dir}:{os.environ["PATH"]}',
             'GITHUB_OUTPUT': str(output), 'GITHUB_ENV': str(environment)},
        capture_output=True, text=True,
    )
    assert result.returncode == expected_exit, result.stderr
    assert ('action_items_found=true' in output.read_text()) == action_items
    assert ('ACTION_ITEMS_FOUND=true' in environment.read_text()) == action_items
