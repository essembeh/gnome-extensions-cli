import sys
from argparse import ONE_OR_MORE, ZERO_OR_MORE, ArgumentParser, Namespace
from collections import OrderedDict

from gnome_extensions_cli import __title__, __version__
from gnome_extensions_cli.manager import (
    DbusExtensionManager,
    ExtensionManager,
    FilesystemExtensionManager,
)
from gnome_extensions_cli.model import GNOME_URL, ExtensionInfo
from gnome_extensions_cli.utils import version_comparator

MANAGERS = OrderedDict(
    (("dbus", DbusExtensionManager), ("file", FilesystemExtensionManager))
)


def uuid_resolve(uuid):
    if isinstance(uuid, str) and uuid.isdigit():
        info = ExtensionInfo.find(int(uuid))
        if info:
            return info.uuid
    return uuid


def edit_handler(args: Namespace, manager: ExtensionManager):
    ext = manager[args.extension]
    if ext is None:
        print("Extensions {0} is not installed".format(args.extension))
        return 1
    else:
        manager.edit_extension(ext)


def list_handler(args: Namespace, manager: ExtensionManager):
    installed_extensions = {e.uuid: e for e in manager.list_installed_extensions()}
    enabled_uuids = manager.get_enabled_uuids()

    if args.verbose:
        print("Gnome Shell", manager.current_shell_version)

    print("Installed extensions:")
    for uuid in sorted(
        installed_extensions.keys(),
        key=lambda x: str(x not in enabled_uuids) if args.sort else "" + x.lower(),
    ):
        ext = installed_extensions[uuid]
        print(
            "[{enabled}] {e}".format(
                e=ext, enabled="X" if ext.uuid in enabled_uuids else " "
            ),
            " #{e.info.pk}".format(e=ext) if args.verbose and ext.info else "",
            (" /system" if ext.read_only else " /user") if args.verbose else "",
            sep="",
        )
        if args.verbose and ext.info:
            if version_comparator(ext.version, ext.info.version) > 0:
                print("      version {e.info.version} is available".format(e=ext))


def search_handler(args: Namespace, manager: ExtensionManager):
    installed_extensions = {e.uuid: e for e in manager.list_installed_extensions()}
    for ext_id in dict.fromkeys(args.extensions):
        info = ExtensionInfo.find(ext_id)
        if info:
            print("{i.name}: {i.uuid}".format(i=info))
            print("    url: {i.url}".format(i=info))
            print("    tag: {i.tag}".format(i=info))
            if args.verbose:
                print("    description: {i.description}".format(i=info))
            print("    recommended version: {i.version}".format(i=info))
            ext = installed_extensions.get(info.uuid)
            if ext:
                print("    installed version: {e.version}".format(e=ext))
            print("    available versions:")
            for data in info.iter_versions(sort_desc=True):
                print(
                    "      version {version} for Gnome Shell {shell_version}".format(
                        version=data["version"],
                        shell_version=data["shell_version"],
                    )
                )
        else:
            print("Cannot find extension {ext_id}".format(ext_id=ext_id))


def install_handler(args: Namespace, manager: ExtensionManager):
    installed_extensions = {e.uuid: e for e in manager.list_installed_extensions()}
    for ext_id in dict.fromkeys(args.extensions):
        info = ExtensionInfo.find(ext_id)
        if info is None:
            print("Cannot find extension {0}".format(ext_id))
        elif info.uuid in installed_extensions:
            print("Extension {i.uuid} is already installed".format(i=info))
        else:
            print("Install {i}".format(i=info))
            manager.install_extension(info)


def uninstall_handler(args: Namespace, manager: ExtensionManager):
    installed_extensions = {e.uuid: e for e in manager.list_installed_extensions()}
    for e in dict.fromkeys(args.extensions):
        ext = installed_extensions.get(e)
        if ext is None:
            print("Extensions {0} is not installed".format(e))
        elif ext.read_only:
            print("Cannot uninstall {e} which is a system extension".format(e=ext))
        else:
            print("Uninstall {e}".format(e=ext))
            manager.uninstall_extension(ext)


def update_handler(args: Namespace, manager: ExtensionManager):
    installed_extensions = {e.uuid: e for e in manager.list_installed_extensions()}
    enabled_uuids = manager.get_enabled_uuids()
    items = (
        dict.fromkeys(args.extensions)
        if len(args.extensions)
        else map(
            lambda e: e.uuid,
            filter(
                lambda e: args.all or e.uuid in enabled_uuids,
                installed_extensions.values(),
            ),
        )
    )
    update_available = False
    for item in items:
        info = ExtensionInfo.find(item)
        if info is None:
            print("Unknown extension {0}".format(item))
        elif info.uuid not in installed_extensions:
            if args.install:
                print(
                    "[DRYRUN] " if args.dry_run else "",
                    "Installing missing extension {i}".format(i=info),
                    sep="",
                )
                if args.dry_run:
                    update_available = True
                else:
                    manager.install_extension(info)
            else:
                print("Extension {i.uuid} is not installed".format(i=info))
        elif (
            version_comparator(installed_extensions[info.uuid].version, info.version)
            > 0
        ):
            ext = installed_extensions[info.uuid]
            print(
                "[DRYRUN] " if args.dry_run else "",
                "Update {e.uuid} ({i.version}) over ({e.version})".format(
                    e=ext, i=info
                ),
                sep="",
            )
            if args.dry_run:
                update_available = True
            else:
                manager.install_extension(info)
        else:
            print("Extension {i.uuid} is up-to-date".format(i=info))

    return 2 if update_available else 0


def enable_handler(args: Namespace, manager: ExtensionManager):
    installed_extensions = {e.uuid: e for e in manager.list_installed_extensions()}
    uuid_list = []
    for e in dict.fromkeys(args.extensions):
        if e in installed_extensions:
            uuid_list.append(e)
        else:
            print("Cannot enable '{0}', extension is not installed".format(e))
    if len(uuid_list):
        manager.enable_uuid(*uuid_list)


def disable_handler(args: Namespace, manager: ExtensionManager):
    manager.disable_uuid(*dict.fromkeys(args.extensions))


def run():
    parser = ArgumentParser(prog=__title__)
    parser.add_argument(
        "--version", action="version", version="%(prog)s {0}".format(__version__)
    )
    parser.add_argument(
        "--backend",
        choices=MANAGERS.keys(),
        default=next(iter(MANAGERS.keys())),
        type=str.lower,
        help="implementation to use to manage extensions",
    )
    subparsers = parser.add_subparsers(help="sub-command help")

    # ACTION: list
    subparser = subparsers.add_parser("list", help="list installed extensions")
    subparser.add_argument(
        "-v", "--verbose", action="store_true", help="display more informations"
    )
    subparser.add_argument(
        "--sort", action="store_true", help="sort enabled extensions first"
    )
    subparser.set_defaults(handler=list_handler)

    # ACTION: search
    subparser = subparsers.add_parser(
        "search",
        help="search available extensions on {0}".format(GNOME_URL),
    )
    subparser.add_argument(
        "-v", "--verbose", action="store_true", help="display more informations"
    )
    subparser.set_defaults(handler=search_handler)
    subparser.add_argument(
        "extensions",
        nargs=ONE_OR_MORE,
        help="uuid or extension number",
    )

    # ACTION: install
    subparser = subparsers.add_parser("install", help="install extension")
    subparser.set_defaults(handler=install_handler)
    subparser.add_argument(
        "extensions",
        nargs=ONE_OR_MORE,
        help="uuid or extension number",
    )

    # ACTION: uninstall
    subparser = subparsers.add_parser("uninstall", help="uninstall extension")
    subparser.set_defaults(handler=uninstall_handler)
    subparser.add_argument(
        "extensions",
        nargs=ONE_OR_MORE,
        type=uuid_resolve,
        help="uuid or extension number",
    )

    # ACTION: update
    subparser = subparsers.add_parser("update", help="update installed extensions")
    subparser.set_defaults(handler=update_handler)
    subparser.add_argument(
        "-a",
        "--all",
        action="store_true",
        help="update all extensions, by default only enabled extensions are updated",
    )
    subparser.add_argument(
        "-i",
        "--install",
        action="store_true",
        help="install extension if not installed",
    )
    subparser.add_argument(
        "-n",
        "--dry-run",
        action="store_true",
        help="only checks if update are available, return 0 if everything is up-to-date, 2 if some updates can be installed",
    )
    subparser.add_argument(
        "extensions",
        nargs=ZERO_OR_MORE,
        type=uuid_resolve,
        help="uuid or extension number",
    )

    # ACTION: enable
    subparser = subparsers.add_parser("enable", help="enable extension")
    subparser.set_defaults(handler=enable_handler)
    subparser.add_argument(
        "extensions",
        nargs=ONE_OR_MORE,
        type=uuid_resolve,
        help="uuid of extensions to enable",
    )

    # ACTION: disable
    subparser = subparsers.add_parser("disable", help="disable extension")
    subparser.set_defaults(handler=disable_handler)
    subparser.add_argument(
        "extensions",
        nargs=ONE_OR_MORE,
        type=uuid_resolve,
        help="uuid or extension number",
    )

    # ACTION: edit
    subparser = subparsers.add_parser("edit", help="edit extension preferences")
    subparser.set_defaults(handler=edit_handler)
    subparser.add_argument(
        "extension",
        type=uuid_resolve,
        help="uuid or extension number",
    )

    args = parser.parse_args()

    if "handler" in args:
        try:
            return args.handler(args, MANAGERS[args.backend]())
        except KeyboardInterrupt:
            return 130
        except BaseException as e:
            print("ERROR", type(e).__name__, e, file=sys.stderr)
            return 1
