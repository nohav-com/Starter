# -*- coding: utf-8 -*-
"""Simple abstract class for classes defining type of package classes."""

from abc import ABC, abstractmethod

__all__ = ['TypeOfPackage']


class TypeOfPackage(ABC):

    @abstractmethod
    def it_is_me(self):
        """Check if app package/source code is my type.

        Returns:
        True in case postive identification, otherwise False
        """

    @abstractmethod
    def files_changed(self):
        """Check if files/folders changed from the last run of the app.

        Returns:
        True in case of changes happened, otherwise False
        """

    @abstractmethod
    def search_for_main_files(self, main_folder=None):
        """Search for main file in source code to be use to start app.

        Args:
        main_folder = where to start looking

        Returns:
        Path(s) to main file(s)
        """
