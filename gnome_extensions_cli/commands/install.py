"""
gnome-extensions-cli
"""

from argparse import ONE_OR_MORE, ArgumentParser, Namespace

from tqdm import tqdm

from ..icons import Color, Icons, Label
from ..manager import ExtensionManager
from ..store import GnomeExtensionStore
from ..utils import version_comparator


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
    enabled_uuids = manager.list_enabled_uuids()
    shell_version = manager.get_current_shell_version()

    extensions_to_fetch = dict.fromkeys(args.extensions)
    fetched_extensions = {
        uuid: ext
        for uuid, ext in tqdm(
            store.iter_fetch(extensions_to_fetch, shell_version=shell_version),
            unit=" extension(s) fetched",
            total=len(extensions_to_fetch),
        )
    }

    for motif, available_ext in fetched_extensions.items():
        if available_ext is None:
            print(Icons.ERROR, "Cannot find extension", Color.RED(motif))
        elif available_ext.uuid not in installed_extensions:
            print(Icons.PACKAGE, "Install", Label.available(available_ext))
            manager.install_extension(available_ext)
        elif (
            version_comparator(
                installed_extensions[available_ext.uuid].metadata.version,
                available_ext.version,
            )
            > 0
        ):
            print(Icons.PACKAGE, "Upgrade", Label.available(available_ext))
            manager.install_extension(available_ext)
        elif available_ext.uuid not in enabled_uuids:
            print(Icons.HINT, "Enable", Label.available(available_ext))
            manager.enable_uuids(available_ext.uuid)
        else:
            print(
                Icons.DRYRUN,
                "Extension",
                Label.available(available_ext),
                "is already installed",
            )
            manager.enable_uuids(available_ext.uuid)
