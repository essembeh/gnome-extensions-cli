from pathlib import Path

from gnome_extensions_cli.schema import AvailableExtension, Metadata, Search
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
                metadata = Metadata.model_validate_json(metadata_file.read_text())
                assert metadata is not None


def test_samples():
    samples_dir = Path(__file__).parent / "samples"
    assert samples_dir.is_dir()

    assert (
        AvailableExtension.model_validate_json(
            (samples_dir / "available.json").read_text()
        )
        is not None
    )
    assert (
        AvailableExtension.model_validate_json(
            (samples_dir / "available-alt.json").read_text()
        )
        is not None
    )
    assert (
        Metadata.model_validate_json((samples_dir / "installed.json").read_text())
        is not None
    )
    assert (
        Search.model_validate_json((samples_dir / "search.json").read_text())
        is not None
    )
