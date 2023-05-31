"""
gnome-extensions-cli
"""

from argparse import ArgumentParser, Namespace

from ..icons import Color, Icons, Label
from ..manager import ExtensionManager
from ..store import GnomeExtensionStore


def configure(parser: ArgumentParser):
    """
    Configure parser for subcommand
    """
    parser.set_defaults(handler=run)

    parser.add_argument(
        "-v", "--verbose", action="store_true", help="display more information"
    )
    parser.add_argument(
        "-a",
        "--all",
        action="store_true",
        help="list all extensions, (by default only enabled are shown)",
    )


def run(args: Namespace, manager: ExtensionManager, _store: GnomeExtensionStore):
    """
    Handler for subcommand
    """
    verbose = "verbose" in args and args.verbose
    show_all = "all" in args and args.all

    if verbose:
        print("Gnome Shell", Label.version(manager.get_current_shell_version()))
        print()
        print(
            "Installed Extensions:",
            f"(enabled: {Icons.DOT_BLUE}, disabled: {Icons.DOT_WHITE})",
        )

    installed_extensions = sorted(
        manager.list_installed_extensions(), key=lambda x: x.uuid.lower()
    )
    enabled_uuids = manager.list_enabled_uuids()

    for installed_ext in installed_extensions:
        if installed_ext.uuid in enabled_uuids:
            print(Icons.DOT_BLUE, Label.installed(installed_ext, enabled=True))

    if show_all:
        for installed_ext in installed_extensions:
            if installed_ext.uuid not in enabled_uuids:
                print(Icons.DOT_WHITE, Label.installed(installed_ext, enabled=False))

    if verbose:
        print()
        print(
            "Enabled uuids:",
            ", ".join(map(Color.YELLOW, sorted(enabled_uuids, key=str.lower))),
        )
