import pytest

from gnome_extensions_cli.dbus import DbusExtensionManager, test_dbus_available


@pytest.mark.skipif(not test_dbus_available(True), reason="DBus is not available")
def test_dbus():
    manager = DbusExtensionManager()

    assert manager.get_current_shell_version() is not None

    all_extensions = manager.list_installed_extensions()
    assert len(all_extensions) > 0

    enabled_extensions = manager.list_enabled_uuids()
    assert len(enabled_extensions) > 0

    assert len(all_extensions) > len(enabled_extensions)
