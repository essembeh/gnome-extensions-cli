import subprocess
import sys
from pathlib import Path
from re import finditer, fullmatch

from gnome_extensions_cli.version import Version

GNOME_URL = "https://extensions.gnome.org"
SHELL_SYSTEM_FOLDERS = (
    Path("/usr/share/gnome-shell/extensions"),
    Path("/usr/local/share/gnome-shell/extensions"),
)


def get_shell_version():
    try:
        for line in (
            subprocess.check_output(["gnome-shell", "--version"]).decode().splitlines()
        ):
            m = fullmatch(r"GNOME Shell (?P<version>[0-9.]+)", line)
            if m:
                return Version(m.group("version"))
    except BaseException:
        print("Warning, cannot retrieve current Gnome Shell version", file=sys.stderr)


GNOME_SHELL_VERSION = get_shell_version()


def restart_gnome_shell():
    print("Restarting Gnome Shell ...")
    p = subprocess.run(
        [
            "dbus-send",
            "--session",
            "--type=method_call",
            "--dest=org.gnome.Shell",
            "/org/gnome/Shell",
            "org.gnome.Shell.Eval",
            'string:"global.reexec_self();"',
        ]
    )
    if p.returncode != 0:
        print("Could not restart Gnome Shell, you have to restart it", file=sys.stderr)


def list_enabled_extensions():
    return tuple(
        map(
            lambda m: m.group("uuid"),
            finditer(
                r"'(?P<uuid>[^']+)'",
                subprocess.check_output(
                    ["gsettings", "get", "org.gnome.shell", "enabled-extensions"]
                ).decode(),
            ),
        )
    )


def enable_extensions(uuid_list: list, enable: bool = True):
    old_uuids = set(list_enabled_extensions())
    new_uuids = (old_uuids | set(uuid_list)) if enable else (old_uuids - set(uuid_list))
    if old_uuids != new_uuids:
        if enable:
            print("Enable", ", ".join(new_uuids - old_uuids))
        else:
            print("Disable", ", ".join(old_uuids - new_uuids))
        subprocess.check_call(
            [
                "gsettings",
                "set",
                "org.gnome.shell",
                "enabled-extensions",
                "[{0}]".format(
                    ",".join(map(lambda uuid: '"{0}"'.format(uuid), sorted(new_uuids)))
                ),
            ]
        )
        return True
    return False
