"""
gnome-extensions-cli
"""

from abc import ABC, abstractmethod
from typing import List

from .schema import AvailableExtension, InstalledExtension


class ExtensionManager(ABC):
    """
    Abstract class to manipulate extensions

    """

    @abstractmethod
    def get_current_shell_version(self) -> str:
        """
        Return the current Gnome Shell version
        """

    @abstractmethod
    def list_installed_extensions(self) -> List[InstalledExtension]:
        """
        List installed extensions
        """

    @abstractmethod
    def install_extension(self, ext: AvailableExtension) -> bool:
        """
        Install given extension
        """

    @abstractmethod
    def uninstall_extension(self, ext: InstalledExtension):
        """
        Uninstall given extension
        """

    @abstractmethod
    def edit_extension(self, ext: InstalledExtension):
        """
        Edit preferences of given extension
        """

    @abstractmethod
    def list_enabled_uuids(self) -> List[str]:
        """
        List enabled extensions uuids
        """

    @abstractmethod
    def set_enabled_uuids(self, uuids: List[str]) -> bool:
        """
        Set enabled extensions uuids
        """

    def enable_uuids(self, uuids: List[str]) -> bool:
        """
        Enable given extensions
        """
        old_uuids = set(self.list_enabled_uuids())
        new_uuids = old_uuids | set(uuids)
        return old_uuids != new_uuids and self.set_enabled_uuids(list(new_uuids))

    def disable_uuids(self, uuids: List[str]) -> bool:
        """
        Disable given extensions
        """
        old_uuids = set(self.list_enabled_uuids())
        new_uuids = old_uuids - set(uuids)
        return old_uuids != new_uuids and self.set_enabled_uuids(list(new_uuids))
