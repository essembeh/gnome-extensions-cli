"""
Shared fixtures and helpers
"""

import json
from collections.abc import Iterable
from pathlib import Path

from pytest import fixture

from gnome_extensions_cli.manager import ExtensionManager
from gnome_extensions_cli.schema import AvailableExtension, InstalledExtension, Search
from gnome_extensions_cli.store import GnomeExtensionStore

SAMPLES_DIR = Path(__file__).parent / "samples"
SAMPLE_UUID = "todo.txt@bart.libert.gmail.com"
SAMPLE_PK = 570


def make_extension(folder: Path, uuid: str, version: int | str | None = 1) -> InstalledExtension:
    """
    Create a fake extension folder with its metadata.json
    """
    ext_dir = folder / uuid
    ext_dir.mkdir(parents=True)
    metadata: dict[str, object] = {"uuid": uuid, "name": uuid.split("@")[0], "shell-version": ["45"]}
    if version is not None:
        metadata["version"] = version
    (ext_dir / "metadata.json").write_text(json.dumps(metadata))
    return InstalledExtension(ext_dir)


class FakeExtensionManager(ExtensionManager):
    """
    In-memory manager recording the calls made by the commands
    """

    def __init__(
        self,
        installed: Iterable[InstalledExtension] = (),
        enabled: Iterable[str] = (),
        shell_version: str = "45.2",
    ) -> None:
        self.installed = list(installed)
        self.enabled = list(enabled)
        self.shell_version = shell_version
        self.installed_calls: list[AvailableExtension] = []
        self.uninstalled_calls: list[InstalledExtension] = []
        self.edited_calls: list[InstalledExtension] = []

    def get_current_shell_version(self) -> str:
        return self.shell_version

    def list_installed_extensions(self) -> list[InstalledExtension]:
        return list(self.installed)

    def install_extension(self, ext: AvailableExtension) -> bool:
        self.installed_calls.append(ext)
        return True

    def uninstall_extension(self, ext: InstalledExtension) -> None:
        self.uninstalled_calls.append(ext)
        self.installed.remove(ext)

    def edit_extension(self, ext: InstalledExtension) -> None:
        self.edited_calls.append(ext)

    def list_enabled_uuids(self) -> list[str]:
        return list(self.enabled)

    def set_enabled_uuids(self, uuids: list[str]) -> bool:
        self.enabled = list(uuids)
        return True


class SampleStore(GnomeExtensionStore):
    """
    Store answering from the recorded samples instead of the network
    """

    def find(self, ext: str | int, shell_version: str | None = None) -> AvailableExtension | None:
        if ext in (SAMPLE_UUID, SAMPLE_PK, str(SAMPLE_PK)):
            return AvailableExtension.model_validate_json((SAMPLES_DIR / "available.json").read_text())
        return None

    def search(self, motif: str, shell_version: str = "all", limit: int = 0) -> Iterable[AvailableExtension]:
        extensions = Search.model_validate_json((SAMPLES_DIR / "search.json").read_text()).extensions
        return extensions[:limit] if limit > 0 else extensions


@fixture
def sample_store() -> SampleStore:
    return SampleStore()


@fixture
def available_extension(sample_store: SampleStore) -> AvailableExtension:
    ext = sample_store.find(SAMPLE_UUID)
    assert ext is not None
    return ext
