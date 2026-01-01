import glob
import logging
import re
from pathlib import Path
from .common import (
    get_list_of_files_and_timestamp,
    get_all_dependencies_setuptools_approach
)


__all__ = ['WheelProcessing']

FILES_CHANGED_FILTER = ['*.whl']
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
                # Install dependencies --> outher
                # (dependencies related to app's dependencies)
                # Get regex for files search
                # req_files_regex = self.config_handler.get_extra_requirements()
                dependencies = get_all_dependencies_setuptools_approach(
                    self.app_path)
                if dependencies:
                    self.platform_handler.install_dependencies(
                        dependencies
                    )
                try:
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
                    logger.error("Installation of app failed. %s", e)
                    raise e
            # Can we continue
            if self.platform_handler and self.env_structure \
                    and installation_file:
                # Search for main file
                main_files, app_cwd = self.search_for_main_files(
                    self.env_structure.get_path_venv_folder(),
                    installation_file
                )
                if main_files:
                    # Exceptions list
                    exceptions_list = []
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
                                "Attempt to start main file %s failed",
                                item)
                            exceptions_list.append(e)
                            continue
                    if len(exceptions_list) == len(main_files):
                        raise RuntimeError(
                            """Could not properly start the app, because no
                               valid 'main file' has been
                               discovered(other option).""")
                    should_countinue = False
            else:
                logger.warning("Cannot continue because unknown platform,\
                    during of wheel's installation.")

        return should_countinue

    def files_changed(self):
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
        elif previous_list == []:
            # Previous list is empty --> we are assuming this is first time
            # running this script so keep rolling.
            changed = False
        else:
            # Default --> no old list
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
            lib_path = Path(venv_path).joinpath("lib")
            if lib_path and Path(lib_path).exists():
                # Lets get python folder
                python_folder = glob.glob(str(Path(lib_path).joinpath("*")))
                python_side_packages = python_folder and\
                    Path(lib_path).joinpath(python_folder[0], "site-packages")
                if python_side_packages.exists():
                    # Search for app folder
                    packages = glob.glob(
                        str(python_side_packages.joinpath("*")))
                    app_name_parts = app_name.split("-")
                    real_app_name = app_name_parts[0]
                    for part in range(1, len(app_name_parts)):
                        matched = [folder for folder in packages if
                                   Path(folder).name.lower() == real_app_name]
                        if matched:
                            installed_app_folder = matched[0]
                            break
                        real_app_name += "-" + str(part)
                    # Lets search installed app folder
                    if installed_app_folder:
                        founded_files = Path(installed_app_folder).\
                            rglob(PYTHON_FILE_REGEX)
                        # Check if config contains directly specified main
                        # file.
                        config_main_file = \
                            self.config_handler.get_main_file()
                        for file in founded_files:
                            # Check if file is THE file
                            if config_main_file \
                                    and config_main_file.lower() \
                                    == Path(file).name:
                                all_main_files = []
                                all_main_files.append(str(file))
                                # Do I need to check for entry point?
                                break
                            # else:
                            #     with open(str(file), "r") as file_read:
                            #         if re.search(
                            #                 ENTRY_POINT,
                            #                 file_read.read()):
                            #             all_main_files.append(str(file))
                            # else:
                            with open(str(file), "r") as file_read:
                                if re.search(
                                        ENTRY_POINT,
                                        file_read.read()):
                                    all_main_files.append(str(file))

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

    def get_app_file(self):
        """Get app file(wheel file)."""
        file = None
        if self.app_path and Path(self.app_path).exists():
            file = glob.glob(
                str(Path(self.app_path).joinpath(FILES_CHANGED_FILTER[0])))
            if file:
                file = file[0]
        return file
