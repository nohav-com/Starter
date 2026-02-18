# -*- coding: utf-8 -*-
"""Class for wheel approach."""

import glob
import logging
import re
import shutil
import traceback
from pathlib import Path

from starter.app_preparation_by_type.common import (
    get_all_dependencies_setuptools_approach,
    get_list_of_files_and_timestamp
)

__all__ = ['WheelProcessing']

FILE_INSTALL = '*.whl'
FILES_CHANGED_FILTER = [FILE_INSTALL]
PYTHON_FILE_REGEX = "*.py"
ENTRY_POINT = 'if __name__ == "__main__"'
WHEEL_INSTALLATION_ARGS = ["-m", "pip", "install"]

logger = logging.getLogger(__name__)


class WheelProcessing():
    """Processing wheel package."""
    def __init__(self, /, **kwargs):
        self.app_path = kwargs.get("app_path", None)
        self.config_handler = kwargs.get("config_handler", None)
        self.platform_handler = kwargs.get("platform_handler", None)
        self.env_structure = kwargs.get("env_structure", None)
        self.context_handler = kwargs.get("context_handler", None)

    def install_and_start(self,
                          start_fresh=False,
                          continue_processing=True
                          ) -> bool:
        """Install dependencies, app and start it.

        Args:
        start_fresh = clear the environment and install it again
        continoue_processing = flag signaling 'try to install and start'

        Returns:
        True in case to signal next in the chain should countinue to
        try to install and start.
        """
        should_countinue = continue_processing
        installation_file = None
        if continue_processing and self.it_is_me():
            # Get installation file
            installation_file = self.get_app_file()
            if self.config_handler and start_fresh:
                should_countinue = False
                current_list = get_list_of_files_and_timestamp(
                    self.app_path,
                    filters=FILES_CHANGED_FILTER
                )
                if current_list:
                    self.config_handler.set_app_files(
                        current_list)
                try:
                    # Install extra dependencies
                    dependencies = get_all_dependencies_setuptools_approach(
                        self.app_path)
                    if dependencies:
                        self.platform_handler.install_dependencies(
                            dependencies
                        )
                    # # Get installation file
                    if installation_file:
                        args = self.get_install_args()
                        if args:
                            args.append(installation_file)
                            # Install app
                            self.platform_handler.install_app(
                                self.app_path,
                                args
                            )
                except Exception as e:
                    self.config_handler.remove_app_files()
                    logger.error("Installation of app failed. %s", e)
                    logger.error(traceback.format_exc())
                    raise
            # Can we continue
            if self.platform_handler and self.env_structure \
                    and installation_file:
                # Search for main file
                main_files, app_cwd = self.search_for_main_files(
                    self.env_structure.get_path_venv_folder(),
                    installation_file
                )
                # Windows - side branch
                if not main_files and self.context_handler:
                    # Get root folder
                    root_folder = self.context_handler.get_value_for_key(
                        "python_dir")
                    if root_folder:
                        main_files, app_cwd = self.search_for_main_files(
                            str(Path(root_folder).parent),
                            installation_file)
                # Copy all files placed in app folder besides wheel package
                # to app cwd(folder where app is installer)
                try:
                    extra_files = self.get_extra_files()
                    if extra_files:
                        self.copy_extra_files(extra_files, app_cwd)
                except Exception as e:
                    logger.error("Problem with copying extra files(%s).", e)
                    logger.error(traceback.format_exc())
                if main_files:
                    exception_counter = 0
                    for item in main_files:
                        try:
                            # Get app params if exists
                            app_params = self.config_handler.get_app_params()
                            # Start app
                            self.platform_handler.start_app(
                                app_cwd,
                                item,
                                app_params=app_params
                            )
                        except Exception as e:
                            logger.error(
                                "Attempt to start main file %s failed(%s).",
                                item, e)
                            exception_counter += 1
                            continue
                    if exception_counter == len(main_files):
                        raise RuntimeError(
                            """Could not properly start the app, because no
                               valid 'main file' has been
                               discovered(other option).""")
                    should_countinue = False
                else:
                    logger.error(
                        "Could not find any main files. Cannot start the app.")
                    # No point to continue to next type
                    should_countinue = False
            else:
                logger.warning("Cannot continue because unknown platform,\
                    during of wheel's installation.")

        return should_countinue

    def files_changed(self) -> bool:
        """Check if files/folders changed."""
        changed = False
        previous_list = self.config_handler.get_app_files()
        if previous_list and self.app_path:
            # Get current list
            current_list = get_list_of_files_and_timestamp(
                self.app_path,
                filters=FILES_CHANGED_FILTER
            )
            # Check old list vs. current list
            for key, value in current_list.items():
                if key in previous_list:
                    if previous_list[key] != value:
                        changed = True
                        break
                else:
                    changed = True
                    break
        elif not previous_list and self.app_path:
            changed = True
        return changed

    def search_for_main_files(self, venv_path, app_file) -> tuple:
        """Search for main file to be executed.

        Args:
        venv_path = path to venv folder
        app_file = path to wheel file

        Returns:
        tuple = (set of main files, folder where the app is installed)
        """
        all_main_files = []
        # Installed app folder
        installed_app_folder = None
        app_name = app_file and Path(app_file).name
        if venv_path and Path(venv_path).exists():
            try:
                site_packages = list(
                    Path(venv_path).rglob("lib/*/site-packages/*"))
                site_packages = list(
                    Path(venv_path).rglob("lib/site-packages/*")) if\
                    not site_packages else site_packages
                site_packages = list(
                    Path(venv_path).rglob("Lib/*/site-packages/*")) if\
                    not site_packages else site_packages
                site_packages = list(
                    Path(venv_path).rglob("Lib/site-packages/*")) if\
                    not site_packages else site_packages

                # Name of app derived from wheel package name --> installed
                # packages/modules match
                # Split name of wheel to parts by dash
                app_name_parts = app_name.split("-")
                matched_app_folder_name = app_name_parts.pop(0)
                # Continue
                for part in app_name_parts:
                    match = [package for package in site_packages if
                             Path(package).name.lower() ==
                             matched_app_folder_name]
                    if match:
                        installed_app_folder = match[0]
                        break
                    matched_app_folder_name += "-" + part
                # Lets search for main files
                if installed_app_folder:
                    config_main_file = \
                        self.config_handler.get_main_file()
                    if config_main_file:
                        # Lets find the file
                        founded_files = Path(installed_app_folder).\
                            rglob(config_main_file)
                        for file in founded_files:
                            all_main_files.append(str(file))
                    else:
                        # Find all relevant files
                        founded_files = Path(installed_app_folder).\
                            rglob(PYTHON_FILE_REGEX)
                        for file in founded_files:
                            try:
                                with open(
                                       str(file),
                                       "r",
                                       encoding='utf-') as file_read:
                                    if re.search(
                                            ENTRY_POINT,
                                            file_read.read()):
                                        all_main_files.append(str(file))
                            except Exception as e:
                                logger.error(
                                    "Search for main entry point in file\
                                        '%s' failed(%s).", file, e)
            except Exception as e:
                logger.error(
                    "Failed to find main file to start the app(%s).", e)
                logger.error(traceback.format_exc())

        return (set(all_main_files), installed_app_folder)

    def get_install_args(self) -> list:
        """Get args required for app installation.

        Example:
        returned list of args --> ['-m', 'pip', 'install']
        will be extended to format(for explanation)
        <path_to_pathon> -m pip -install <file>

        Returns:
        List of arguments.
        """
        return WHEEL_INSTALLATION_ARGS

    def it_is_me(self) -> bool:
        """Try to assume that this app can be installed via wheel.

        Returns:
        In case yes, returns True, othewise False
        """
        valid = False
        if self.app_path and Path(self.app_path).exists():
            if self.get_app_file():
                valid = True

        return valid

    def get_app_file(self) -> str | None:
        """Get app file(wheel file)."""
        file = None
        if self.app_path and Path(self.app_path).exists():
            file = glob.glob(
                str(Path(self.app_path).joinpath(FILE_INSTALL)))
            if file:
                file = file[0]
        return file

    def get_extra_files(self) -> list:
        """Get all extra files from app folder."""
        files = []
        if self.app_path and Path(self.app_path).exists():
            app_file_whl = self.get_app_file()
            for file in glob.glob(str(Path(self.app_path).joinpath("*"))):
                if app_file_whl != file:
                    files.append(file)
        return files

    def copy_extra_files(self, extra_files: list, destination: str):
        """Copy extra files/folders to app folder."""
        if extra_files and destination:
            for file in extra_files:
                destination_file = Path(destination).joinpath(
                                   Path(file).name)
                if Path(file).is_file():
                    if destination_file.exists():
                        destination_file.unlink(missing_ok=True)
                    shutil.copyfile(file, destination_file)
                elif Path(file).is_dir():
                    shutil.copytree(file, destination_file, dirs_exist_ok=True)
