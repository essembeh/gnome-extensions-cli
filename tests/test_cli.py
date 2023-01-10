import shlex
from typing import List, Tuple
from unittest import mock

import pytest

from gnome_extensions_cli import __version__ as version
from gnome_extensions_cli import cli


def run(capsys, args: str) -> Tuple[int, List[str], List[str]]:
    with pytest.raises(SystemExit) as error:
        with mock.patch("sys.argv", ["gext"] + shlex.split(args)):
            cli.run()
    captured = capsys.readouterr()
    return (
        error.value.code,
        captured.out.splitlines(),
        captured.err.splitlines(),
    )  # pyright: reportGeneralTypeIssues=false


def assert_no_error(
    rc: int, out: List[str], err: List[str]
) -> Tuple[int, List[str], List[str]]:
    assert rc == 0
    assert len(out) > 0
    assert len(err) == 0
    return rc, out, err


def test_help(capsys):
    assert_no_error(*run(capsys, "--help"))
    assert_no_error(*run(capsys, "list --help"))
    assert_no_error(*run(capsys, "show --help"))
    assert_no_error(*run(capsys, "install --help"))
    assert_no_error(*run(capsys, "update --help"))
    assert_no_error(*run(capsys, "uninstall --help"))
    assert_no_error(*run(capsys, "enable --help"))
    assert_no_error(*run(capsys, "disable --help"))
    assert_no_error(*run(capsys, "preferences --help"))


def test_version(capsys):
    _rc, out, _err = assert_no_error(*run(capsys, "--version"))
    assert len(out) == 1
    assert version in out[0]


def test_error(capsys):
    rc, out, err = run(capsys, "foo bar")
    assert rc > 0
    assert len(out) == 0
    assert len(err) > 0
