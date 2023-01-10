from argparse import ONE_OR_MORE, ArgumentParser, Namespace

from ..manager import ExtensionManager
from ..store import GnomeExtensionStore


def configure(parser: ArgumentParser):
    parser.set_defaults(handler=run)

    parser.add_argument(
        "uuids",
        nargs=ONE_OR_MORE,
        metavar="UUID",
        help="uuid of extensions to enable",
    )


def run(args: Namespace, manager: ExtensionManager, _store: GnomeExtensionStore):
    manager.enable_uuids(args.uuids)
