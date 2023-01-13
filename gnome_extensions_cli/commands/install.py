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
        "extensions",
        nargs=ONE_OR_MORE,
        metavar="UUID_OR_PK",
        help="uuid (or pk) of extensions to install",
    )


def run(args: Namespace, manager: ExtensionManager, store: GnomeExtensionStore):
    """
    Handler for subcommand
    """
    installed_extensions = {e.uuid: e for e in manager.list_installed_extensions()}
    shell_version = manager.get_current_shell_version()

    for motif, available_ext in store.iter_fetch(
        dict.fromkeys(args.extensions), shell_version=shell_version
    ):
        if available_ext is None:
            print(Icons.ERROR, "Cannot find extension", Color.RED(motif))
        elif available_ext.uuid in installed_extensions:
            print(
                Icons.DRYRUN,
                "Extension",
                Label.available(available_ext),
                "is already installed",
            )
            manager.enable_uuids([available_ext.uuid])
        else:
            print(Icons.PACKAGE, "Install", Label.available(available_ext))
            manager.install_extension(available_ext)
