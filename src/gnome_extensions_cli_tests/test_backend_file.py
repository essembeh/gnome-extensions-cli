import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from gnome_extensions_cli.manager import FilesystemExtensionManager
from gnome_extensions_cli.model import ExtensionInfo


class FileBackendTests(unittest.TestCase):
    def test_manager(self):
        with TemporaryDirectory() as tmp:
            tmp_folder = Path(tmp)
            manager = FilesystemExtensionManager(
                user_folder=tmp_folder, auto_enable=False
            )
            info = ExtensionInfo.find(570)
            manager.install_extension(info)
            ext = manager[info.uuid]
            self.assertIsNotNone(ext)
            self.assertTrue((tmp_folder / info.uuid).is_dir())
            self.assertEqual(info.uuid, ext.uuid)
            manager.uninstall_extension(ext)
            self.assertFalse((tmp_folder / info.uuid).is_dir())
