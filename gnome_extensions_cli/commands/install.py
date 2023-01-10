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
        help="uuid of extensions to install",
    )


def run(args: Namespace, manager: ExtensionManager, store: GnomeExtensionStore):
    installed_extensions = {e.uuid: e for e in manager.list_installed_extensions()}
    for uuid in dict.fromkeys(args.uuids):
        available_extension = store.find(
            uuid, shell_version=manager.get_current_shell_version()
        )
        if available_extension is None:
            print(Icons.ERROR, f"Cannot find extension ({Color.YELLOW(uuid)})")
        elif available_extension.uuid in installed_extensions:
            print(
                Icons.DRYRUN,
                f"Extension {available_extension.name}",
                f"({Color.YELLOW(available_extension.uuid)})",
                "is already installed",
            )
            manager.enable_uuids([uuid])
        else:
            print(
                Icons.PACKAGE,
                f"Install {available_extension.name}",
                f"({Color.YELLOW(available_extension.uuid)})",
                f"v{available_extension.version}",
            )
            manager.install_extension(available_extension)
