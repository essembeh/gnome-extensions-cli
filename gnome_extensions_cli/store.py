"""
gnome-extensions-cli
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from typing import Iterable, Optional, Tuple, Union

from requests import Session
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

from .schema import AvailableExtension, Search


@dataclass
class GnomeExtensionStore:
    """
    Interface to search for extensions on Gnome Website
    """

    url: str = "https://extensions.gnome.org"
    timeout: int = 20
    session: Session = field(init=False)

    def __post_init__(self):
        self.session = Session()
        self.session.mount(
            "https://",
            HTTPAdapter(
                max_retries=Retry(
                    total=2, backoff_factor=1, status_forcelist=[500, 502, 503, 504]
                )
            ),
        )

    def iter_fetch(
        self,
        extensions: Iterable[Union[str, int]],
        shell_version: Optional[str] = None,
        max_workers: Optional[int] = None,
    ) -> Iterable[Tuple[Union[str, int], Optional[AvailableExtension]]]:
        """
        Fetch multiple available extensions in parallel and yield when fetched
        """
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            jobs = {
                executor.submit(lambda u: self.find(u, shell_version), ext): ext
                for ext in extensions
            }
            for job in as_completed(jobs.keys()):
                uuid = jobs[job]
                yield (uuid, job.result())

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
        resp = self.session.get(
            f"{self.url}/extension-info/",
            params=params,
            timeout=self.timeout,
        )
        if resp.status_code == 404:
            return None
        resp.raise_for_status()

        return AvailableExtension.model_validate_json(resp.text)

    def find_by_pk(
        self, pk: int, shell_version: Optional[str] = None
    ) -> Optional[AvailableExtension]:
        """
        Find an extension by its pk
        """
        params = {"pk": str(pk)}
        if shell_version is not None:
            params["shell_version"] = str(shell_version)
        resp = self.session.get(
            f"{self.url}/extension-info/",
            params=params,
            timeout=self.timeout,
        )
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        return AvailableExtension.model_validate_json(resp.text)

    def search(
        self, motif: str, shell_version: str = "all", limit: int = 0
    ) -> Iterable[AvailableExtension]:
        """
        Search for extensions
        """
        params = {"search": motif, "shell_version": shell_version, "page": 1}
        found = 0
        while True:
            resp = self.session.get(
                f"{self.url}/extension-query/",
                params=params,
                timeout=self.timeout,
            )
            resp.raise_for_status()
            data = Search.model_validate_json(resp.text)
            for ext in data.extensions:
                yield ext
                found += 1
                if 0 < limit <= found:
                    return
            if params["page"] >= data.numpages:
                break
            params["page"] += 1
