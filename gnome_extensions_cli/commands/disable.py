"""
gnome-extensions-cli
"""

from argparse import ZERO_OR_MORE, ArgumentParser, Namespace

from ..icons import Color
from ..manager import ExtensionManager
from ..store import GnomeExtensionStore


def configure(parser: ArgumentParser):
    """
    Configure parser for subcommand
    """
    parser.set_defaults(handler=run)

    parser.add_argument(
        "--not-installed",
        action="store_true",
        help="disable all extensions which are not installed",
    )
    parser.add_argument(
        "uuids",
        nargs=ZERO_OR_MORE,
        metavar="UUID",
        help="uuid of extensions to disable",
    )


def run(args: Namespace, manager: ExtensionManager, _store: GnomeExtensionStore):
    """
    Handler for subcommand
    """
    uuids = list(set(args.uuids))
    if args.fix:
        installed_uuids = [e.uuid for e in manager.list_installed_extensions()]
        uuids += [
            uuid
            for uuid in manager.list_enabled_uuids()
            if uuid not in installed_uuids and uuid not in args.uuids
        ]
    print("Disable extension(s):")
    for uuid in uuids:
        print(" -", Color.YELLOW(uuid))
    manager.disable_uuids(*uuids)
