"""
gnome-extensions-cli
"""

from argparse import ONE_OR_MORE, ArgumentParser, Namespace
from typing import Any

from ..icons import Color, Icons, Label
from ..manager import ExtensionManager
from ..store import GnomeExtensionStore

INDENT = "  "


def configure(parser: ArgumentParser):
    """
    Configure parser for subcommand
    """
    parser.set_defaults(handler=run)
    parser.add_argument("-v", "--verbose", action="store_true", help="display more information")
    parser.add_argument(
        "extensions",
        nargs=ONE_OR_MORE,
        metavar="UUID_OR_PK",
        help="uuid (or pk) of extensions",
    )


def print_form(data: dict[str, Any], indent: str = ""):
    """
    Print a form-like from given data
    """
    maxlen = max(map(len, data.keys()))
    for key, value in data.items():
        if value is not None:
            # right align
            key = key.rjust(maxlen)
            # key style: dim
            key = Color.DEFAULT(key, style="dim")

            if isinstance(value, str) and "\n" in value:
                # multiline string, indent each line
                value = f"\n{indent}{' ' * (maxlen + 2)}".join(value.splitlines())
            elif isinstance(value, (list, set, dict)):
                # if value is a list-like, indent all items
                value = f"\n{indent}{' ' * (maxlen + 2)}".join(map(str, value))

            print(f"{indent}{key}: {value}")


def print_key_value(key: str, value: Any | None, indent: int = 0):
    """
    Print a key-value pair, handling indentation, formatting and colors
    """
    if value is not None:
        if isinstance(value, str) and "\n" in value:
            prefix = INDENT * (indent + 2)
            value = f"\n{prefix}" + value.replace("\n", f"\n{prefix}")
        print(
            INDENT * indent,
            Color.DEFAULT(key, style="dim"),
            ":",
            value if value is not None else "",
        )


def run(args: Namespace, manager: ExtensionManager, store: GnomeExtensionStore):
    """
    Handler for subcommand
    """
    installed_extensions = {e.uuid: e for e in manager.list_installed_extensions()}

    shell_version = manager.get_current_shell_version()

    for motif, available_ext in store.iter_fetch(dict.fromkeys(args.extensions), shell_version=shell_version):
        if available_ext is not None:
            installed_ext = installed_extensions.get(available_ext.uuid)
            print(
                Icons.DOT_BLUE if installed_ext is not None else Icons.DOT_WHITE,
                Color.DEFAULT(available_ext.name, style="bright"),
                Label.uuid(available_ext.uuid),
            )

            print_form(
                {
                    "link": Label.url(store.url, available_ext.link),
                    "screenshot": Label.url(store.url, available_ext.screenshot),
                    "creator": available_ext.creator,
                    "creator_url": Label.url(store.url, available_ext.creator_url),
                    "description": available_ext.description if args.verbose else None,
                    "tag": available_ext.version_tag,
                    "pk": available_ext.pk,
                    "recommended version": Label.version(available_ext.version),
                    "installed version": Label.version(installed_ext.metadata.version)
                    if installed_ext is not None
                    else None,
                    "versions": list(available_ext.shell_version_map.keys()),
                    "available versions": None,
                },
                indent="    ",
            )
        else:
            print(Icons.DOT_RED, f"Cannot find extension {motif}")
