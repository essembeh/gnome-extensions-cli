"""
gnome-extensions-cli
"""

from argparse import ZERO_OR_MORE, ArgumentParser, Namespace

from ..icons import Color, Icons, Label
from ..manager import ExtensionManager
from ..store import GnomeExtensionStore
from ..utils import confirm, version_comparator


def configure(parser: ArgumentParser):
    """
    Configure parser for subcommand
    """
    parser.set_defaults(handler=run)
    parser.add_argument(
        "-i",
        "--install",
        action="store_true",
        help="install extension if not installed",
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-y",
        "--yes",
        action="store_true",
        help="do not prompt confirmation for update/install",
    )
    group.add_argument(
        "-n",
        "--dry-run",
        action="store_true",
        help="do not update nor install anything, "
        + "a return code 17 is returned if updates are available",
    )
    parser.add_argument(
        "--user",
        action="store_true",
        help="only update /user extensions, ignore /system ones",
    )
    parser.add_argument(
        "extensions",
        nargs=ZERO_OR_MORE,
        metavar="UUID_OR_PK",
        help="uuid (or pk) of extensions to update (default: all enabled extensions)",
    )


def run(args: Namespace, manager: ExtensionManager, store: GnomeExtensionStore):
    """
    Handler for subcommand
    """
    installed_extensions = {e.uuid: e for e in manager.list_installed_extensions()}
    enabled_uuids = manager.list_enabled_uuids()
    shell_version = manager.get_current_shell_version()

    # fetch available
    extensions_to_update = []
    extensions_to_install = []
    count = 0
    for uuid, available_ext in store.iter_fetch(
        args.extensions or enabled_uuids, shell_version=shell_version
    ):
        count += 1
        progress = f"[{count}]"
        if available_ext is None:
            # cannot fetch extension
            print(progress, "Cannot find extension", Color.RED(uuid))
        elif available_ext.uuid not in installed_extensions:
            # extension is not installed
            print(
                progress,
                "Found extension",
                Label.available(available_ext),
                ": not installed",
            )
            if args.install:
                extensions_to_install.append(available_ext)
        elif (
            version_comparator(
                installed_extensions[available_ext.uuid].metadata.version,
                available_ext.version,
            )
            > 0
        ):
            # extension can be updated
            print(
                progress,
                "Found extension",
                Label.available(available_ext),
                ": outdated",
            )
            extensions_to_update.append(available_ext)
        else:
            # extension is up to date
            print(
                progress,
                "Found extension",
                Label.available(available_ext),
                ": up-to-date",
            )
    print("")

    if len(extensions_to_update) + len(extensions_to_install) == 0:
        print(Icons.THUMB_UP, "Nothing to update")
    else:
        if len(extensions_to_update) > 0:
            print(Icons.PACKAGE, "Extensions to update:")
            for ext in extensions_to_update:
                print("  ", Color.YELLOW(ext.uuid))

        if len(extensions_to_install) > 0:
            print(Icons.PACKAGE, "Extensions to install:")
            for ext in extensions_to_install:
                print("  ", Color.YELLOW(ext.uuid))

        if args.dry_run:
            # in dryrun mode, exit 17
            raise SystemExit(17)

        if args.yes or confirm("Continue?", default=True):
            for available_extension in extensions_to_update:
                installed_extension = installed_extensions[available_extension.uuid]
                print("Update", Label.available(available_extension))
                if installed_extension.metadata.version is not None:
                    print("  over", Label.version(installed_extension.metadata.version))
                manager.install_extension(available_extension)

            for available_extension in extensions_to_install:
                print("Install", Label.available(available_extension))
                manager.install_extension(available_extension)
