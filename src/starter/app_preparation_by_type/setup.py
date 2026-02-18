# -*- coding: utf-8 -*-
"""Class for processing the old school style requirements file(s)."""

import logging
import re
import traceback
from pathlib import Path

from starter.app_preparation_by_type.common import (
    get_all_dependencies_setuptools_approach,
    get_list_of_files_and_timestamp
)
from starter.app_preparation_by_type.dummy_setup import DummySetup

__all__ = ['SetupProcessing']

FILES_CHANGED_FILTER = ["*.py"]
REQUIRED_FILES_REQUIREMENT_REGEX = "(.*)requirements(.*)"
SETUP_FILE = 'setup.py'
REQUIRED_FILES = [SETUP_FILE]
ENTRY_POINT = 'if __name__ == "__main__"'
SETUP_INSTALLATION_ARGS = ["-m", "pip", "install", "-e", "."]


logger = logging.getLogger(__name__)


class SetupProcessing():
    """This class doing searching, checking the app's requirements the old
       school way. Searching for file(s) '*requirements*,*'."""

    def __init__(self, /, **kwargs):
        self.app_path = kwargs.get("app_path", None)
        self.config_handler = kwargs.get("config_handler", None)
        self.platform_handler = kwargs.get("platform_handler", None)

        self.setup_dummy = DummySetup()

    def install_and_start(self,
                          start_fresh=False,
                          continue_processing=True
                          ) -> bool:
        """Install dependencies, app and start it.

        Args:
        start_fresh = clear the environment and install it again
        continue_processing = flag signaling 'try to install and start'

        Returns:
        True in case to signal next in the chain should countinue to
        try to install and start.
        """
        should_continue = continue_processing
        if continue_processing and self.it_is_me():
            # Check if we are to suppose to install
            if start_fresh and self.platform_handler:
                should_continue = False
                current_list = get_list_of_files_and_timestamp(
                    self.app_path,
                    filters=FILES_CHANGED_FILTER + REQUIRED_FILES
                )
                if current_list:
                    self.config_handler.set_app_files(current_list)
                try:
                    # Setup tool approach --> *requirement*
                    dependencies = get_all_dependencies_setuptools_approach(
                        self.app_path)
                    if dependencies:
                        self.platform_handler.install_dependencies(
                            dependencies
                        )
                    # Install app
                    self.platform_handler.install_app(
                        self.app_path,
                        self.get_install_args()
                    )
                except Exception as e:
                    self.config_handler.remove_app_files()
                    logger.error("Installation of app failed. %s", e)
                    logger.error(traceback.format_exc())
                    raise
            if self.platform_handler:
                # Start app
                main_files = self.search_for_main_files()
                exception_counter = 0
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
                    except Exception as e:
                        logger.error(
                            "Attempt to start main file %s failed(%s).",
                            item, e)
                        # Do we need just count of exceptions
                        # themselves
                        exception_counter += 1
                        continue
                # If amount of founded 'main' files is equal to catched
                # exceptions --> raise error
                if exception_counter == len(main_files):
                    raise RuntimeError(
                        """Could not properly start the app, because no valid
                           'main file' has been discovered.""")
                should_continue = False
            else:
                logger.warning("Cannot continue because unknown platform,\
                    during of setuptool's installation.")

        return should_continue

    def files_changed(self) -> bool:
        """Check if files/folders changed."""
        changed = False
        previous_list = self.config_handler.get_app_files()
        if previous_list and self.app_path:
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
        elif not previous_list and self.app_path:
            changed = True
        return changed

    def search_for_main_files(self, folder_path=None) -> set:
        """Search for main files.

        Args:
        folder_path = where to search

        Returns:
        Set of main files
        """
        search_folder = self.app_path
        if folder_path:
            search_folder = folder_path
        all_main_files = []
        try:
            config_main_file = \
                self.config_handler.get_main_file()
            if config_main_file:
                # Lets find the file
                founded_files = Path(search_folder).\
                    rglob(config_main_file)
                for file in founded_files:
                    all_main_files.append(str(file))
            else:
                founded_files = Path(search_folder).rglob("*.py")
                for file in sorted(founded_files):
                    try:
                        with open(
                                str(file), "r", encoding='utf-') as file_read:
                            if re.search(ENTRY_POINT, file_read.read()):
                                all_main_files.append(str(file))
                    except Exception as e:
                        logger.error(
                            "Search for main entry point in file '%s'\
                            failed(%s).", file, e)

        except Exception as e:
            logger.error("Search for main file failed. %s", e)
        return set(all_main_files)

    def it_is_me(self) -> bool:
        """Try to assume that this app can be installed via setuptools.

        Searching for all file required by setuptools to be successfully
        installed.

        Returns:
        In case yes, returns True, othewise False
        """
        valid = False
        if Path(self.app_path).exists():
            root_files = Path(self.app_path).glob("*")
            required = [file for file in root_files if
                        re.search(SETUP_FILE, str(file.name))]
            if required:
                valid = True

        return valid

    def find_setup_file(self, app_path=None) -> str | None:
        """Try to find setup.py file if exists.

        Args:
        app_path = where to serch for setup.py file

        Returns:
        Path to setup.py file or None
        """
        setup_file_path = None
        search_path = self.app_path
        if app_path:
            search_path = app_path
        if Path(search_path).exists():
            setup_file_path = list(Path(search_path).glob(SETUP_FILE))
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
