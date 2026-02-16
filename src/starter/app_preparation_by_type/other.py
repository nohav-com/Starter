# -*- coding: utf-8 -*-
"""Other processing, suing install tool, setup."""

import glob
import logging
import re
import traceback
from collections import Counter
from pathlib import Path

from starter.app_preparation_by_type.common import (
    get_list_of_files_and_timestamp,
    get_all_dependencies_setuptools_approach
)
from starter.app_preparation_by_type.dummy_setup import DummySetup
from starter.app_preparation_by_type.type import TypeOfPackage


__all__ = ['OtherProcessing']


SETUP_FILE = 'setup.py'
FILES_CHANGED_FILTER = ["*.py"]
TOML_FILE = '(.*).toml$'
REQUIRED_FILES = [TOML_FILE]
ENTRY_POINT = 'if __name__ == "__main__"'
POETRY_INSTALLATION_ARGS = ["-m", "pip", "install", "-e", "."]

logger = logging.getLogger(__name__)


class OtherProcessing(TypeOfPackage):
    """This class is doing searching, checking app's requirements if
      poetry's style.
    """

    def __init__(self, /, **kwargs):
        self.app_path = kwargs.get("app_path", None)
        self.config_handler = kwargs.get("config_handler", None)
        self.platform_handler = kwargs.get("platform_handler", None)

        self.setup_dummy = DummySetup()

    def install_and_start(
                self,
                start_fresh=False,
                continue_processing=True):
        """Install dependencies, app and start it.

        Args:
        start_fresh = clear the environment and install it again
        continoue_processing = flag signaling 'try to install and start'

        Returns:
        True in case to signal next in the chain should countinue to
        try to install and start.
        """
        should_continue = continue_processing
        # Should we continue
        if continue_processing and self.it_is_me():
            # Check if we are to suppose to install
            if start_fresh and self.platform_handler:
                should_continue = False
                current_list = get_list_of_files_and_timestamp(
                    self.app_path,
                    filters=FILES_CHANGED_FILTER + REQUIRED_FILES
                )
                # Store app file info for next run
                if current_list:
                    self.config_handler.set_app_files(current_list)
                try:
                    # Need to create setup.py --> to use setuptools
                    setup_file = Path(self.app_path).joinpath(
                        SETUP_FILE)
                    if not setup_file.exists():
                        self.setup_dummy.create_dummy_setup(
                            folder_to_create=self.app_path,
                            app_root_folder=self.search_common_root_folder()
                        )
                    # Does the setup.py file exists?
                    if setup_file.exists():
                        # Install extra dependencies
                        dependencies = \
                            get_all_dependencies_setuptools_approach(
                                self.app_path)
                        if dependencies:
                            self.platform_handler.install_dependencies(
                                dependencies
                            )
                        self.platform_handler.install_app(
                            self.app_path,
                            self.get_install_args()
                        )
                        # Remove dummy setup file
                        self.setup_dummy.remove(setup_file)
                    else:
                        # The setup.py file doesnt exist -> raise an error
                        logger.error(
                            "The setup.py file doesn't exist at '%s'.",
                            setup_file)
                        raise RuntimeError
                except Exception as e:
                    # Something went wrong --> clear the app files
                    # Next run will be detected as fresh start
                    self.config_handler.remove_app_files()
                    logger.error("Installation of app failed. %s", e)
                    logger.error(traceback.format_exc())
                    raise
            # Can we continue
            if self.platform_handler:
                # Search for main files
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
                    except Exception:
                        logger.error(
                            "Attempt to start main file %s failed.",
                            item)
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
                    during of other's installation.")
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

    def it_is_me(self) -> bool:
        """Try to assume that this app can be installed via setuptools.

        Searching for all required files.

        Returns:
        In case yes, returns True, othewise False
        """
        valid = False
        if self.app_path and Path(self.app_path).exists():
            root_files = Path(self.app_path).glob("**/*")
            for file in root_files:
                if re.search(TOML_FILE, str(file)):
                    valid = True
        return valid

    def search_for_main_files(self, folder_path=None) -> set:
        """Search for main file along in the path to app's source code.

        Args:
        folder_path = path to folder to process

        Returns:
        Set of 'main' files.
        """
        search_folder = self.app_path
        if folder_path:
            search_folder = folder_path
        all_main_files = []
        try:
            # Check if config contains directly specified main
            # file.
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
                # Check which contains entry point
                for file in founded_files:
                    try:
                        with open(str(file), "r") as file_read:
                            if re.search(ENTRY_POINT, file_read.read()):
                                all_main_files.append(str(file))
                    except Exception as e:
                        logger.error(
                            "Search for main entry point in file '%s'\
                            failed(%s).", file, e)
        except Exception as e:
            logger.error("Search for main file failed. %s", e)

        return set(all_main_files)

    def search_common_root_folder(self, app_path=None) -> str:
        """Get to common root folder of all .py files.

        Info is extracted from 'pyproject.toml' file.
        It helps to install the whole app.

        Args:
        app_path = path to app folder
        """
        root_folder = self.app_path
        if app_path:
            root_folder = app_path
        try:
            if self.app_path:
                glob_search = Path(self.app_path).joinpath("pyproject.toml")
                if glob_search.exists():
                    file = glob.glob(str(glob_search))
                    if file:
                        packages = self.process_pyproject_file(file[-1])
                        if packages:
                            root_folder = self.get_common_root_folder(
                                list(packages))
        except Exception as e:
            logger.error("Search for common root folder failed(%s).", e)
            raise
            
        return root_folder

    def get_common_root_folder(self, packages_paths) -> str | None:
        """Get most common(intersection) root folder from list of paths

        Params:
        packages_paths = list of paths

        Returns:
        The folder path
        """
        common_folder = None
        all_parents = []
        try:
            for package in packages_paths:
                package_parents = list(Path(package).parents)
                if Path(package).joinpath(self.app_path).is_dir():
                    package_parents.append(package)
                for _, value in enumerate(package_parents):
                    if str(value) != '.':
                        all_parents.append(str(value))
            if all_parents:
                counted_parents = Counter(all_parents).most_common()
                if counted_parents:
                    common_folder = " "
                    for counted in counted_parents:
                        if len(counted[0]) > len(common_folder)\
                                and counted[1] == len(packages_paths):
                            common_folder = counted[0]
                    common_folder = str(
                        Path(self.app_path).joinpath(common_folder))
        except Exception as e:
            logger.error("Get root folder failed.(%s)" % e)
            raise

        return common_folder

    def process_pyproject_file(self, file_path) -> set | None:
        """Process pyproject file and search for included packages.

        Params;
        file_path = path to pyproject file

        Returns:
        Set of unique paths or None
        """
        packages = []
        if Path(file_path).exists():
            content = self.load_file_content(file_path)
            if content:
                parts = content.split("packages = ")
                if parts:
                    packages = re.findall(
                        ", from = \"(.*)\"",
                        parts[-1]
                    )

        return set(packages) if packages else None

    def load_file_content(self, file_path) -> str | None:
        """Load file content and return it as str.

        Params:
        file_path = path to file

        Returns:
        File content in str format or None
        """
        content = None
        if file_path and Path(file_path).exists():
            with open(file_path, "r") as file_in:
                content = file_in.read()
        return content

    def get_install_args(self) -> list:
        """Get args required for app installation.

        Example:
        returned list of args --> ['-m', 'pip', 'install']
        will be extended to format(for explanation)
        <path_to_pathon> -m pip -install <file>

        Returns:
        List of arguments.
        """
        return POETRY_INSTALLATION_ARGS
