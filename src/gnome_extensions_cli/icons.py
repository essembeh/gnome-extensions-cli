"""
gnome-extensions-cli
"""

from enum import Enum
from pathlib import Path
from typing import Any, Optional

from colorama import Back, Fore, Style

from .schema import AvailableExtension, InstalledExtension


class Icons(Enum):
    """
    UTF8 Icons
    """

    OK = "✅"
    ERROR = "❌"
    WARNING = "🚨"
    RED_FLAG = "🚩"
    BOOM = "💥"
    QUESTION = "❓"
    DRYRUN = "🙈"
    HINT = "💡"
    DOT_BLACK = "⚫"
    DOT_WHITE = "⚪"
    DOT_RED = "🔴"
    DOT_BLUE = "🔵"
    PACKAGE = "📦"
    THUMB_UP = "👍"
    TRASH = "🗑"

    def __str__(self):
        return self.value


def color(
    *message: str,
    fore: Optional[str] = None,
    back: Optional[str] = None,
    style: Optional[str] = None,
) -> str:
    """
    string formatter with color and style
    """
    pre = ""
    post = ""
    if isinstance(fore, str):
        pre += fore
        post += Fore.RESET
    if isinstance(back, str):
        pre += back
        post += Back.RESET
    if isinstance(style, str):
        pre += style
        post += Style.RESET_ALL
    return pre + " ".join(map(str, filter(None, message))) + post


class Color(Enum):
    """
    Utility tool to use colorama colors
    """

    DEFAULT = None
    BLACK = Fore.BLACK
    RED = Fore.RED
    GREEN = Fore.GREEN
    YELLOW = Fore.YELLOW
    BLUE = Fore.BLUE
    MAGENTA = Fore.MAGENTA
    CYAN = Fore.CYAN
    WHITE = Fore.WHITE
    LIGHTBLACK_EX = Fore.LIGHTBLACK_EX
    LIGHTRED_EX = Fore.LIGHTRED_EX
    LIGHTGREEN_EX = Fore.LIGHTGREEN_EX
    LIGHTYELLOW_EX = Fore.LIGHTYELLOW_EX
    LIGHTBLUE_EX = Fore.LIGHTBLUE_EX
    LIGHTMAGENTA_EX = Fore.LIGHTMAGENTA_EX
    LIGHTCYAN_EX = Fore.LIGHTCYAN_EX
    LIGHTWHITE_EX = Fore.LIGHTWHITE_EX

    def __call__(self, *args, style: Optional[str] = None) -> str:
        style = (
            {"dim": Style.DIM, "bright": Style.BRIGHT}.get(style.lower()) or style
            if style is not None
            else style
        )
        return color(*args, fore=self.value, style=style)


class Label:
    """
    __str__ builder for common types
    """

    @staticmethod
    def uuid(uuid: str) -> str:
        return f"({Color.YELLOW(uuid)})"

    @staticmethod
    def version(version: Optional[Any]) -> Optional[str]:
        return f"v{version}" if version is not None else None

    @staticmethod
    def url(base: str, path: Optional[str]) -> Optional[str]:
        return Color.BLUE(base + path) if path is not None else None

    @staticmethod
    def available(ext: AvailableExtension) -> str:
        return " ".join(
            filter(
                None,
                [
                    Color.DEFAULT(ext.name, style="bright"),
                    Label.uuid(ext.uuid),
                    Label.version(ext.version),
                ],
            )
        )

    @staticmethod
    def installed(ext: InstalledExtension, enabled: Optional[bool] = None) -> str:
        name = ext.metadata.name
        if enabled is True:
            name = Color.DEFAULT(name, style="bright")
        elif enabled is False:
            name = Color.DEFAULT(name, style="dim")
        return (
            f"{name} {Label.uuid(ext.metadata.uuid)} {Label.version(ext.metadata.version) or ''} "
            + (Color.RED("/system") if ext.read_only else Color.GREEN("/user"))
        )

    @staticmethod
    def folder(path: Path) -> str:
        return Color.BLUE(f"{path}/", style="bright")
