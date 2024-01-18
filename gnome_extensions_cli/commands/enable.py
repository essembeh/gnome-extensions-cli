"""
gnome-extensions-cli
"""

from argparse import ONE_OR_MORE, ArgumentParser, Namespace

from ..icons import Color
from ..manager import ExtensionManager
from ..store import GnomeExtensionStore


def configure(parser: ArgumentParser):
    """
    Configure parser for subcommand
    """
    parser.set_defaults(handler=run)

    parser.add_argument(
        "uuids",
        nargs=ONE_OR_MORE,
        metavar="UUID",
        help="uuid of extensions to enable",
    )


def run(args: Namespace, manager: ExtensionManager, _store: GnomeExtensionStore):
    """
    Handler for subcommand
    """
    uuids = list(set(args.uuids))
    print("Enable extension(s):")
    for uuid in uuids:
        print(" -", Color.YELLOW(uuid))
    manager.enable_uuids(*uuids)
