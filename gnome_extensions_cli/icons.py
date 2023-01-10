from enum import Enum


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

    def __str__(self):
        return self.value
