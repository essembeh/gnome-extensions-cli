from gnome_extensions_cli.schema import AvailableExtension
from gnome_extensions_cli.store import GnomeExtensionStore

from .conftest import SAMPLE_PK, SAMPLE_UUID


def test_find() -> None:
    store = GnomeExtensionStore()

    ext = store.find_by_uuid(SAMPLE_UUID)
    assert ext is not None
    assert ext.pk == SAMPLE_PK
    assert ext.uuid == SAMPLE_UUID
    assert ext.download_url is None

    assert ext == store.find_by_pk(ext.pk)
    assert ext == store.find(SAMPLE_PK)
    assert ext == store.find(str(SAMPLE_PK))
    assert ext == store.find(SAMPLE_UUID)


def test_not_found() -> None:
    store = GnomeExtensionStore()

    assert store.find_by_uuid("this-extension-does-not-exists") is None


def test_shell_version() -> None:
    store = GnomeExtensionStore()

    ext = store.find_by_uuid(SAMPLE_UUID, shell_version="40")
    assert ext is not None
    assert ext.download_url is not None


def test_iter_fetch() -> None:
    store = GnomeExtensionStore()

    results = dict(store.iter_fetch([SAMPLE_UUID, "this-extension-does-not-exists"]))

    assert results["this-extension-does-not-exists"] is None
    found = results[SAMPLE_UUID]
    assert found is not None
    assert found.pk == SAMPLE_PK


def test_search() -> None:
    store = GnomeExtensionStore()

    results = list(store.search("todo", limit=3))

    assert 0 < len(results) <= 3
    assert all(isinstance(ext, AvailableExtension) for ext in results)
    assert any("todo" in ext.name.lower() for ext in results)
