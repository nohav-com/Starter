"""Create, change, handle environment folder structure."""

import json
import logging
import os
import shutil
from pathlib import Path

from starter.environment_default_content.default_config_content import CONFIG_CONTENT

__all__ = ['EnvironmentStructure']

VENV_FOLDER_NAME = "app_venv"
VENV_CONFIG_FILE = "app_starter_config.json"
APP_DEFAULT_FOLDER = "app"
VENV_CONTEXT_FILE = "context.json"
APP_ENVIRONMENT_FOLDER = "app_environment"

logger = logging.getLogger(__name__)


class EnvironmentStructure():
    def __init__(self, **kwargs):
        """Creates app's environment structure with folders, file.
        
        This structure is used to prepare venv for app to be started.add()
        
        Args:
        app_environment_parent = Root folder where to locate the structure.
                                 Its optional arg.
        """
        self.app_venv_folder = None
        self.context_file = None
        self.config_file = None
        self.app_folder = None
        self.app_environment_folder = None
        # Where the evironment folder will be placed
        self.current_parent = kwargs.get(
            "app_environment_parent", Path(__file__).parents[2])

    def prepare_env_structure(self):
        """Prepare a whole environment structure."""
        try:
            self.prepare_app_environment_folder()
            self.prepare_config_file()
            self.prepare_context_file()
            self.prepare_venv_folder()
            self.prepare_app_folder()
            logger.info(
                "App environment prepared %s.",
                self.get_path_app_environment_folder())
        except Exception as e:
            logger.error(
                "Could not fully prepare app env structure(%s).", e)
            raise

    def clear_environment(self):
        """Removes everything related to app environment."""
        try:
            self.remove_app_environment_folder()
            logger.info("Environment successfully cleared")
        except Exception as e:
            logger.error(
                "Could not clear the app environment(%s).", e)
            raise

    def clear_environment_exclude_app_folder(self):
        """Clear environment, keep the app_folder."""
        try:
            self.remove_context_file()
            self.remove_config_file()
            self.remove_venv_folder()
        except Exception as e:
            logger.error(
                "Problem with clearing enviroment, exclude app_folder(%s).", e)
            raise

    def get_path_app_environment_folder(self) -> str | None:
        """Gets path to root app environment folder."""
        return str(self.app_environment_folder) if self.app_environment_folder\
            else None

    def remove_app_environment_folder(self):
        """Removes app root folder and it content."""
        if self.app_environment_folder \
                and self.app_environment_folder.exists():
            self.remove_item(self.app_environment_folder)
            self.app_environment_folder = None

    def prepare_app_environment_folder(self):
        """Prepare app root folder."""
        self.app_environment_folder = self.current_parent.joinpath(
            APP_ENVIRONMENT_FOLDER)
        if not self.app_environment_folder.exists():
            try:
                self.app_environment_folder.mkdir()
                logger.info(
                    "App root folder %s created.",
                    self.app_environment_folder)
            except Exception as e:
                logger.error(
                    "Creation of app root folder %s failed(%s).",
                    self.app_environment_folder, e)
                raise

    def get_path_venv_folder(self) -> str | None:
        """Returns path to app venv folder."""
        return str(self.app_venv_folder) if self.app_venv_folder else None

    def remove_venv_folder(self):
        """Removes app venv folder and its content."""
        if self.app_venv_folder and self.app_venv_folder.exists():
            logger.info(
                "Removing venv folder %s", str(self.app_venv_folder))
            self.remove_item(self.app_venv_folder)
            self.app_venv_folder = None

    def prepare_venv_folder(self):
        """Prepares folder for venv environment."""
        self.app_venv_folder = self.current_parent.joinpath(
            APP_ENVIRONMENT_FOLDER, VENV_FOLDER_NAME)
        if not self.app_venv_folder.exists():
            try:
                self.app_venv_folder.mkdir()
                logger.info("App venv folder created. %s",
                            self.app_venv_folder)
            except Exception as e:
                # Failed
                self.app_venv_folder = None
                logger.error(
                    "Preparation of venv folder %s failed(%s).",
                    self.app_venv_folder, e)
                raise

    def get_path_config_file(self) -> str | None:
        """Gets path to config file."""
        return str(self.config_file) if self.config_file else None

    def remove_config_file(self):
        """Removes config file."""
        if self.config_file and self.config_file.exists():
            logger.info("Removing config file %s", str(self.config_file))
            self.remove_item(str(self.config_file))
            self.config_file = None

    def prepare_config_file(self):
        """Prepare app starter config file and eventually fill it.

        It should contains info where the the app's file are located,
        what dependencies should be installed, etc.
        """
        self.config_file = self.current_parent.joinpath(
            APP_ENVIRONMENT_FOLDER, VENV_CONFIG_FILE)
        if not self.config_file.exists():
            try:
                with open(str(self.config_file), "w") as config_in:
                    config_in.write(json.dumps(CONFIG_CONTENT, indent=4))
                logger.info("Config file %s created", self.config_file)
            except Exception as e:
                self.config_file = None
                logger.error(
                    "Problem with preparation of config file - \
                    default content(%s).", e)
                raise

    def get_path_app_folder(self) -> str | None:
        """Gets path to app folder."""
        return str(self.app_folder) if self.app_folder else None

    def set_path_app_folder(self, path: str):
        """Set path to app folder.
        
        Args:
        path = Path to set
        """
        if path:
            self.app_folder = Path(path)

    def remove_app_folder(self):
        """Removes app folder and its content."""
        if self.app_folder and self.app_folder.exists():
            self.remove_item(str(self.app_folder))
            self.app_folder = None

    def prepare_app_folder(self):
        """Prepare path do default app folder."""
        self.app_folder = self.current_parent.joinpath(
            APP_ENVIRONMENT_FOLDER, APP_DEFAULT_FOLDER)
        if not self.app_folder.exists():
            try:
                self.app_folder.mkdir()
                logger.info("App folder %s created.",  self.app_folder)
            except Exception as e:
                self.app_folder = None
                logger.error("Preparation of app folder %s failed(%s).",
                             self.app_folder, e)
                raise

    def get_path_context_file(self) -> str | None:
        """Gets path to contenxt file."""
        return str(self.context_file) if self.context_file else None

    def remove_context_file(self):
        """Remove context file."""
        if self.context_file and self.context_file.exists():
            self.remove_item(str(self.context_file))
            self.context_file = None

    def prepare_context_file(self):
        """Prepare file and path for context content.

        Returns:
        The path to file or None
        """
        self.context_file = self.current_parent.joinpath(
            APP_ENVIRONMENT_FOLDER, VENV_CONTEXT_FILE)
        if not self.context_file.exists():
            try:
                with open(str(self.context_file), "w") as context_in:
                    context_in.write(json.dumps({}, indent=4))
                logger.info("Context file %s prepared.", self.context_file)
            except Exception as e:
                self.context_file = None
                logger.error("Creating of context file %s failed(%s).",
                             self.context_file, e)
                raise

    def folder_is_empty(self, folder_path, filter=[]) -> bool:
        """Check if folder contains something.

        Args:
        folder_path = folder to check
        filters = list of files to exclude from founded files/folders

        Returns:
        Returns True if folder is not empty, otherwise false
        """
        empty = True
        if folder_path and Path(folder_path).exists():
            founded = os.listdir(folder_path)
            if filter:
                founded = [file for file in os.listdir(folder_path)
                           if Path(file).name not in filter]
            if founded:
                empty = False

        return empty

    def remove_item(self, item):
        """Removes given item.

        Args:
        item = path to item to be removed(includes file, folders)
        """
        if item and Path(item).exists() and Path(item).is_dir():
            # Remove folder
            try:
                shutil.rmtree(str(item), ignore_errors=True)
                logger.info("Folder %s successfully removed.", item)
            except Exception as e:
                logger.error("Cannot remove item(folder) '%s'(%s).", item, e)
                raise
        elif item and Path(item).exists() and Path(item).is_file():
            # Remove file
            try:
                os.remove(str(item))
                logger.info("File %s successfully removed.", item)
            except Exception as e:
                logger.error("Cannot remove item(file) '%s'(%s).", item, e)
                raise
