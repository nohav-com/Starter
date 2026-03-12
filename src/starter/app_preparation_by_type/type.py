# -*- coding: utf-8 -*-
"""Simple abstract class for defining package type classes."""

from abc import ABC, abstractmethod

__all__ = ['TypeOfPackage']


class TypeOfPackage(ABC):
    """Simple interface."""
    @abstractmethod
    def it_is_me(self):
        """Check if the app package/source code matches my type.

        Returns:
        True if the identification is positive, otherwise False.
        """

    @abstractmethod
    def files_changed(self):
        """Check if files/folders have changed since the last run of the app.

        Returns:
        True if changes occurred, otherwise False.
        """

    @abstractmethod
    def search_for_main_files(self, main_folder=None):
        """Search for the main file in the source code to use for startign the
        app.

        Args:
        main_folder = the folder where the search should begin

        Returns:
        Path(s) to the main file(s)
        """
