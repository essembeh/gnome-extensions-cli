from dataclasses import dataclass
from typing import Optional, Union

import requests

from .schema import AvailableExtension


@dataclass
class GnomeExtensionStore:
    """
    Interface to search for extensions on Gnome Website
    """

    url: str = "https://extensions.gnome.org"
    timeout: int = 20

    def find(
        self, ext: Union[str, int], shell_version: Optional[str] = None
    ) -> Optional[AvailableExtension]:
        """
        Find an extension by its uuid or pk
        """
        if isinstance(ext, int):
            return self.find_by_pk(ext, shell_version=shell_version)
        if isinstance(ext, str) and ext.isnumeric():
            return self.find_by_pk(int(ext), shell_version=shell_version)
        return self.find_by_uuid(ext, shell_version=shell_version)

    def find_by_uuid(
        self, uuid: str, shell_version: Optional[str] = None
    ) -> Optional[AvailableExtension]:
        """
        Find an extension by its uuid
        """
        params = {"uuid": uuid}
        if shell_version is not None:
            params["shell_version"] = str(shell_version)
        resp = requests.get(
            f"{self.url}/extension-info/",
            params=params,
            timeout=self.timeout,
        )
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        return AvailableExtension.parse_raw(resp.content)

    def find_by_pk(
        self, pk: int, shell_version: Optional[str] = None
    ) -> Optional[AvailableExtension]:
        """
        Find an extension by its pk
        """
        params = {"pk": str(pk)}
        if shell_version is not None:
            params["shell_version"] = str(shell_version)
        resp = requests.get(
            f"{self.url}/extension-info/",
            params=params,
            timeout=self.timeout,
        )
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        return AvailableExtension.parse_raw(resp.content)
