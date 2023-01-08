from gnome_extensions_cli.model import ExtensionInfo
from gnome_extensions_cli.utils import version_comparator


def test_find():
    info = ExtensionInfo.find(570)
    assert info is not None
    assert info.pk == 570
    assert info.version is not None
    assert len(tuple(info.iter_versions())) > 3

    info2 = ExtensionInfo.find(info.uuid)
    assert info.json == info2.json


def test_version():
    for a, b, out in (
        (1, 2, 1),
        (2, 10, 1),
        (None, 1, 1),
        ("1.2", "1.2.0", 1),
        (1, "1", 0),
        (1.2, "1.2", 0),
        (None, None, 0),
    ):
        assert version_comparator(a, b) == out
        assert version_comparator(b, a) == out * -1
