from pytest import MonkeyPatch, mark

from gnome_extensions_cli.utils import confirm, version_comparator


@mark.parametrize(
    ("left", "right", "expected"),
    [
        (1, 2, 1),
        (2, 10, 1),
        (None, 1, 1),
        ("1.2", "1.2.0", 0),
        (1, "1", 0),
        (1.2, "1.2", 0),
        (None, None, 0),
    ],
)
def test_version_comparator(left: object, right: object, expected: int) -> None:
    assert version_comparator(left, right) == expected
    assert version_comparator(right, left) == -expected


@mark.parametrize(
    ("answers", "default", "expected"),
    [
        (["y"], None, True),
        (["N"], None, False),
        ([""], True, True),
        ([""], False, False),
        (["maybe", "", "n"], None, False),
    ],
)
def test_confirm(monkeypatch: MonkeyPatch, answers: list[str], default: bool | None, expected: bool) -> None:
    remaining = iter(answers)
    monkeypatch.setattr("builtins.input", lambda _prompt: next(remaining))

    assert confirm("Continue?", default=default) is expected
