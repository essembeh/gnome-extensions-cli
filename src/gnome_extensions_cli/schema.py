"""
gnome-extensions-cli
"""

import os
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path

from pydantic import BaseModel, Field


class Metadata(BaseModel):
    uuid: str
    name: str
    description: str | None = None
    extension_id: str | None = Field(alias="extension-id", default=None)
    shell_version: list[str] | None = Field(alias="shell-version", default=None)
    url: str | None = None
    version: str | int | float | None = None
    path: Path | None = None


class _Version(BaseModel):
    pk: int
    version: int


class AvailableExtension(BaseModel):
    uuid: str
    pk: int
    name: str
    description: str
    creator: str
    creator_url: str | None = None
    link: str | None = None
    icon: str | None = None
    screenshot: str | None = None
    shell_version_map: dict[str, _Version]
    version: int | None = None
    version_tag: int | None = None
    download_url: str | None = None


class Search(BaseModel):
    extensions: list[AvailableExtension]
    total: int
    numpages: int


@dataclass
class InstalledExtension:
    folder: Path

    @property
    def metadata_json(self) -> Path:
        return self.folder / "metadata.json"

    @property
    def read_only(self):
        return not os.access(str(self.folder), os.W_OK)

    @cached_property
    def metadata(self) -> Metadata:
        return Metadata.model_validate_json(self.metadata_json.read_text())

    @property
    def uuid(self) -> str:
        return self.metadata.uuid
