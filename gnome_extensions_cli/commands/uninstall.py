from argparse import ONE_OR_MORE, ArgumentParser, Namespace

from colorama import Fore

from ..icons import Icons
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
                f"Extension {Fore.YELLOW}{uuid}{Fore.RESET} is not installed",
            )
        elif installed_extension.read_only:
            print(
                Icons.ERROR,
                f"Cannot uninstall {Fore.YELLOW}{uuid}{Fore.RESET}, it is a system extension",
            )
        else:
            print(
                Icons.OK,
                f"Uninstall {installed_extension.metadata.name}",
                f"({Fore.YELLOW}{installed_extension.uuid}{Fore.RESET})",
            )
            manager.uninstall_extension(installed_extension)
