import shlex
from unittest import mock

import pytest

from gnome_extensions_cli import __version__ as version
from gnome_extensions_cli import cli


def run(capsys: pytest.CaptureFixture[str], args: str) -> tuple[int, list[str], list[str]]:
    with pytest.raises(SystemExit) as error, mock.patch("sys.argv", ["gext", *shlex.split(args)]):
        cli.run()
    captured = capsys.readouterr()
    rc = error.value.code
    assert isinstance(rc, int)
    return (
        rc,
        captured.out.splitlines(),
        captured.err.splitlines(),
    )


def assert_no_error(rc: int, out: list[str], err: list[str]) -> tuple[int, list[str], list[str]]:
    assert rc == 0
    assert len(out) > 0
    assert len(err) == 0
    return rc, out, err


def test_help(capsys: pytest.CaptureFixture[str]) -> None:
    assert_no_error(*run(capsys, "--help"))
    assert_no_error(*run(capsys, "disable --help"))
    assert_no_error(*run(capsys, "enable --help"))
    assert_no_error(*run(capsys, "install --help"))
    assert_no_error(*run(capsys, "list --help"))
    assert_no_error(*run(capsys, "preferences --help"))
    assert_no_error(*run(capsys, "search --help"))
    assert_no_error(*run(capsys, "show --help"))
    assert_no_error(*run(capsys, "uninstall --help"))
    assert_no_error(*run(capsys, "update --help"))


def test_version(capsys: pytest.CaptureFixture[str]) -> None:
    _rc, out, _err = assert_no_error(*run(capsys, "--version"))
    assert len(out) == 1
    assert version in out[0]


def test_error(capsys: pytest.CaptureFixture[str]) -> None:
    rc, out, err = run(capsys, "foo bar")
    assert rc > 0
    assert len(out) == 0
    assert len(err) > 0
