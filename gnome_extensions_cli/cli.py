"""
gnome-extensions-cli
"""

import sys
from argparse import ArgumentParser
from os import getenv

from colorama import init

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

    parser.add_argument(
        "--no-color",
        action="store_true",
        help="disable colors and style in output text "
        + "(you can also set NO_COLOR=1 instead of using this option)",
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

    # handle nocolor in output
    if args.no_color or getenv("NO_COLOR") is not None:
        init(strip=True, convert=False)
    else:
        init()

    try:
        # instantiate store
        store = GnomeExtensionStore()

        # instantiate manager
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
