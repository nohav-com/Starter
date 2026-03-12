# -*- coding: utf-8 -*-
"""A simple abstract class for defining platform-specific classes."""

from abc import ABC, abstractmethod

__all__ = ['PlatformInterface']


class PlatformInterface(ABC):
    @abstractmethod
    def pyinstaller_magic(self):
        """The logic and operations required by PyInstaller usage."""

    @abstractmethod
    def install_dependencies(self, dependencies: list = []):
        """Install a list of dependencies.

        Args:
        dependencies (list)= a list of dependencies
        """

    @abstractmethod
    def install_dependency(self, name: str | None = None):
        """Install the dependency with given name.

        Args:
        name (str | None)= name of the dependency
        """

    @abstractmethod
    def get_valid_python(self):
        """
        Get the path to valid python (exe) file.
        Distinguished by the format of the starter(dev vs. exe).
        """

    @abstractmethod
    def install_app(self, cwd: str, app_args: list = []):
        """Install the app.

        Args:
        cwd (str)= the current working directory
        app_args (list)= the install command in list format
            e.g.
            ['-m', 'pip', 'install', '-e', '.']
        """

    @abstractmethod
    def start_app(self, cwd: str, main_path: str, app_params=None):
        """Start the app.

        Args:
        cwd (str)= the current working directory(e.g. app folder)
        main_path (str)= path to the main file to be started
        app_params = the params for the app
        """

    @abstractmethod
    def context_needs_to_be_altered(self):
        """Check if the context needs to be altered.

        There may be a problem with Windows causing different behavior.
        """
