from argparse import ONE_OR_MORE, ZERO_OR_MORE, ArgumentParser, Namespace
from collections import OrderedDict
from os.path import expanduser
from pathlib import Path

from gnome_extensions_cli import __title__, __version__
from gnome_extensions_cli.model import ExtensionInfo, InstalledExtension
from gnome_extensions_cli.utils import GNOME_URL, enable_extensions, restart_gnome_shell


def list_handler(args: Namespace):
    installed_extensions = OrderedDict(
        (ext_id.uuid, ext_id)
        for ext_id in InstalledExtension.iter_installed(
            args.directory, only_user=not args.all
        )
    )
    print("Installed extensions:")
    for uuid in sorted(installed_extensions.keys()):
        ext = installed_extensions[uuid]
        if ext.version:
            print(
                "[{enabled}] {e.uuid}  (v{e.version})".format(
                    e=ext, enabled="X" if ext.enabled else " "
                )
            )
        else:
            print(
                "[{enabled}] {e.uuid}".format(
                    e=ext, enabled="X" if ext.enabled else " "
                )
            )

        if args.verbose and ext.info:
            if ext.info.version and (
                ext.version is None or ext.info.version > ext.version
            ):
                print("      available version: {e.info.version}".format(e=ext))


def search_handler(args: Namespace):
    installed_extensions = {
        ext_id.uuid: ext_id
        for ext_id in InstalledExtension.iter_installed(args.directory)
    }
    for ext_id in list(dict.fromkeys(args.extensions)):
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
                        version=data["version"], shell_version=data["shell_version"],
                    )
                )
        else:
            print("Cannot find extension {ext_id}".format(ext_id=ext_id))


def install_handler(args: Namespace):
    installed_extensions = {
        ext_id.uuid: ext_id
        for ext_id in InstalledExtension.iter_installed(args.directory, only_user=True)
    }
    need_restart = False
    for ext_id in list(dict.fromkeys(args.extensions)):
        info = ExtensionInfo.find(ext_id)
        if info is None:
            print("Cannot find extension {0}".format(ext_id))
        elif info.uuid in installed_extensions:
            print("Extension {i.name} is already installed".format(i=info))
        else:
            print(
                "Install {i.name} version {i.version} from {i.recommended_url}".format(
                    i=info
                )
            )
            ext = info.install(args.directory)
            if args.enable_extensions:
                need_restart |= ext.enable()
    if need_restart:
        restart_gnome_shell()


def uninstall_handler(args: Namespace):
    installed_extensions = {
        e.uuid: e for e in InstalledExtension.iter_installed(args.directory)
    }
    need_restart = False
    for e in list(dict.fromkeys(args.extensions)):
        ext = installed_extensions.get(e)
        if ext is None:
            print("Extensions {0} is not installed".format(e))
        elif ext.read_only:
            print("Extensions {e.uuid} is a system extension".format(e=ext))
        else:
            print("Uninstall {e.uuid} from {e.folder}".format(e=ext))
            need_restart |= ext.disable()
            ext.rmtree()
    if need_restart:
        restart_gnome_shell()


def update_handler(args: Namespace):
    installed_extensions = {
        e.uuid: e for e in InstalledExtension.iter_installed(args.directory)
    }
    need_restart = False
    for ext in installed_extensions.values():
        if len(args.extensions) and ext.uuid not in args.extensions:
            continue
        if not args.all and not ext.enabled:
            continue
        if ext.info is None:
            print(
                "Cannot find extension {e.uuid} on {url}".format(e=ext, url=GNOME_URL)
            )
        elif ext.info.version and (
            ext.version is None or ext.info.version > ext.version
        ):
            print("Update {e.uuid} from {e.version} to {e.info.version}".format(e=ext))
            need_restart |= ext.enabled
            if not ext.read_only:
                ext.rmtree()
            ext.info.install(args.directory)
        else:
            print("Extension {e.uuid} is up-to-date".format(e=ext))
    if need_restart:
        restart_gnome_shell()


def enable_handler(args: Namespace):
    installed_map = {
        e.uuid: e for e in InstalledExtension.iter_installed(args.directory)
    }
    uuid_list = []
    for e in list(dict.fromkeys(args.extensions)):
        if e in installed_map:
            uuid_list.append(e)
        else:
            print("Cannot enable '{0}', extension is not installed".format(e))
    if enable_extensions(uuid_list, enable=True):
        restart_gnome_shell()


def disable_handler(args: Namespace):
    if enable_extensions(dict.fromkeys(args.extensions), enable=False):
        restart_gnome_shell()


def main():
    parser = ArgumentParser(prog=__title__)
    parser.add_argument(
        "--version", action="version", version="%(prog)s {0}".format(__version__)
    )
    parser.add_argument(
        "-d",
        "--directory",
        type=Path,
        default=Path(expanduser("~/.local/share/gnome-shell/extensions")),
        help="folder where extensions are installed",
    )
    subparsers = parser.add_subparsers(help="sub-command help")
    parser_list = subparsers.add_parser("list", help="list installed extensions")
    parser_list.add_argument(
        "-v", "--verbose", action="store_true", help="display more informations"
    )
    parser_list.add_argument(
        "-a",
        "--all",
        action="store_true",
        help="also list system installed extensions",
    )
    parser_list.set_defaults(handler=list_handler)

    parser_search = subparsers.add_parser(
        "search", help="search available extensions on {0}".format(GNOME_URL),
    )
    parser_search.add_argument(
        "-v", "--verbose", action="store_true", help="display more informations"
    )
    parser_search.set_defaults(handler=search_handler)
    parser_search.add_argument(
        "extensions",
        nargs=ONE_OR_MORE,
        help="uuid or extension number from {0}".format(GNOME_URL),
    )

    parser_install = subparsers.add_parser("install", help="install extension")
    parser_install.set_defaults(handler=install_handler)
    parser_install.add_argument(
        "-d",
        "--disable",
        dest="enable_extensions",
        action="store_false",
        help="install extensions but do not enable them",
    )
    parser_install.add_argument(
        "extensions",
        nargs=ONE_OR_MORE,
        help="uuid or extension number (from {url}) to install".format(url=GNOME_URL),
    )

    parser_uninstall = subparsers.add_parser("uninstall", help="uninstall extension")
    parser_uninstall.set_defaults(handler=uninstall_handler)
    parser_uninstall.add_argument(
        "extensions", nargs=ONE_OR_MORE, help="uuid of extensions to uninstall",
    )

    parser_update = subparsers.add_parser("update", help="update installed extensions")
    parser_update.set_defaults(handler=update_handler)
    parser_update.add_argument(
        "-a",
        "--all",
        action="store_true",
        help="update all extensions, by default only enabled extensions are updated",
    )
    parser_install.add_argument(
        "-n",
        "--dryrun",
        action="store_true",
        help="dryrun mode, do not install new versions, only print details",
    )
    parser_update.add_argument(
        "extensions", nargs=ZERO_OR_MORE, help="only update the given extensions",
    )

    parser_enable = subparsers.add_parser("enable", help="enable extension")
    parser_enable.set_defaults(handler=enable_handler)
    parser_enable.add_argument(
        "extensions", nargs=ONE_OR_MORE, help="uuid of extensions to enable",
    )

    parser_disable = subparsers.add_parser("disable", help="disable extension")
    parser_disable.set_defaults(handler=disable_handler)
    parser_disable.add_argument(
        "extensions", nargs=ONE_OR_MORE, help="uuid of extensions to disable",
    )
    args = parser.parse_args()

    if "handler" in args:
        return args.handler(args)
