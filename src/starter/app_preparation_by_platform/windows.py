"""Class contains everything related to differences by platform."""
import logging
import os
import re
import shutil
from .common import CommonPreparationByPlatform
from .platform_interface import PlatformInterface
from pathlib import Path

__all__ = ['WindowsPlatform']

PYTHON_PYINSTALLER_NAME = "app_starter.exe"

logger = logging.getLogger(__name__)


class WindowsPlatform(PlatformInterface, CommonPreparationByPlatform):
    def __init__(self, *args, **kwargs):
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
                failed. {%s}""" % e)

    def install_dependencies(self, dependencies=[]):
        """Installl list of dependencies

        Params:
        dependencies = list of dependencies for installation
        """
        if dependencies:
            for dependency in dependencies:
                try:
                    self.install_dependency(dependency)
                except Exception:
                    logger.info("Installation of dependency {%s} failed."
                                % dependency)
                    # Keep rolling
                    continue
        else:
            logger.info("No dependencies to install(linux handler).")

    def install_dependency(self, name=None):
        """Install dependency

        Params:
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
                        logger.info("""Copying 'maginician' script from '{%s}'
                                    was successfully
                                    finished.""" % current_maginician)
                except Exception:
                    current_maginician = str(Path(self.cwd).parents[1]
                                             .joinpath(maginician))
                    if Path(bin_path).exists():
                        shutil.copy(current_maginician, bin_path)
                        logger.info("""Copying 'maginician' script from '{%s}'
                                    was successfully
                                    finished.""" % current_maginician)
                # Put together args for installation
                if future_maginician.exists():
                    # Standart args list (IDE)
                    python = self.get_valid_python()
                    if python:
                        args = [python, str(future_maginician),
                                "--dependency", name]
                        self.install(name, args, bin_path)
                    else:
                        logger.error(
                            "Cannot install app, no python.exe founded")
                else:
                    logger.error("""Script '{%s}' doesn't exist."""
                                 % future_maginician)
            except Exception as e:
                logger.error(
                    "Cannot install dependency '{%s}'. Error: {%s}"
                    % (name, e))
        else:
            logger.info("No dependency to install(linux).")

    def get_valid_python(self):
        """Get path to right python exe file."""
        python = None
        if self.context_handler and self.context_handler.get_context().env_exe:
            if Path(self.context_handler.get_context().env_exe).name.lower()\
                    == PYTHON_PYINSTALLER_NAME:
                python = str(Path(self.context_handler.get_context().env_exe)
                             .parent.joinpath("python_default.exe"))
            else:
                python = str(self.context_handler.get_context().env_exe)
        return python

    def install_app(self, cwd, app_args=[]):
        """Installing app itself

        Params:
        cwd = working directory(e.g. app folder)
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
                    self.install("app", args, cwd)
                else:
                    logger.error(
                        "Cannot install app, no python.exe founded")
        except Exception as e:
            logger.error("Installation of app failed. {%s}" % e)

    def start_app(self, cwd, main_path, app_params=None):
        """Start the app.

        Params:
        cwd = working directory(e.g. app_folder)
        main_path = path to main file
        app_params = params to start app with
        """
        try:
            if Path(main_path).exists() and Path(cwd).exists():
                os.chdir(cwd)
                command = self.get_valid_python()
                command += f" {main_path}"
                if app_params:
                    command += f" {app_params}"
                if command:
                    os.system(command)
        except Exception as e:
            logger.error("Start of application failed. {%s}" % e)