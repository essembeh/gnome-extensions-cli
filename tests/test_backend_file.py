from gnome_extensions_cli.manager import FilesystemExtensionManager
from gnome_extensions_cli.model import ExtensionInfo


def test_manager(tmp_path):
    manager = FilesystemExtensionManager(user_folder=tmp_path, auto_enable=False)
    info = ExtensionInfo.find(570)
    manager.install_extension(info)
    ext = manager[info.uuid]
    assert ext is not None
    assert (tmp_path / info.uuid).is_dir()
    assert info.uuid == ext.uuid
    manager.uninstall_extension(ext)
    assert not (tmp_path / info.uuid).is_dir()
