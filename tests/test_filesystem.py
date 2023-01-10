from gnome_extensions_cli.filesystem import FilesystemExtensionManager
from gnome_extensions_cli.store import GnomeExtensionStore


def test_filesystem():
    manager = FilesystemExtensionManager(store=GnomeExtensionStore())

    assert manager.get_current_shell_version() is not None

    all_extensions = manager.list_installed_extensions()
    assert len(all_extensions) > 0

    enabled_extensions = manager.list_enabled_uuids()
    assert len(enabled_extensions) > 0

    assert len(all_extensions) > len(enabled_extensions)
