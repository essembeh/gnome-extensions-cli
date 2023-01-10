from argparse import ONE_OR_MORE, ArgumentParser, Namespace

from colorama import Fore, Style

from ..icons import Icons
from ..manager import ExtensionManager
from ..store import GnomeExtensionStore

INDENT = "  "


def configure(parser: ArgumentParser):
    parser.set_defaults(handler=run)
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="display more informations"
    )
    parser.add_argument(
        "extensions",
        nargs=ONE_OR_MORE,
        help="uuid or extension number",
    )


def print_key_value(key: str, value: str, indent: int = 0):
    print(INDENT * indent, f"{Style.DIM}{key}{Style.NORMAL}:", value or "")


def run(args: Namespace, manager: ExtensionManager, store: GnomeExtensionStore):
    installed_extensions = {e.uuid: e for e in manager.list_installed_extensions()}

    shell_version = manager.get_current_shell_version()
    for ext_id in dict.fromkeys(args.extensions):
        info = store.find(ext_id, shell_version=shell_version)
        if info is not None:
            ext = installed_extensions.get(info.uuid)
            print(
                Icons.DOT_BLUE if ext is not None else Icons.DOT_WHITE,
                f"{info.name} ({Fore.YELLOW}{info.uuid}{Fore.RESET})",
            )
            print_key_value("link", f"{store.url}{info.link}", 1)
            print_key_value("screenshot", f"{store.url}{info.screenshot}", 1)
            print_key_value("creator", f"{info.creator}", 1)
            print_key_value("creator_url", f"{store.url}{info.creator_url}", 1)
            if args.verbose:
                print_key_value("description", f"{info.description}", 1)
            print_key_value("tag", f"{info.version_tag}", 1)
            print_key_value("recommended version", f"{info.version}", 1)
            if ext:
                print_key_value("installed version", f"{ext.metadata.version}", 1)
            print_key_value("available versions", "", 1)
            for shell_version in reversed(info.shell_version_map):
                data = info.shell_version_map[shell_version]
                print(
                    INDENT * 2,
                    f"version:{data.version} (tag:{data.pk}) for Gnome Shell v{shell_version}",
                )
        else:
            print(Icons.DOT_RED, f"Cannot find extension {ext_id}")
