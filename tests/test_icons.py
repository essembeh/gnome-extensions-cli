from pathlib import Path

from colorama import Fore, Style

from gnome_extensions_cli.icons import Color, Icons, Label, color

from .conftest import make_extension


def test_icons() -> None:
    assert str(Icons.OK) == "✅"
    assert f"{Icons.BOOM} boom" == "💥 boom"


def test_color() -> None:
    assert color("a", "b", fore=Fore.RED) == f"{Fore.RED}a b{Fore.RESET}"
    assert color("a", None, "b") == "a b"
    assert color("a", style=Style.DIM) == f"{Style.DIM}a{Style.RESET_ALL}"


def test_color_enum() -> None:
    assert Color.RED("x") == f"{Fore.RED}x{Fore.RESET}"
    assert Color.DEFAULT("x", style="bright") == f"{Style.BRIGHT}x{Style.RESET_ALL}"
    assert "boom" in Color.RED(ValueError("boom"))


def test_label(tmp_path: Path) -> None:
    assert Label.version(None) is None
    assert Label.version(3) == "v3"
    assert Label.url("https://x", None) is None
    assert "https://x/p" in str(Label.url("https://x", "/p"))
    assert "a@x" in Label.uuid("a@x")
    assert f"{tmp_path}/" in Label.folder(tmp_path)

    ext = make_extension(tmp_path, "a@x", version=2)
    label = Label.installed(ext, enabled=True)
    assert "a@x" in label
    assert "v2" in label
    assert "/user" in label
