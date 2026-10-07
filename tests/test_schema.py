from pathlib import Path

from pytest import mark

from gnome_extensions_cli.schema import AvailableExtension, Metadata, Search

from .conftest import SAMPLES_DIR, make_extension


def test_samples() -> None:
    assert AvailableExtension.model_validate_json((SAMPLES_DIR / "available.json").read_text()).pk == 570
    assert AvailableExtension.model_validate_json((SAMPLES_DIR / "available-alt.json").read_text()).version is None
    assert Metadata.model_validate_json((SAMPLES_DIR / "installed.json").read_text()).version == 33
    assert len(Search.model_validate_json((SAMPLES_DIR / "search.json").read_text()).extensions) == 10


def test_system_metadata() -> None:
    for folder in filter(Path.is_dir, [Path("/usr/share/gnome-shell/extensions")]):
        for metadata_file in folder.glob("*/metadata.json"):
            assert Metadata.model_validate_json(metadata_file.read_text()).uuid == metadata_file.parent.name


@mark.parametrize("version", [1, 1.5, "1.5.2", None])
def test_metadata_version(version: int | float | str | None) -> None:
    metadata = Metadata.model_validate({"uuid": "a@x", "name": "a", "version": version})

    assert metadata.version == version


def test_installed_extension(tmp_path: Path) -> None:
    ext = make_extension(tmp_path, "a@x", version="1.2")

    assert ext.metadata_json == tmp_path / "a@x" / "metadata.json"
    assert ext.uuid == "a@x"
    assert ext.metadata.name == "a"
    assert ext.metadata.version == "1.2"
    assert ext.read_only is False
