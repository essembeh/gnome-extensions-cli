from argparse import ZERO_OR_MORE, ArgumentParser, Namespace
from concurrent.futures import ThreadPoolExecutor, as_completed

from ..icons import Color, Icons
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
                print(f"[{index}/{len(jobs)}] Fetch {Color.YELLOW(uuid)}")
            else:
                print(f"[{index}/{len(jobs)}] Could not find {Color.YELLOW(uuid)}")
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
        print(f"{Icons.THUMB_UP} {len(uuids)} extension(s) up-to-date")
    else:
        if len(extensions_to_update) > 0:
            print(Icons.PACKAGE, "Extensions to update:")
            for ext in extensions_to_update:
                print("  ", Color.YELLOW(ext.uuid))

        if len(extensions_to_install) > 0:
            print(Icons.PACKAGE, "Extensions to install:")
            for ext in extensions_to_install:
                print("  ", Color.YELLOW(ext.uuid))

        if args.yes or confirm("Continue?", default=True):
            for available_extension in extensions_to_update:
                installed_extension = installed_extensions[available_extension.uuid]
                print(
                    f"Update {available_extension.name}",
                    f"({Color.YELLOW(available_extension.uuid)})",
                    f"v{available_extension.version}",
                    f"over v{installed_extension.metadata.version}"
                    if installed_extension.metadata.version is not None
                    else "",
                )
                manager.install_extension(available_extension)

            for available_extension in extensions_to_install:
                print(
                    f"Install {available_extension.name}",
                    f"({Color.YELLOW(available_extension.uuid)})",
                    f"v{available_extension.version}",
                )
                manager.install_extension(available_extension)
