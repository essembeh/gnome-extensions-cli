"""
gnome-extensions-cli
"""

from argparse import ArgumentParser, Namespace

from ..manager import ExtensionManager
from ..store import GnomeExtensionStore


def configure(parser: ArgumentParser):
    """
    Configure parser for subcommand
    """
    parser.set_defaults(handler=run)

    parser.add_argument(
        "uuid",
        metavar="UUID",
        help="uuid of extension to edit preferences",
    )


def run(args: Namespace, manager: ExtensionManager, _store: GnomeExtensionStore):
    """
    Handler for subcommand
    """
    ext = next(
        filter(lambda e: e.uuid == args.uuid, manager.list_installed_extensions()), None
    )
    assert ext is not None, f"Extension {args.uuid} is not installed"
    manager.edit_extension(ext)
