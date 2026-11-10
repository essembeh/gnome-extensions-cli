from gnome_extensions_cli.filesystem import FilesystemExtensionManager
from gnome_extensions_cli.store import GnomeExtensionStore


def test_list_installed_extensions_skips_corrupt_metadata(tmp_path):
    good = tmp_path / "good@example.com"
    good.mkdir()
    (good / "metadata.json").write_text(
        '{"uuid": "good@example.com", "name": "Good"}'
    )
    bad = tmp_path / "bad@example.com"
    bad.mkdir()
    (bad / "metadata.json").write_text("{not valid json!!!")

    manager = FilesystemExtensionManager(
        store=GnomeExtensionStore(), user_folder=tmp_path, system_folders=[]
    )
    extensions = manager.list_installed_extensions()

    assert [ext.uuid for ext in extensions] == ["good@example.com"]


def test_filesystem():
    manager = FilesystemExtensionManager(store=GnomeExtensionStore())

    assert manager.get_current_shell_version() is not None

    all_extensions = manager.list_installed_extensions()
    assert len(all_extensions) > 0

    enabled_extensions = manager.list_enabled_uuids()
    assert len(enabled_extensions) >= 0

    assert len(all_extensions) >= len(enabled_extensions)
