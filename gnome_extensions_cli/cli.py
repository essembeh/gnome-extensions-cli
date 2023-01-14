"""
gnome-extensions-cli
"""

import sys
from argparse import ArgumentParser
from os import getenv

from . import __version__
from .commands import (
    disable,
    enable,
    install,
    list_,
    preferences,
    search,
    show,
    uninstall,
    update,
)
from .dbus import DbusExtensionManager, test_dbus_available
from .filesystem import FilesystemExtensionManager
from .icons import Color, Icons
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
        "-D",
        "--dbus",
        action="store_const",
        dest="backend",
        const="dbus",
        help="force DBus backend",
    )
    group.add_argument(
        "-F",
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
    search.configure(
        subparsers.add_parser("search", aliases=[], help="search for extensions")
    )
    show.configure(
        subparsers.add_parser("show", aliases=[], help="show extensions details")
    )

    install.configure(
        subparsers.add_parser("install", aliases=["i"], help="install extensions")
    )
    uninstall.configure(
        subparsers.add_parser("uninstall", aliases=[""], help="uninstall extensions")
    )
    update.configure(
        subparsers.add_parser("update", aliases=["u"], help="update extensions")
    )

    enable.configure(
        subparsers.add_parser("enable", aliases=[], help="enable extensions")
    )
    disable.configure(
        subparsers.add_parser("disable", aliases=[], help="disable extensions")
    )
    preferences.configure(
        subparsers.add_parser(
            "preferences",
            aliases=["p", "config"],
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
        elif test_dbus_available(getenv("DEBUG") == "1"):
            manager = DbusExtensionManager()
        else:
            manager = FilesystemExtensionManager(store)
        handler = args.handler if "handler" in args else list_.run
        handler(args, manager, store)
    except KeyboardInterrupt:
        print(Icons.ERROR, "Process interrupted")
        sys.exit(1)
    except SystemExit:
        raise
    except BaseException as error:  # pylint: disable=broad-except
        print(Icons.BOOM, "Error:", Color.RED(error))
        raise error
