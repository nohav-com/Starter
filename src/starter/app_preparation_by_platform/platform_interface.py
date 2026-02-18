# -*- coding: utf-8 -*-
"""Simple abstract class for classes defining platform."""

from abc import ABC, abstractmethod

__all__ = ['PlatformInterface']


class PlatformInterface(ABC):
    @abstractmethod
    def pyinstaller_magic(self):
        """Logic and operations required by pyinstaller use."""

    @abstractmethod
    def install_dependencies(self, dependencies=[]):
        """Install list of dependencies.

        Args:
        dependencies = list of dependencies
        """

    @abstractmethod
    def install_dependency(self, name=None):
        """Install dependency of given name.

        Args:
        name = name of the dependency
        """

    @abstractmethod
    def get_valid_python(self):
        """
        Get path to valid python (exe) file.
        Distinguished by format of starter(dev vs. exe).
        """

    @abstractmethod
    def install_app(self, cwd, app_args=[]):
        """Install app.

        Args:
        cwd = current working directory
        app_args = install comamnd in list format
            e.g.
            ['-m', 'pip', 'install', '-e', '.']
        """

    @abstractmethod
    def start_app(self, cwd, main_path, app_params=None):
        """Startr the app.

        Args:
        cwd = current working directory(e.g. app folder)
        main_path = path to main file to be started
        app_params = params of app
        """

    @abstractmethod
    def context_needs_to_be_altered(self):
        """Check if context needs to be altered.

        Problem with windows and different behaviour.
        """
