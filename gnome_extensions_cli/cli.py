"""
command line interface
"""
from argparse import ArgumentParser

from colorama import Fore
from gi.repository import GLib

from . import __version__
from .commands import (
    disable,
    enable,
    install,
    list_,
    preferences,
    search,
    uninstall,
    update,
)
from .dbus import DbusExtensionManager
from .filesystem import FilesystemExtensionManager
from .icons import Icons
from .store import GnomeExtensionStore


def run():
    """
    entry point
    """
    parser = ArgumentParser(description="Gnome Shell extensions manager")

    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--dbus",
        action="store_const",
        dest="backend",
        const="dbus",
        help="force DBus backend",
    )
    group.add_argument(
        "--filesystem",
        action="store_const",
        dest="backend",
        const="filesystem",
        help="force filesystem backend",
    )

    subparsers = parser.add_subparsers()
    list_.configure(
        subparsers.add_parser("list", aliases=["ls"], help="list installed extensions")
    )
    install.configure(
        subparsers.add_parser("install", aliases=["i"], help="install extensions")
    )
    uninstall.configure(
        subparsers.add_parser("uninstall", aliases=["u"], help="uninstall extensions")
    )
    enable.configure(
        subparsers.add_parser("enable", aliases=[], help="enable extensions")
    )
    disable.configure(
        subparsers.add_parser("disable", aliases=[], help="disable extensions")
    )
    search.configure(
        subparsers.add_parser("search", aliases=[], help="search extensions")
    )
    update.configure(
        subparsers.add_parser("update", aliases=["u"], help="update extensions")
    )
    disable.configure(
        subparsers.add_parser("disable", aliases=[], help="disable extensions")
    )
    preferences.configure(
        subparsers.add_parser(
            "preferences",
            aliases=["edit", "pref"],
            help="edit preferences of extension",
        )
    )

    args = parser.parse_args()

    try:
        # instanciate store
        store = GnomeExtensionStore()

        # instanciate manager
        manager = None
        if args.backend == "dbus":
            manager = DbusExtensionManager()
        elif args.backend == "filesystem":
            manager = FilesystemExtensionManager(store)
        else:
            try:
                manager = DbusExtensionManager()
            except GLib.Error:
                manager = FilesystemExtensionManager(store)
        assert manager is not None

        handler = args.handler if "handler" in args else list_.run
        handler(args, manager, store)
    except KeyboardInterrupt:
        print(f"{Icons.ERROR} Process interrupted")
        exit(1)
    except BaseException as error:  # pylint: disable=broad-except
        print(f"{Icons.BOOM} Error: {Fore.RED}{error}{Fore.RESET}")
        raise error
