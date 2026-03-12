# -*- coding: utf-8 -*-
"""This class encapsulates all platform-specific differences and behaviors."""

import logging
import shutil
import traceback
from pathlib import Path

from starter.app_preparation_by_platform.common import (
    CommonPreparationByPlatform
)
from starter.app_preparation_by_platform.platform_interface import (
    PlatformInterface
)

__all__ = ['LinuxPlatform']

PYTHON_PYINSTALLER_NAME_LINUX = "app_starter"
PYTHON_DEFAULT_NAME_LINUX = "python_default"

logger = logging.getLogger(__name__)


class LinuxPlatform(PlatformInterface, CommonPreparationByPlatform):
    """Linux platform handler."""
    def __init__(self, /, **kwargs):
        self.context_handler = kwargs.get("context_handler", None)
        self.cwd = kwargs.get("cwd", None)
        self.venv_folder = kwargs.get("venv_folder", None)
        CommonPreparationByPlatform().__init__()

    def pyinstaller_magic(self):
        """Logic tailored for the PyInstaller."""
        try:
            _internal_from = self.cwd.parents[2].joinpath("_internal")
            path_to = self.venv_folder.joinpath("bin", "_internal")
            path_to_python = self.venv_folder.joinpath("bin")
            if path_to.exists():
                shutil.rmtree(str(path_to))
            path_to.mkdir()

            if _internal_from.exists() and path_to.exists():
                # Copy every file extra
                for file in _internal_from.iterdir():
                    # Rename the  python --> python_real
                    if file.is_file() and file.name.lower() in ["python"]:
                        shutil.copy(
                            str(file),
                            str(path_to_python.
                                joinpath(PYTHON_DEFAULT_NAME_LINUX)))
                    elif file.is_file():
                        if path_to.joinpath(file.name).exists():
                            path_to.joinpath(file.name).unlink(missing_ok=True)
                        shutil.copyfile(
                            str(file),
                            str(path_to.joinpath(file.name)))
                    elif file.is_dir():
                        shutil.copytree(
                            str(file),
                            str(path_to.joinpath(file.name)))

        except Exception as e:
            logger.error(
                """The application of PyInstaller's magic for the Linux
                platform failed: %s.""", e)
            logger.error(traceback.format_exc())
            raise

    def install_dependencies(self, dependencies: list = []):
        """Installl the list of dependencies.

        Args:
        dependencies (list)= a list of dependencies to be installed
        """
        if dependencies:
            for dependency in dependencies:
                try:
                    self.install_dependency(dependency)
                except Exception:
                    logger.error("Installation of dependency %s has failed.",
                                 dependency)
                    logger.error(traceback.format_exc())
                    raise
        else:
            logger.info("No dependencies to install(linux handler).")

    def install_dependency(self, name: str = None):
        """Install a dependency.

        Args:
        name (str)= the dependency to be installed (e.g. wheel==0.0.0 or wheel)
        """
        if name and self.context_handler:
            try:
                bin_path = self.context_handler.get_context().bin_path
                maginician = "maginician.py"
                future_maginician = Path(bin_path).joinpath(maginician)
                try:
                    # Copy from the correct source --> IDE vs. PyInstaller
                    current_maginician = str(Path(self.cwd).parent.joinpath(
                        maginician))
                    if Path(bin_path).exists():
                        shutil.copy(current_maginician, bin_path)
                        logger.info(""""Copying the 'maginician' script from
                                    '%s' was successfully
                                    completed.""", current_maginician)
                except Exception:
                    # Try a different approach because of PyInstaller
                    current_maginician = str(Path(self.cwd).parents[1]
                                             .joinpath(maginician))
                    if Path(bin_path).exists():
                        shutil.copy(current_maginician, bin_path)
                        logger.info("""Copying the 'maginician' script from
                                    '%s' was successfully
                                    completed.""", current_maginician)
                # Prepare the args for installation
                if future_maginician.exists():
                    python = self.get_valid_python()
                    if python:
                        args = [python, str(future_maginician),
                                "--dependency", name]
                        self.install(name, args, bin_path)
                    else:
                        logger.error(
                            "Cannot install the app: no python.exe found.")
                else:
                    logger.error("""The script '%s' does not exist.""",
                                 future_maginician)
            except Exception as e:
                logger.error(
                    "Cannot install dependency '%s'. Error: %s", name, e)
                logger.error(traceback.format_exc())
                raise
        else:
            logger.info("No dependency to install(linux).")

    def get_valid_python(self) -> str:
        """Get the path to the correct Python .exe file."""
        python = None
        if self.context_handler and self.context_handler.get_context().env_exe:
            if Path(self.context_handler.get_context().env_exe).name.lower()\
                    == PYTHON_PYINSTALLER_NAME_LINUX:
                python = str(Path(self.context_handler.get_context().env_exe)
                             .parent.joinpath(PYTHON_DEFAULT_NAME_LINUX))
            else:
                python = str(self.context_handler.get_context().env_exe)

        return python if python else None

    def install_app(self, cwd: str, app_args: list = []):
        """Installing the app itself.

        Args:
        cwd (str)= the working directory(e.g. app folder)
        app_args (list)= a list of arguments for installation
                   e.g. ["-m", "pip", "install", "-e", "."]
        """
        try:
            if self.context_handler and cwd and app_args:
                python = self.get_valid_python()
                if python:
                    args = [python] + app_args
                    # Production --> force reinstall, upgrade
                    # args += ["--upgrade",
                    #          "--force-reinstall",
                    #          "--no-cache-dir"]
                    logger.info(
                        "The installation of your app have started.")
                    self.install("app", args, cwd)
                    logger.info("The installation of your app is complete.")
                else:
                    logger.error(
                        "Cannot install the app, no python.exe found.")
        except Exception as e:
            logger.error("Installation of app failed.(%e)", e)
            logger.error(traceback.format_exc())
            raise

    def start_app(self, cwd: str, main_path: str, app_params: str = None):
        """Start the app.

        Args:
        cwd (str)= the working directory(e.g. app_folder)
        main_path (str)= the path to the main file
        app_params (str)= the params to start the app with
        """
        try:
            if Path(main_path).exists() and Path(cwd).exists():
                command = []
                python = self.get_valid_python()
                if python:
                    command.append(python)
                    command.append(main_path)
                    if app_params:
                        command += app_params.split()
                    logger.info(
                        "Starting your app with %s.",
                        main_path)
                    self.start_of_app("app", command, cwd)
                    logger.info(
                        "The start of the app with {%s} was successful.")
        except Exception as e:
            logger.error(
                "The start of the app failed on the windows platform(%s).", e)
            logger.error(traceback.format_exc())
            raise

    def context_needs_to_be_altered(self) -> tuple:
        """Returns the status if the context needs to be altered.

        Returns:
        A tuple containing (alter, exe_name, pyinstaller_exe_name)
        """
        alter = False
        return (alter, None, None)
