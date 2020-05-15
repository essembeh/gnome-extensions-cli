import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from gnome_extensions_cli.model import ExtensionInfo
from gnome_extensions_cli.version import Version


class ExtTests(unittest.TestCase):
    def test_find(self):
        info = ExtensionInfo.find(570)
        self.assertIsNotNone(info)
        self.assertEqual(info.pk, 570)
        self.assertIsInstance(info.version, Version)
        self.assertGreater(info.version, "1.0")
        self.assertGreater(len(tuple(info.iter_versions())), 3)

        info2 = ExtensionInfo.find(info.uuid)
        self.assertEqual(info.json, info2.json)

        with TemporaryDirectory() as tmp:
            tmp_folder = Path(tmp)
            ext = info.install(tmp_folder)
            self.assertTrue((tmp_folder / info.uuid).is_dir())
            self.assertEqual(info.uuid, ext.uuid)
            ext.rmtree()
            self.assertFalse((tmp_folder / info.uuid).is_dir())
