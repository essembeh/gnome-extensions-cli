import subprocess
import sys
from distutils.version import LooseVersion
from re import fullmatch


def get_shell_version():
    try:
        for line in (
            subprocess.check_output(["gnome-shell", "--version"]).decode().splitlines()
        ):
            m = fullmatch(r"GNOME Shell (?P<version>[0-9.]+)", line)
            if m:
                return m.group("version")
    except BaseException:
        print("Warning, cannot retrieve current Gnome Shell version", file=sys.stderr)


def version_comparator(a, b):
    if a == b:
        return 0
    if a is None:
        return 1
    if b is None:
        return -1
    a, b = LooseVersion(str(a)), LooseVersion(str(b))
    if a < b:
        return 1
    if a > b:
        return -1
    return 0
