"""
gnome-extensions-cli
"""

from operator import itemgetter
from pathlib import Path
from traceback import print_exc
from typing import List

from .manager import ExtensionManager
from .schema import AvailableExtension, InstalledExtension

DBUS_INTERFACE = "org.gnome.Shell"
DBUS_PATH = "/org/gnome/Shell"


def test_dbus_available(debug: bool = False) -> bool:
    """
    Test if DBus is available
    """
    try:
        from gi.repository import Gio  # pylint: disable=import-outside-toplevel

        dbus = Gio.bus_get_sync(Gio.BusType.SESSION, None)
        return dbus is not None
    except BaseException:  # pylint: disable=broad-except
        if debug:
            print_exc()
    return False


class DbusExtensionManager(ExtensionManager):
    """
    Handle extensions using DBus messages, just like recommended Firefox extensions on Gnome website

    dbus schema: /usr/share/dbus-1/interfaces/org.gnome.Shell.Extensions.xml
    """

    def __init__(self):
        from gi.repository import Gio  # pylint: disable=import-outside-toplevel

        dbus = Gio.bus_get_sync(Gio.BusType.SESSION, None)
        self.proxy_extensions = Gio.DBusProxy.new_sync(
            dbus,
            Gio.DBusProxyFlags.NONE,
            None,
            DBUS_INTERFACE,
            "/org/gnome/Shell",
            "org.gnome.Shell.Extensions",
            None,
        )
        self.proxy_properties = Gio.DBusProxy.new_sync(
            dbus,
            Gio.DBusProxyFlags.NONE,
            None,
            DBUS_INTERFACE,
            "/org/gnome/Shell",
            "org.freedesktop.DBus.Properties",
            None,
        )
        self.settings = Gio.Settings.new("org.gnome.shell")

    def get_current_shell_version(self) -> str:
        return self.proxy_properties.Get("(ss)", DBUS_INTERFACE, "ShellVersion")

    def list_installed_extensions(self) -> List[InstalledExtension]:
        return list(
            map(
                InstalledExtension,
                filter(
                    Path.exists,
                    map(
                        Path,
                        filter(
                            None,
                            map(
                                itemgetter("path"),
                                self.proxy_extensions.ListExtensions().values(),
                            ),
                        ),
                    ),
                ),
            )
        )

    def install_extension(self, ext: AvailableExtension) -> bool:
        return (
            self.proxy_extensions.InstallRemoteExtension("(s)", ext.uuid)
            == "successful"
        )

    def uninstall_extension(self, ext: InstalledExtension):
        self.proxy_extensions.UninstallExtension("(s)", ext.uuid)

    def edit_extension(self, ext: InstalledExtension):
        self.proxy_extensions.LaunchExtensionPrefs("(s)", ext.uuid)

    def list_enabled_uuids(self) -> List[str]:
        return list(self.settings["enabled-extensions"])

    def set_enabled_uuids(self, uuids: List[str]) -> bool:
        self.settings["enabled-extensions"] = uuids
        return True
