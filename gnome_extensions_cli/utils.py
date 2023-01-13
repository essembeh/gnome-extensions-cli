"""
gnome-extensions-cli
"""

from typing import Any, Optional

from packaging.version import Version


def version_comparator(left: Any, right: Any) -> int:
    """
    Compare two versions by handling None, integer or strings
    """
    if left == right:
        return 0
    if left is None:
        return 1
    if right is None:
        return -1
    vleft, vright = Version(str(left)), Version(str(right))
    if vleft < vright:
        return 1
    if vleft > vright:
        return -1
    return 0


def confirm(message: str, default: Optional[bool] = None) -> bool:
    """
    Simple interactive confirmation
    """
    while True:
        answer = input(
            f"💬  {message} ["
            + ("Y" if default is True else "y")
            + "/"
            + ("N" if default is False else "n")
            + "] "
        )
        if answer == "" and default is not None:
            return default
        if answer.lower() == "y":
            return True
        if answer.lower() == "n":
            return False
