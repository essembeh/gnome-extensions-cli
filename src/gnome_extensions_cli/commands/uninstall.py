"""
gnome-extensions-cli
"""

from argparse import ONE_OR_MORE, ArgumentParser, Namespace

from ..icons import Color, Icons, Label
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
        help="uuid of extensions to uninstall",
    )


def run(args: Namespace, manager: ExtensionManager, _store: GnomeExtensionStore):
    """
    Handler for subcommand
    """
    installed_extensions = {e.uuid: e for e in manager.list_installed_extensions()}
    for uuid in dict.fromkeys(args.uuids):
        installed_extension = installed_extensions.get(uuid)
        if installed_extension is None:
            print(
                Icons.WARNING,
                f"Extension {Color.RED(uuid)} is not installed",
            )
        elif installed_extension.read_only:
            print(
                Icons.HINT,
                "Cannot uninstall",
                installed_extension.metadata.name,
                Label.uuid(installed_extension.uuid),
                ": it is a system extension",
            )
        else:
            print(
                Icons.TRASH,
                "Uninstall",
                installed_extension.metadata.name,
                Label.uuid(installed_extension.uuid),
            )
            manager.uninstall_extension(installed_extension)
