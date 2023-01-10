from argparse import ArgumentParser, Namespace

from ..icons import Color, Icons
from ..manager import ExtensionManager
from ..schema import InstalledExtension
from ..store import GnomeExtensionStore


def configure(parser: ArgumentParser):
    parser.set_defaults(handler=run)

    parser.add_argument(
        "-v", "--verbose", action="store_true", help="display more informations"
    )
    parser.add_argument(
        "-a",
        "--all",
        action="store_true",
        help="list all extensions, (by default only enabled are shown)",
    )


def print_ext(ext: InstalledExtension, enabled: bool):
    print(
        Icons.DOT_BLUE if enabled else Icons.DOT_RED,
        Color.DEFAULT(ext.metadata.name, style="bright" if enabled else "dim"),
        f"({Color.YELLOW(ext.uuid)})",
        f"v{ext.metadata.version}" if ext.metadata.version is not None else "",
        Color.RED("/system") if ext.read_only else Color.GREEN("/user"),
    )


def run(args: Namespace, manager: ExtensionManager, _store: GnomeExtensionStore):
    verbose = "verbose" in args and args.verbose
    show_all = "all" in args and args.all

    if verbose:
        print("Gnome Shell", manager.get_current_shell_version())

    extensions = sorted(
        manager.list_installed_extensions(), key=lambda x: x.uuid.lower()
    )
    enabled_uuids = manager.list_enabled_uuids()

    for ext in extensions:
        if ext.uuid in enabled_uuids:
            print_ext(ext, True)

    if show_all:
        for ext in extensions:
            if ext.uuid not in enabled_uuids:
                print_ext(ext, False)
