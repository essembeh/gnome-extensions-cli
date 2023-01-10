from enum import Enum
from typing import Optional

from colorama import Back, Fore, Style


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
