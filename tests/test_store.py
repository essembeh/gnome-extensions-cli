from gnome_extensions_cli.store import GnomeExtensionStore


def test_find():
    store = GnomeExtensionStore()

    ext = store.find_by_uuid("todo.txt@bart.libert.gmail.com")
    assert ext is not None
    assert ext.pk == 570
    assert ext.uuid == "todo.txt@bart.libert.gmail.com"
    assert ext.download_url is None

    assert ext == store.find_by_pk(ext.pk)


def test_not_found():
    store = GnomeExtensionStore()

    ext = store.find_by_uuid("this-extension-does-not-exists")
    assert ext is None


def test_shell_version():
    store = GnomeExtensionStore()

    ext = store.find_by_uuid("todo.txt@bart.libert.gmail.com", shell_version="40")
    assert ext is not None
    assert ext.download_url is not None
