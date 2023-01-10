from argparse import ZERO_OR_MORE, ArgumentParser, Namespace
from concurrent.futures import ThreadPoolExecutor, as_completed
from operator import itemgetter

from colorama import Fore

from ..icons import Icons
from ..manager import ExtensionManager
from ..store import GnomeExtensionStore
from ..utils import confirm, version_comparator


def configure(parser: ArgumentParser):
    parser.set_defaults(handler=run)
    parser.add_argument(
        "-i",
        "--install",
        action="store_true",
        help="install extension if not installed",
    )
    parser.add_argument(
        "-y",
        "--yes",
        action="store_true",
        help="do not prompt confirmation for update/install",
    )
    parser.add_argument(
        "uuids",
        nargs=ZERO_OR_MORE,
        metavar="UUID",
        help="uuid or extension number",
    )


def run(args: Namespace, manager: ExtensionManager, store: GnomeExtensionStore):

    installed_extensions = {e.uuid: e for e in manager.list_installed_extensions()}
    enabled_uuids = manager.list_enabled_uuids()
    shell_version = manager.get_current_shell_version()

    uuids = args.uuids or [
        uuid for uuid in installed_extensions if uuid in enabled_uuids
    ]

    # fetch available
    available_extensions = {}
    with ThreadPoolExecutor() as executor:
        jobs = {
            executor.submit(lambda u: store.find(u, shell_version), uuid): uuid
            for uuid in uuids
        }
        for index, job in enumerate(as_completed(jobs.keys()), start=1):
            uuid = jobs[job]
            result = job.result()
            if result is not None:
                available_extensions[uuid] = result
                print(f"[{index}/{len(jobs)}] Fetch {Fore.YELLOW}{uuid}{Fore.RESET}")
            else:
                print(
                    f"[{index}/{len(jobs)}] Could not find {Fore.YELLOW}{uuid}{Fore.RESET}"
                )
    print("")
    # upate all extension with a newer version
    extensions_to_update = list(
        filter(
            lambda ae: version_comparator(
                installed_extensions[ae.uuid].metadata.version, ae.version
            )
            > 0,
            filter(
                lambda ae: ae.uuid in installed_extensions,
                available_extensions.values(),
            ),
        )
    )
    extensions_to_install = (
        list(
            filter(
                lambda ae: ae.uuid not in installed_extensions,
                available_extensions.values(),
            )
        )
        if args.install
        else []
    )

    if len(extensions_to_update) + len(extensions_to_install) == 0:
        print(f"{Icons.OK} {len(uuids)} extension(s) up-to-date")
    else:
        if len(extensions_to_update) > 0:
            print("Extensions to update:")
            print("  ", " ".join(map(itemgetter("uuid"), extensions_to_update)))

        if len(extensions_to_install) > 0:
            print("Extensions to install:")
            print("  ", " ".join(map(itemgetter("uuid"), extensions_to_install)))

        if args.yes or confirm("Continue?", default=True):
            for available_extension in extensions_to_update:
                print(
                    f"Update {available_extension.name}",
                    f"({Fore.YELLOW}{available_extension.uuid}{Fore.RESET})",
                    f"v{available_extension.version}",
                    f"over v{installed_extensions[available_extension.uuid].metadata.version or ''}",
                )
                manager.install_extension(available_extension)

            for available_extension in extensions_to_install:
                print(
                    f"Install {available_extension.name}",
                    f"({Fore.YELLOW}{available_extension.uuid}{Fore.RESET})",
                    f"v{available_extension.version}",
                )
                manager.install_extension(available_extension)
