import enumerate
import logging
import re
import glob
from collections import Counter
from pathlib import Path

from .common import (
    get_list_of_files_and_timestamp,
    get_all_dependencies_setuptools_approach
)
from .dummy_setup import DummySetup
from .type import TypeOfPackage


__all__ = ['OtherProcessing']


DEFAULT_SETUP_CREATE = 'setup.py'
FILES_CHANGED_FILTER = ["*.py"]
REQUIRED_FILES = ['(.*).toml$']
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
                if current_list:
                    self.config_handler.set_app_files(current_list)
                # Need to create setup.py --> to use setuptools
                setup_file = Path(self.app_path).joinpath(DEFAULT_SETUP_CREATE)
                if not setup_file.exists():
                    self.setup_dummy.create_dummy_setup(
                        folder_to_create=self.app_path,
                        main_folder=self.search_for_common_root_folder()
                    )
                # Install dependencies --> outher
                # (dependencies related to app's dependencies)
                # Setup tool approach --> *requirement*
                dependencies = get_all_dependencies_setuptools_approach(
                    self.app_path)
                if dependencies:
                    self.platform_handler.install_dependencies(
                        dependencies
                    )
                try:
                    # Install app, dependenceis installed as well
                    self.platform_handler.install_app(
                        self.app_path,
                        self.get_install_args()
                    )
                    # Remove dummy setup file
                    self.setup_dummy.remove(setup_file)
                except Exception as e:
                    logger.error("Installation of app failed. %s", e)
                    raise e
            # Can we continue
            if self.platform_handler:
                # Search for main files
                main_files = self.search_for_main_files()
                # Exceptions list
                exceptions_list = []
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
                        # next = False
                    except Exception as e:
                        logger.error(
                            "Attempt to start main file %s failed", item)
                        # logger.error("Problem was %s" % e)
                        # raise e
                        exceptions_list.append(e)
                        continue

                # If amount of founded 'main' files is equal to catched
                # exceptions --> raise error
                if len(exceptions_list) == len(main_files):
                    raise RuntimeError(
                        """Could not properly start the app, because no valid
                           'main file' has been discovered(other option).""")
                should_continue = False
            else:
                logger.warning("Cannot continue because unknown platform,\
                    during of other's installation.")
        return should_continue

    def files_changed(self):
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
        elif previous_list == [] and not self.app_path:
            # Previous list is empty --> we are assuming this is first time
            # running this script so keep rolling.
            changed = False
        else:
            # Default --> no old list
            changed = True
        return changed

    # def refill_reload_variables_content(self, **kwargs):
    #     """Take received variables content and set it."""
    #     self.app_path = kwargs.get("app_path", self.app_path)
    #     self.config_handler = kwargs.get(
    #         "config_processing",
    #         self.config_handler
    #     )

    def it_is_me(self):
        """Try to assume that this app can be installed via setuptools.

        Searching for all required files.

        Returns:
        In case yes, returns True, othewise False
        """
        valid = False
        if self.app_path and Path(self.app_path).exists():
            root_files = Path(self.app_path).glob("**/*")
            for file in root_files:
                if re.search(REQUIRED_FILES[0], str(file)):
                    valid = True
        return valid

    def prepare_dummy_setup(self, **kwargs):
        """Prepare dummy setup for installation."""
        setup_path = None
        try:
            setup_path = self.setup_dummy.create_dummy_setup(
                folder_to_create=kwargs.get("folder_to_create", None),
                main_folder=kwargs.get("main_folder", None))
        except Exception as e:
            logger.error("Cannot prepare dummy setup file. %s", e)
        return setup_path

    def search_for_main_files(self, folder_path=None):
        """Search for main file along in the path to app's source code"""
        search_folder = self.app_path
        if folder_path:
            search_folder = folder_path
        all_main_files = []
        try:
            founded_files = Path(search_folder).rglob("*.py")
            # Check if config contains directly specified main
            # file.
            config_main_file = \
                self.config_handler.get_main_file()
            # Check which contains entry point
            for file in founded_files:
                # Check if file is THE file
                if config_main_file \
                        and config_main_file.lower() == Path(file).name:
                    all_main_files = []
                    all_main_files.append(str(file))
                    # Do I need to check for entry point?
                    break
                else:
                    with open(str(file), "r") as file_read:
                        if re.search(ENTRY_POINT, file_read.read()):
                            all_main_files.append(str(file))
        except Exception as e:
            logger.error("Search for main file failed. %s", e)

        return set(all_main_files)

    def search_for_common_root_folder(self, app_path=None):
        """Get to common root folder of all .py files.

        Info is extracted from 'pyproject.toml' fiel.
        It helps to install the whole app."""
        root_folder = self.app_path
        if app_path:
            root_folder = app_path
        if self.app_path:
            glob_search = Path(self.app_path).joinpath("pyproject.toml")
            if glob_search.exists():
                file = glob.glob(str(glob_search))
                if file:
                    packages = self.process_pyproject_file(file[-1])
                    if packages:
                        root_folder = self.get_common_root_folder(
                            list(packages))
        return root_folder

    def get_common_root_folder(self, packages_paths):
        """Get most common(intersection) root folder from list of paths

        Params:
        packages_paths = list of paths

        Returns:
        The folder path
        """
        common_folder = None
        all_parents = []
        for package in packages_paths:
            package_parents = list(Path(package).parents)
            if Path(package).joinpath(self.app_path).is_dir():
                package_parents.append(Path(package))
            # for index in range(len(package_parents)):
            for index in enumerate(package_parents):
                if str(package_parents[index]) != '.':
                    all_parents.append(str(package_parents[index]))
        if all_parents:
            counted_parents = Counter(all_parents).most_common()
            if counted_parents:
                common_folder = " "
                for counted in counted_parents:
                    if len(counted[0]) > len(common_folder)\
                            and counted[1] == len(packages_paths):
                        common_folder = counted[0]
                common_folder = str(Path(self.app_path).joinpath(common_folder))
        return common_folder

    def process_pyproject_file(self, file_path):
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

    def get_install_args(self):
        """Get args required for app installation.

        Example:
        returned list of args --> ['-m', 'pip', 'install']
        will be extended to format(for explanation)
        <path_to_pathon> -m pip -install <file>

        Returns:
        List of arguments.
        """
        return POETRY_INSTALLATION_ARGS
