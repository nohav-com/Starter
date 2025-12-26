"""Class for processing the old school style requirements file(s)."""

import glob
import logging
import re
import os
from pathlib import Path

from .dummy_setup import DummySetup
from .common import (
    get_list_of_files_and_timestamp,
    get_all_dependencies_setuptools_approach
)


__all__ = ['SetupProcessing']

FILES_CHANGED_FILTER = ["**/*.py"]
REQUIRED_FILES_REGEX = "(.*)requirements(.*)"
REQUIRED_FILES = ['setup.py']
ENTRY_POINT = 'if __name__ == "__main__"'
SETUP_INSTALLATION_ARGS = ["-m", "pip", "install", "-e", "."]


logger = logging.getLogger(__name__)


class SetupProcessing():
    """This class doing searching, checking the app's requirements the old 
       school way. Searching for file(s) 'requirements*,*'."""

    def __init__(self, *args, **kwargs):
        self.app_path = kwargs.get("app_path", None)
        self.config_handler = kwargs.get("config_handler", None)
        self.platform_handler = kwargs.get("platform_handler", None)

        self.setup_dummy = DummySetup()

    def install_and_start(self,
                          start_fresh=False,
                          continue_processing=True
                          ) -> bool:
        """Install dependencies, app and start it"""
        next = True
        if continue_processing and self.it_is_me():
            # Check if we are to suppose to install
            if start_fresh and self.platform_handler:
                next = False
                # Store current list to config file
                current_list = get_list_of_files_and_timestamp(
                    self.app_path,
                    filters=FILES_CHANGED_FILTER + REQUIRED_FILES
                )
                if current_list:
                    self.config_handler.set_app_files(current_list)
                # Setup tool approach --> *requirement*
                dependencies = get_all_dependencies_setuptools_approach(
                    self.app_path)
                if dependencies:
                    self.platform_handler.install_dependencies(
                        dependencies
                    )
                # Install app
                try:
                    self.platform_handler.install_app(
                        self.app_path,
                        self.get_install_args()
                    )
                except Exception as e:
                    logger.error("Installation of app failed. {%s}" % e)
            if self.platform_handler:
                # Start app
                main_files = self.search_for_main_files()
                for item in main_files:
                    try:
                        # Get app params if exists
                        app_params = self.config_handler.get_app_params()
                        # Start app
                        self.platform_handler.start_app(
                            self.app_path,
                            item,
                            app_params=app_params
                        )
                        next = False
                    except Exception as e:
                        logger.warning(
                            "Attempt to start main file {%s} failed" % item)
                        logger.warning("Problem was %s" % e)
            else:
                logger.warning("Cannot continue because unknown platform,\
                    during of setuptool's installation.")
        else:
            logger.info("Cannot continue with installing of app.")
            next = True

        return next

    def refill_reload_variables_content(self, **kwargs):
        """Take received variables content and set it."""
        self.app_path = kwargs.get("app_path", self.app_path)
        self.config_handler = kwargs.get(
            "config_processing",
            self.config_handler
        )

    def files_changed(self):
        """Check if files/folders changed."""
        changed = False
        previous_list = self.config_handler.get_app_files()
        if previous_list and self.app_path:
            # Get current list
            current_list = get_list_of_files_and_timestamp(
                self.app_path,
                filters=FILES_CHANGED_FILTER + REQUIRED_FILES
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
        elif previous_list == []:
            # Previous list is empty --> we are assuming this is first time
            # running this script so keep rolling.
            changed = False
        else:
            # Default --> no old list
            changed = True
        return changed

    def preprare_dummy_setup(self, **kwargs):
        """Prepare dummy setup for installation."""
        setup_path = None
        try:
            setup_path = self.setup_dummy.create_dummy_setup(
                folder_to_create=kwargs.get("folder_to_create", None),
                main_folder=kwargs.get("main_folder", None))
        except Exception as e:
            logger.error("Cannot prepare dummy setup file. {%s}" % e)

        return setup_path

    def search_for_main_files(self, folder_path=None):
        """TBD"""
        search_folder = self.app_path
        if folder_path:
            search_folder = folder_path
        all_main_files = []
        # Get all .py files
        try:
            founded_files = Path(search_folder).rglob("*.py")
            # Check if config contains directly specified main
            # file.
            specified_main_file = \
                self.config_handler.get_main_file()
            for file in founded_files:
                # Check if file is THE file
                if specified_main_file.lower() == Path(file).name:
                    all_main_files = []
                    all_main_files.append(str(file))
                    # Do I need to check for entry point?
                    break
                else:
                    with open(str(file), "r") as file_read:
                        if re.search(ENTRY_POINT, file_read.read()):
                            all_main_files.append(str(file))
        except Exception as e:
            logger.error("Search for main file failed. {%s}" % e)
        return set(all_main_files)

    def it_is_me(self) -> bool:
        """Try to assume that this app can be installed via setuptools

        Searching for all file required by setuptools to be successfully
        installed.

        Returns:
        In case yes, returns True, othewise False
        """
        valid = False
        if Path(self.app_path).exists():
            root_files = Path(self.app_path).glob("*")
            required = [file for file in root_files if
                        re.search(REQUIRED_FILES_REGEX, str(file.name))]
            if required:
                valid = True

        return valid

    def find_setup_file(self, app_path=None):
        """Try to find setup.py file if exists.

        Returns:
        Path to setup.py file or None
        """
        setup_file_path = None
        search_path = self.app_path
        if app_path:
            search_path = app_path
        if Path(search_path).exists():
            setup_file_path = list(Path(search_path).glob("setup.py"))
            if setup_file_path:
                setup_file_path = str(setup_file_path[0])
        return setup_file_path

    def get_install_args(self) -> list:
        """Get args required for app installation.

        Example:
        returned list of args --> ['-m', 'pip', 'install']
        will be extended to format(for explanation)
        <path_to_pathon> -m pip -install <file>

        Returns:
        List of arguments.
        """
        return SETUP_INSTALLATION_ARGS
