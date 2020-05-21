import unittest

from gnome_extensions_cli.model import ExtensionInfo
from gnome_extensions_cli.utils import version_comparator


class ExtTests(unittest.TestCase):
    def test_find(self):
        info = ExtensionInfo.find(570)
        self.assertIsNotNone(info)
        self.assertEqual(info.pk, 570)
        self.assertIsNotNone(info.version)
        self.assertGreater(len(tuple(info.iter_versions())), 3)

        info2 = ExtensionInfo.find(info.uuid)
        self.assertEqual(info.json, info2.json)

    def test_version(self):
        for a, b, out in (
            (1, 2, 1),
            (2, 10, 1),
            (None, 1, 1),
            ("1.2", "1.2.0", 1),
            (1, "1", 0),
            (1.2, "1.2", 0),
            (None, None, 0),
        ):
            self.assertEqual(version_comparator(a, b), out)
            self.assertEqual(version_comparator(b, a), out * -1)
