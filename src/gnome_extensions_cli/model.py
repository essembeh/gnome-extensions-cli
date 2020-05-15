from dataclasses import dataclass, field
from json import load as jsonload
from pathlib import Path
from shutil import rmtree
from tempfile import NamedTemporaryFile
from typing import ClassVar
from urllib.request import urlopen
from zipfile import ZipFile

import requests

from gnome_extensions_cli.utils import (
    GNOME_SHELL_VERSION,
    GNOME_URL,
    SHELL_SYSTEM_FOLDERS,
    enable_extensions,
    list_enabled_extensions,
)
from gnome_extensions_cli.version import Version


@dataclass
class ExtensionInfo:
    json: object
    gnome_shell_target_version: ClassVar[str] = field(init=False)

    @classmethod
    def build_ext_url(cls, field: str, value: str, shell_version: str = None):
        out = "{url}/extension-info/?{field}={value}".format(
            url=GNOME_URL, field=field, value=value
        )
        if shell_version:
            out += "&shell_version={shell_version}".format(shell_version=shell_version)
        return out

    @classmethod
    def find(cls, value):
        field = "uuid"
        if isinstance(value, int) or (isinstance(value, str) and value.isdigit()):
            field = "pk"
        url = ExtensionInfo.build_ext_url(
            field, value, shell_version=GNOME_SHELL_VERSION
        )
        req = requests.get(url)
        if req.status_code == 200:
            return ExtensionInfo(req.json())

    def iter_versions(self, sort_desc: bool = False):
        data = {Version(k): v for k, v in self.json["shell_version_map"].items()}
        for shell_version in sorted(data.keys(), reverse=sort_desc):
            tag, version = data[shell_version]["pk"], data[shell_version]["version"]
            yield {
                "shell_version": shell_version,
                "tag": tag,
                "version": version,
                "url": "{base}/download-extension/{uuid}.shell-extension.zip?version_tag={tag}".format(
                    base=GNOME_URL, uuid=self.uuid, tag=tag
                ),
            }

    @property
    def name(self):
        return self.json["name"]

    @property
    def description(self):
        return self.json["description"]

    @property
    def uuid(self):
        return self.json["uuid"]

    @property
    def pk(self):
        return self.json["pk"]

    @property
    def version(self):
        return Version(self.json["version"]) if "version" in self.json else None

    @property
    def tag(self):
        return self.json.get("version_tag")

    @property
    def recommended_url(self):
        urlpath = self.json.get("download_url")
        if not urlpath:
            raise ValueError("No compatible version found for {s.uuid}".format(s=self))
        return GNOME_URL + urlpath

    @property
    def url(self):
        return "{base}/extension/{s.pk}".format(base=GNOME_URL, s=self)

    def install(self, extensions_root_dir: Path):
        target_dir = extensions_root_dir / self.uuid
        if target_dir.exists():
            raise ValueError("Extension folder {0} already exists".format(target_dir))
        target_dir.mkdir(parents=True)
        try:
            with NamedTemporaryFile() as fp:
                with urlopen(self.recommended_url) as stream:
                    fp.write(stream.read())
                fp.seek(0)
                with ZipFile(fp.name) as zf:
                    for member in zf.namelist():
                        zf.extract(member, path=target_dir)
            return InstalledExtension(target_dir, False)
        except BaseException as e:
            rmtree(str(target_dir))
            raise e


@dataclass
class InstalledExtension:
    folder: Path
    read_only: bool
    _info: ExtensionInfo = field(init=False, default=None)

    @staticmethod
    def iter_installed(user_folder: Path, only_user=False):
        if not only_user:
            for root_folder in filter(lambda d: d.is_dir(), SHELL_SYSTEM_FOLDERS):
                for subfolder in sorted(
                    filter(
                        lambda d: (d / "metadata.json").is_file(), root_folder.iterdir()
                    )
                ):
                    yield InstalledExtension(subfolder, True)
        if user_folder and user_folder.is_dir():
            for subfolder in sorted(
                filter(lambda d: (d / "metadata.json").is_file(), user_folder.iterdir())
            ):
                yield InstalledExtension(subfolder, False)

    @property
    def metadata(self):
        with (self.folder / "metadata.json").open() as fp:
            return jsonload(fp)

    @property
    def name(self):
        return self.metadata.get("name")

    @property
    def version(self):
        return Version(self.metadata["version"]) if "version" in self.metadata else None

    @property
    def uuid(self):
        return self.metadata.get("uuid")

    @property
    def info(self):
        if self._info is None:
            self._info = ExtensionInfo.find(self.uuid) or False
        return self._info if isinstance(self._info, ExtensionInfo) else None

    @property
    def enabled(self):
        return self.uuid in list_enabled_extensions()

    def rmtree(self):
        if self.read_only:
            raise ValueError("Cannot uninstall a system extension")
        rmtree(str(self.folder))

    def enable(self):
        return enable_extensions([self.uuid], enable=True)

    def disable(self):
        return enable_extensions([self.uuid], enable=False)
