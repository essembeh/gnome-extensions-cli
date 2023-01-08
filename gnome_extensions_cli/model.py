from dataclasses import dataclass
from distutils.version import LooseVersion
from os import W_OK, access
from pathlib import Path
from typing import ClassVar

import requests

from gnome_extensions_cli.utils import get_shell_version

GNOME_URL = "https://extensions.gnome.org"
GNOME_SHELL_VERSION = get_shell_version()


@dataclass
class ExtensionInfo:
    json: object
    CACHE: ClassVar = {}

    @classmethod
    def fetch_info(cls, value, shell_version: str = None):
        url = "{url}/extension-info/?{field}={value}".format(
            url=GNOME_URL, field="pk" if isinstance(value, int) else "uuid", value=value
        )
        if shell_version:
            url += "&shell_version={shell_version}".format(shell_version=shell_version)
        req = requests.get(url)
        if req.status_code == 200:
            return ExtensionInfo(req.json())

    @classmethod
    def find(cls, value):
        if isinstance(value, str) and value.isdigit():
            value = int(value)
        for info in cls.CACHE.values():
            if (isinstance(value, int) and info.pk == value) or (
                isinstance(value, str) and info.uuid == value
            ):
                return info
        out = cls.fetch_info(value, shell_version=GNOME_SHELL_VERSION)
        if out:
            cls.CACHE[out.uuid] = out
        return out

    def iter_versions(self, sort_desc: bool = False):
        data = self.json["shell_version_map"]
        for shell_version in sorted(data.keys(), reverse=sort_desc, key=LooseVersion):
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
        return self.json.get("version")

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

    def __str__(self):
        return "{s.uuid} (v{s.version})".format(s=self) if self.version else self.uuid


@dataclass
class Extension:
    uuid: str
    name: str
    version: str
    folder: Path

    @property
    def read_only(self):
        return not access(str(self.folder), W_OK)

    @property
    def info(self):
        return ExtensionInfo.find(self.uuid)

    def __str__(self):
        return "{s.uuid} (v{s.version})".format(s=self) if self.version else self.uuid
