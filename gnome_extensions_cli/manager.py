#!/usr/bin/python

import subprocess
import sys
from abc import ABC, abstractmethod, abstractproperty
from collections import OrderedDict
from dataclasses import dataclass, field
from json import load
from os.path import expanduser
from pathlib import Path
from re import finditer, fullmatch
from shutil import rmtree
from tempfile import NamedTemporaryFile
from urllib.request import urlopen
from zipfile import ZipFile

from gi.repository import Gio

from gnome_extensions_cli.model import Extension, ExtensionInfo


class ExtensionManager(ABC):
    @abstractproperty
    def current_shell_version(self):
        pass

    @abstractmethod
    def list_installed_extensions(self):
        pass

    @abstractmethod
    def install_extension(self, info: ExtensionInfo):
        pass

    @abstractmethod
    def uninstall_extension(self, ext: Extension):
        pass

    @abstractmethod
    def edit_extension(self, ext: Extension):
        pass

    @abstractmethod
    def get_enabled_uuids(self):
        pass

    @abstractmethod
    def set_enabled_uuids(self, *args):
        pass

    def __getitem__(self, uuid: str):
        return next(
            filter(lambda x: x.uuid == uuid, self.list_installed_extensions()), None
        )

    def enable_uuid(self, *args):
        old_uuids = set(self.get_enabled_uuids())
        new_uuids = old_uuids | set(args)
        if old_uuids != new_uuids:
            self.set_enabled_uuids(*new_uuids)
            return True
        return False

    def disable_uuid(self, *args):
        old_uuids = set(self.get_enabled_uuids())
        new_uuids = old_uuids - set(args)
        if old_uuids != new_uuids:
            self.set_enabled_uuids(*new_uuids)
            return True
        return False


@dataclass
class FilesystemExtensionManager(ExtensionManager):
    user_folder: Path = field(
        default=Path(expanduser("~/.local/share/gnome-shell/extensions"))
    )
    auto_enable: bool = field(default=True)

    @property
    def current_shell_version(self):
        for line in (
            subprocess.check_output(["gnome-shell", "--version"]).decode().splitlines()
        ):
            m = fullmatch(r"GNOME Shell (?P<version>[0-9.]+)", line)
            if m:
                return m.group("version")

    def list_installed_extensions(self):
        out = OrderedDict()
        for folder in filter(
            Path.is_dir,
            (
                Path("/usr/share/gnome-shell/extensions"),
                Path("/usr/local/share/gnome-shell/extensions"),
                self.user_folder,
            ),
        ):
            for subfolder in sorted(folder.iterdir()):
                metadata_file = subfolder / "metadata.json"
                if metadata_file.is_file():
                    with metadata_file.open() as fp:
                        metadata = load(fp)
                        out[metadata["uuid"]] = Extension(
                            metadata["uuid"],
                            metadata["name"],
                            metadata.get("version"),
                            subfolder,
                        )
        return tuple(out.values())

    def install_extension(self, info: ExtensionInfo):
        target_dir = self.user_folder / info.uuid
        if target_dir.exists():
            rmtree(str(target_dir))
        target_dir.mkdir(parents=True)
        try:
            with NamedTemporaryFile() as fp:
                with urlopen(info.recommended_url) as stream:
                    fp.write(stream.read())
                fp.seek(0)
                with ZipFile(fp.name) as zf:
                    for member in zf.namelist():
                        zf.extract(member, path=target_dir)
            if self.auto_enable:
                self.enable_uuid(info.uuid)
        except BaseException:
            rmtree(str(target_dir))
            return False
        return True

    def uninstall_extension(self, ext: Extension):
        if ext.read_only:
            raise ValueError("Cannot uninstall a system extension")
        if self.auto_enable:
            self.disable_uuid(ext.uuid)
        rmtree(str(ext.folder))
        return True

    def edit_extension(self, ext: Extension):
        raise NotImplementedError()

    def get_enabled_uuids(self):
        return tuple(
            map(
                lambda m: m.group("uuid"),
                finditer(
                    r"'(?P<uuid>[^']+)'",
                    subprocess.check_output(
                        ["gsettings", "get", "org.gnome.shell", "enabled-extensions"]
                    ).decode(),
                ),
            )
        )

    def set_enabled_uuids(self, *args):
        subprocess.check_call(
            [
                "gsettings",
                "set",
                "org.gnome.shell",
                "enabled-extensions",
                "[{0}]".format(",".join(map('"{0}"'.format, args))),
            ]
        )
        self.restart_gnome_shell()

    def restart_gnome_shell(self):
        p = subprocess.run(
            [
                "dbus-send",
                "--session",
                "--type=method_call",
                "--dest=org.gnome.Shell",
                "/org/gnome/Shell",
                "org.gnome.Shell.Eval",
                'string:"global.reexec_self();"',
            ]
        )
        if p.returncode != 0:
            print(
                "Could not restart Gnome Shell, you have to restart it", file=sys.stderr
            )
        return p.returncode


class DbusExtensionManager(ExtensionManager):
    # dbus schema: /usr/share/dbus-1/interfaces/org.gnome.Shell.Extensions.xml

    INTERFACE = "org.gnome.Shell"
    PATH = "/org/gnome/Shell"

    def __init__(self):
        dbus = Gio.bus_get_sync(Gio.BusType.SESSION, None)
        self.proxy_extensions = Gio.DBusProxy.new_sync(
            dbus,
            Gio.DBusProxyFlags.NONE,
            None,
            DbusExtensionManager.INTERFACE,
            DbusExtensionManager.PATH,
            "org.gnome.Shell.Extensions",
            None,
        )
        self.proxy_properties = Gio.DBusProxy.new_sync(
            dbus,
            Gio.DBusProxyFlags.NONE,
            None,
            DbusExtensionManager.INTERFACE,
            DbusExtensionManager.PATH,
            "org.freedesktop.DBus.Properties",
            None,
        )
        self.settings = Gio.Settings.new("org.gnome.shell")

    @property
    def current_shell_version(self):
        return self.proxy_properties.Get(
            "(ss)", DbusExtensionManager.INTERFACE, "ShellVersion"
        )

    def list_installed_extensions(self):
        def factory(kv):
            uuid, data = kv
            version = data.get("version")
            if isinstance(version, float) and int(version) == version:
                version = int(version)
            version = str(version) if version is not None else None
            return Extension(uuid, data["name"], version, data["path"])

        return tuple(map(factory, self.proxy_extensions.ListExtensions().items()))

    def install_extension(self, info: ExtensionInfo):
        return (
            self.proxy_extensions.InstallRemoteExtension("(s)", info.uuid)
            == "successful"
        )

    def uninstall_extension(self, ext: Extension):
        self.proxy_extensions.UninstallExtension("(s)", ext.uuid)

    def edit_extension(self, ext: Extension):
        self.proxy_extensions.LaunchExtensionPrefs("(s)", ext.uuid)

    def get_enabled_uuids(self):
        return self.settings["enabled-extensions"]

    def set_enabled_uuids(self, *args):
        self.settings["enabled-extensions"] = args
