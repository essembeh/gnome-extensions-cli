from argparse import ONE_OR_MORE, ArgumentParser, Namespace
from typing import Any, Dict, List, Optional

from gnome_extensions_cli.schema import AvailableExtension

from ..icons import Color, Icons
from ..manager import ExtensionManager
from ..store import GnomeExtensionStore

INDENT = "  "


def configure(parser: ArgumentParser):
    parser.set_defaults(handler=run)
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="display more informations"
    )
    parser.add_argument(
        "extensions",
        nargs=ONE_OR_MORE,
        help="uuid or extension number",
    )


def print_key_value(key: str, value: Optional[Any], indent: int = 0):
    if value is not None:
        if isinstance(value, str) and "\n" in value:
            prefix = INDENT * (indent + 1)
            value = f"\n{prefix}" + value.replace("\n", f"\n{prefix}")
        print(
            INDENT * indent,
            Color.DEFAULT(key, style="dim"),
            ":",
            value if value is not None else "",
        )


def build_versions_dict(ext: AvailableExtension) -> Dict[int, List[str]]:
    out = {}
    for shell_version, app in ext.shell_version_map.items():
        app_version = app.version
        if app.version not in out:
            out[app_version] = []
        out[app_version].append(shell_version)
    return out


def build_url(base: str, path: Optional[str]) -> Optional[str]:
    return Color.BLUE(base + path) if path is not None else None


def run(args: Namespace, manager: ExtensionManager, store: GnomeExtensionStore):
    installed_extensions = {e.uuid: e for e in manager.list_installed_extensions()}

    shell_version = manager.get_current_shell_version()
    for ext_id in dict.fromkeys(args.extensions):
        available_ext = store.find(ext_id, shell_version=shell_version)
        if available_ext is not None:
            installed_ext = installed_extensions.get(available_ext.uuid)
            print(
                Icons.DOT_BLUE if installed_ext is not None else Icons.DOT_WHITE,
                Color.DEFAULT(available_ext.name, style="bright"),
                f"({Color.YELLOW(available_ext.uuid)})",
            )
            print_key_value("link", build_url(store.url, available_ext.link), 1)
            print_key_value(
                "screenshot", build_url(store.url, available_ext.screenshot), 1
            )
            print_key_value("creator", available_ext.creator, 1)
            print_key_value(
                "creator_url", build_url(store.url, available_ext.creator_url), 1
            )
            if args.verbose:
                print_key_value("description", available_ext.description, 1)
            print_key_value("tag", available_ext.version_tag, 1)
            print_key_value("recommended version", available_ext.version, 1)
            if installed_ext is not None:
                print_key_value("installed version", installed_ext.metadata.version, 1)
            print_key_value("available versions", "", 1)
            app_versions_dict = build_versions_dict(available_ext)
            for app_version in sorted(app_versions_dict, reverse=True):
                shell_versions = app_versions_dict[app_version]
                gnome_version_label = f"v{shell_versions[0]}"
                if len(shell_versions) > 1:
                    gnome_version_label += f" to v{shell_versions[-1]}"
                print(
                    INDENT * 2,
                    f"v{app_version} for Gnome Shell {gnome_version_label}",
                )
            print()
        else:
            print(Icons.DOT_RED, f"Cannot find extension {ext_id}")
