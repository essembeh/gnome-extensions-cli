"""
gnome-extensions-cli
"""

import os
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path
from typing import Dict, List, Optional, Union

from pydantic import BaseModel, Field


class Metadata(BaseModel):
    uuid: str
    name: str
    description: Optional[str] = None
    extension_id: Optional[str] = Field(alias="extension-id", default=None)
    shell_version: Optional[List[str]] = Field(alias="shell-version", default=None)
    url: Optional[str] = None
    version: Optional[Union[str, int]] = None
    path: Optional[Path] = None


class _Version(BaseModel):
    pk: int
    version: int


class AvailableExtension(BaseModel):
    uuid: str
    pk: int
    name: str
    description: str
    creator: str
    creator_url: Optional[str] = None
    link: Optional[str] = None
    icon: Optional[str] = None
    screenshot: Optional[str] = None
    shell_version_map: Dict[str, _Version]
    version: Optional[int] = None
    version_tag: Optional[int] = None
    download_url: Optional[str] = None


class Search(BaseModel):
    extensions: List[AvailableExtension]
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
