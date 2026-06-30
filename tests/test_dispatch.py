"""Smoke tests for the tidereach umbrella dispatcher (dispatch.py)."""

from __future__ import annotations

import sys
from unittest.mock import MagicMock, patch

import pytest

from tidereach.interlock import dispatch


def test_help_exits_cleanly(capsys: pytest.CaptureFixture[str]) -> None:
    with patch.object(sys, "argv", ["tidereach"]):
        dispatch.main()
    out = capsys.readouterr().out
    assert "tidereach — Tidereach stack CLI" in out
    assert "interlock" in out


def test_unknown_layer_exits_1(capsys: pytest.CaptureFixture[str]) -> None:
    with patch.object(sys, "argv", ["tidereach", "nonexistent"]):
        with pytest.raises(SystemExit) as exc:
            dispatch.main()
    assert exc.value.code == 1
    assert "unknown layer" in capsys.readouterr().err


def test_uninstalled_layer_exits_1(capsys: pytest.CaptureFixture[str]) -> None:
    with patch.object(sys, "argv", ["tidereach", "sieve"]):
        with pytest.raises(SystemExit) as exc:
            dispatch.main()
    assert exc.value.code == 1
    err = capsys.readouterr().err
    assert "pip install tidereach-sieve" in err


def test_interlock_layer_dispatches(capsys: pytest.CaptureFixture[str]) -> None:
    captured_argv: list[str] = []

    mock_cli = MagicMock()
    mock_cli.main.side_effect = lambda: captured_argv.extend(sys.argv)

    with (
        patch.object(sys, "argv", ["tidereach", "interlock", "--help"]),
        patch("importlib.import_module", return_value=mock_cli),
    ):
        dispatch.main()

    mock_cli.main.assert_called_once()
    assert captured_argv[0] == "tidereach-interlock"
    assert captured_argv[1] == "--help"
