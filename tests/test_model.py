from pathlib import Path

from gnome_extensions_cli.schema import Metadata
from gnome_extensions_cli.utils import version_comparator


def test_version():
    for a, b, out in (
        (1, 2, 1),
        (2, 10, 1),
        (None, 1, 1),
        ("1.2", "1.2.0", 0),
        (1, "1", 0),
        (1.2, "1.2", 0),
        (None, None, 0),
    ):
        assert version_comparator(a, b) == out
        assert version_comparator(b, a) == out * -1


def test_schema():

    for folder in filter(
        Path.is_dir,
        [
            Path("/usr/share/gnome-shell/extensions"),
            Path("/usr/local/share/gnome-shell/extensions"),
        ],
    ):
        for sub in folder.iterdir():
            metadata_file = sub / "metadata.json"
            if metadata_file.exists():
                metadata = Metadata.parse_file(metadata_file)
                assert metadata is not None
