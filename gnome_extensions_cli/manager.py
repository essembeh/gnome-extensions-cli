from abc import ABC, abstractmethod
from typing import List

from .schema import AvailableExtension, InstalledExtension


class ExtensionManager(ABC):
    @abstractmethod
    def get_current_shell_version(self) -> str:
        pass

    @abstractmethod
    def list_installed_extensions(self) -> List[InstalledExtension]:
        pass

    @abstractmethod
    def install_extension(self, ext: AvailableExtension) -> bool:
        pass

    @abstractmethod
    def uninstall_extension(self, ext: InstalledExtension):
        pass

    @abstractmethod
    def edit_extension(self, ext: InstalledExtension):
        pass

    @abstractmethod
    def list_enabled_uuids(self) -> List[str]:
        pass

    @abstractmethod
    def set_enabled_uuids(self, uuids: List[str]):
        pass

    def enable_uuids(self, uuids: List[str]) -> bool:
        old_uuids = set(self.list_enabled_uuids())
        new_uuids = old_uuids | set(uuids)
        if old_uuids != new_uuids:
            self.set_enabled_uuids(list(new_uuids))
            return True
        return False

    def disable_uuids(self, uuids: List[str]) -> bool:
        old_uuids = set(self.list_enabled_uuids())
        new_uuids = old_uuids - set(uuids)
        if old_uuids != new_uuids:
            self.set_enabled_uuids(list(new_uuids))
            return True
        return False
