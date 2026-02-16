# -*- coding: utf-8 -*-
"""Class contains everything related to differences by platform."""

import logging
import re
import shutil
import traceback
from pathlib import Path

from starter.app_preparation_by_platform.common import (
    CommonPreparationByPlatform
)
from starter.app_preparation_by_platform.platform_interface import (
    PlatformInterface
)

__all__ = ['WindowsPlatform']

PYTHON_PYINSTALLER_NAME_WIN = "app_starter.exe"

logger = logging.getLogger(__name__)


class WindowsPlatform(PlatformInterface, CommonPreparationByPlatform):
    def __init__(self, /, **kwargs):
        self.context_handler = kwargs.get("context_handler", None)
        self.cwd = kwargs.get("cwd", None)
        self.venv_folder = kwargs.get("venv_folder", None)
        CommonPreparationByPlatform().__init__()

    def pyinstaller_magic(self):
        """Logic tailored for pyinstaller."""
        try:
            _internal_from = self.cwd.parents[2].joinpath("_internal")
            path_to = self.venv_folder.joinpath("Scripts", "_internal")
            path_to_python = self.venv_folder.joinpath("Scripts")
            if path_to.exists():
                shutil.rmtree(str(path_to))
            path_to.mkdir()
            if _internal_from.exists() and path_to.exists():
                # Copy every file extra
                for file in _internal_from.iterdir():
                    # We have rename python --> python_real
                    if file.is_file() \
                            and re.search("python(.*).exe", file.name)\
                            and not re.search("pythonw(.*).exe", file.name):
                        shutil.copy(
                            str(file),
                            str(path_to_python.
                                joinpath("python_default.exe")))
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
                """Application of pyinstaller's magic for linux platform
                failed. %s""", e)
            logger.error(traceback.format_exc())
            raise

    def install_dependencies(self, dependencies=[]):
        """Installl list of dependencies.

        Args:
        dependencies = list of dependencies for installation
        """
        if dependencies:
            for dependency in dependencies:
                try:
                    self.install_dependency(dependency)
                except Exception:
                    logger.info("Installation of dependency %s failed.",
                                dependency)
                    logger.error(traceback.format_exc())
                    raise
        else:
            logger.info("No dependencies to install(linux handler).")

    def install_dependency(self, name=None):
        """Install dependency.

        Args:
        name = dependency to be installed (e.g. wheel==0.0.0 or wheel)
        """
        if name and self.context_handler:
            try:
                bin_path = self.context_handler.get_context().bin_path
                maginician = "maginician.py"
                future_maginician = Path(bin_path).joinpath(maginician)
                try:
                    # Copy from right source --> problem IDE vs. pyinstaller
                    current_maginician = str(Path(self.cwd).parent.joinpath(
                        maginician))
                    if Path(bin_path).exists():
                        shutil.copy(current_maginician, bin_path)
                        logger.info("""Copying 'maginician' script from '%s'
                                    was successfully
                                    finished.""", current_maginician)
                except Exception:
                    # Try it different way because of  pyinstaller
                    current_maginician = str(Path(self.cwd).parents[1]
                                             .joinpath(maginician))
                    if Path(bin_path).exists():
                        shutil.copy(current_maginician, bin_path)
                        logger.info("""Copying 'maginician' script from '%s'
                                    was successfully
                                    finished.""", current_maginician)
                # Put together args for installation
                if future_maginician.exists():
                    python = self.get_valid_python()
                    if python:
                        args = [python, str(future_maginician),
                                "--dependency", name]
                        self.install(name, args, bin_path)
                    else:
                        logger.error(
                            "Cannot install app, no python.exe founded")
                else:
                    logger.error("""Script '%s' doesn't exist.""",
                                 future_maginician)
            except Exception as e:
                logger.error(
                    "Cannot install dependency '%s'. Error: %s",
                    name, e)
                raise
        else:
            logger.info("No dependency to install(linux).")

    def get_valid_python(self) -> str:
        """Get path to right python exe file."""
        python = None
        if self.context_handler and self.context_handler.get_context().env_exe:
            if Path(self.context_handler.get_context().env_exe).name.lower()\
                    == PYTHON_PYINSTALLER_NAME_WIN:
                python = str(Path(self.context_handler.get_context().env_exe)
                             .parent.joinpath("python_default.exe"))
            else:
                python = str(self.context_handler.get_context().env_exe)
        return python if python else None

    def install_app(self, cwd, app_args=[]):
        """Installing app itself.

        Args:
        cwd = working directory(e.g. app folder)
        app_args = list of arguments for installation
                   e.g. ["-m", "pip", "install", "-e", "."]
        """
        try:
            if self.context_handler and cwd and app_args:
                python = self.get_valid_python()
                if python:
                    args = [python] + app_args
                    # TODO
                    # Production --> force reinstall, upgrade
                    # args += ["--upgrade",
                    #          "--force-reinstall",
                    #          "--no-cache-dir"]
                    logger.info("Installation of your app started.")
                    self.install("app", args, cwd)
                    logger.info("Installation of your app finished.")
                else:
                    logger.error(
                        "Cannot install app, no python.exe founded")
        except Exception as e:
            logger.error("Installation of app failed(%s).", e)
            logger.error(traceback.format_exc())
            raise

    def start_app(self, cwd, main_path, app_params=None):
        """Start the app.

        Args:
        cwd = working directory(e.g. app_folder)
        main_path = path to main file
        app_params = params to start app with
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
                    # logger.info(
                    #     "Start of app with {%s} was successful.")
        except Exception as e:
            logger.error("Start of app failed at windows platform(%s).", e)
            logger.error(traceback.format_exc())
            raise
