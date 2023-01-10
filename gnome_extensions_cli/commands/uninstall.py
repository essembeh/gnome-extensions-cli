from argparse import ONE_OR_MORE, ArgumentParser, Namespace

from ..icons import Color, Icons
from ..manager import ExtensionManager
from ..store import GnomeExtensionStore


def configure(parser: ArgumentParser):
    parser.set_defaults(handler=run)

    parser.add_argument(
        "uuids",
        nargs=ONE_OR_MORE,
        metavar="UUID",
        help="uuid of extensions to uninstall",
    )


def run(args: Namespace, manager: ExtensionManager, _store: GnomeExtensionStore):
    installed_extensions = {e.uuid: e for e in manager.list_installed_extensions()}
    for uuid in dict.fromkeys(args.uuids):
        installed_extension = installed_extensions.get(uuid)
        if installed_extension is None:
            print(
                Icons.ERROR,
                f"Extension {Color.YELLOW(uuid)} is not installed",
            )
        elif installed_extension.read_only:
            print(
                Icons.ERROR,
                f"Cannot uninstall {Color.YELLOW(uuid)}, it is a system extension",
            )
        else:
            print(
                Icons.TRASH,
                f"Uninstall {installed_extension.metadata.name}",
                f"({Color.YELLOW(installed_extension.uuid)})",
            )
            manager.uninstall_extension(installed_extension)
