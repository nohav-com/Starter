# -*- coding: utf-8 -*-
"""Create, modify, and manage the environment folder structure."""

import copy
import json
import logging
import os
import shutil
from pathlib import Path

from starter.environment_default_content.default_config_content import (
    CONFIG_CONTENT
)

__all__ = ['EnvironmentStructure']

VENV_FOLDER_NAME = "app_venv"
VENV_CONFIG_FILE = "app_starter_config.json"
APP_DEFAULT_FOLDER = "app"
VENV_CONTEXT_FILE = "context.json"
APP_ENVIRONMENT_FOLDER = "app_environment"
MAIN_FILE = "main_file"

logger = logging.getLogger(__name__)


class EnvironmentStructure():
    def __init__(self, **kwargs):
        """Creates the app's environment structure, including folders
        and files.

        This structure is used to prepare the virtual environment (venv)
        for the app to start.

        Args:
        app_environment_parent = Optional root folder for the 
                                 environment structure.
        """
        self.app_venv_folder = None
        self.context_file = None
        self.config_file = None
        self.main_file = kwargs.get("main_file", None)
        self.app_folder = None
        self.app_environment_folder = None
        # Where the evironment folder will be placed
        self.current_parent = kwargs.get(
            "app_environment_parent", Path(__file__).parents[2])

    def prepare_env_structure(self):
        """Set up the full environment structure."""
        try:
            self.prepare_app_environment_folder()
            self.prepare_config_file()
            self.file_main_file_to_config_file()
            self.prepare_context_file()
            self.prepare_venv_folder()
            self.prepare_app_folder()
            logger.info(
                "App environment prepared %s.",
                self.get_path_app_environment_folder())
        except Exception as e:
            logger.error(
                "Failed to fully prepare the app environment(%s).", e)
            raise

    def clear_environment(self):
        """Clear the app environment."""
        try:
            self.remove_app_environment_folder()
            logger.info("App environment cleared.")
        except Exception as e:
            logger.error(
                "Failed to clear the app environment.(%s).", e)
            raise

    def clear_environment_exclude_app_folder(self):
        """Clear environment while preserving the app folder."""
        try:
            self.remove_context_file()
            self.remove_config_file()
            self.remove_venv_folder()
        except Exception as e:
            logger.error(
                "Failed to clear environment (app folder excluded)(%s).", e)
            raise

    def get_path_app_environment_folder(self) -> str | None:
        """Return the root app environment folder path."""
        return str(self.app_environment_folder) if self.app_environment_folder\
            else None

    def remove_app_environment_folder(self):
        """Delete the app root folder and its contents."""
        if self.app_environment_folder \
                and self.app_environment_folder.exists():
            self.remove_item(self.app_environment_folder)
            self.app_environment_folder = None

    def prepare_app_environment_folder(self):
        """Set up the app root folder."""
        self.app_environment_folder = self.current_parent.joinpath(
            APP_ENVIRONMENT_FOLDER)
        if not self.app_environment_folder.exists():
            try:
                self.app_environment_folder.mkdir()
                logger.info(
                    "Created app root folder %s.",
                    self.app_environment_folder)
            except Exception as e:
                logger.error(
                    "Failed to create app root folder %s (%s).",
                    self.app_environment_folder, e)
                raise

    def get_path_venv_folder(self) -> str | None:
        """Get the app venv folder path."""
        return str(self.app_venv_folder) if self.app_venv_folder else None

    def remove_venv_folder(self):
        """Delete the app venv folder and its contents."""
        if self.app_venv_folder and self.app_venv_folder.exists():
            logger.info(
                "Deleting venv folder %s.", str(self.app_venv_folder))
            self.remove_item(self.app_venv_folder)
            self.app_venv_folder = None

    def prepare_venv_folder(self):
        """Set up folder for the venv."""
        self.app_venv_folder = self.current_parent.joinpath(
            APP_ENVIRONMENT_FOLDER, VENV_FOLDER_NAME)
        if not self.app_venv_folder.exists():
            try:
                self.app_venv_folder.mkdir()
                logger.info("Created app venv folder: %s.",
                            self.app_venv_folder)
            except Exception as e:
                # Failed
                self.app_venv_folder = None
                logger.error(
                    "Failed to prepare venv folder %s (%s).",
                    self.app_venv_folder, e)
                raise

    def get_path_config_file(self) -> str | None:
        """Return the config file path."""
        return str(self.config_file) if self.config_file else None

    def remove_config_file(self):
        """Delete the config file."""
        if self.config_file and self.config_file.exists():
            logger.info("Removing config file %s", str(self.config_file))
            self.remove_item(str(self.config_file))
            self.config_file = None

    def prepare_config_file(self):
        """Set up the app starter config file and optionally fill it.

        Includes info on app file locations, required dependencies, etc.
        """
        self.config_file = self.current_parent.joinpath(
            APP_ENVIRONMENT_FOLDER, VENV_CONFIG_FILE)
        if not self.config_file.exists():
            try:
                config_content = copy.deepcopy(CONFIG_CONTENT)
                with open(
                        str(self.config_file), "w", encoding='utf-8') as f_in:
                    f_in.write(json.dumps(config_content, indent=4))
                logger.info("Created config file %s.", self.config_file)
            except Exception as e:
                self.config_file = None
                logger.error(
                    "Failed to prepare config file – default content (%s).",
                    e)
                raise

    def file_main_file_to_config_file(self):
        """Set 'main_file' in the config file.

        Verify main_file and set it in the config file.
        """
        if self.main_file and Path(self.config_file).exists():
            try:
                config_content = {}
                # Lets try to read the content
                with open(
                        str(self.config_file), "r", encoding='utf-8') as f_out:
                    config_content = json.loads(f_out.read())
                if MAIN_FILE in config_content:
                    # Lets try to set it
                    with open(
                            str(self.config_file),
                            "w",
                            encoding='utf-8') as f_in:
                        config_content[MAIN_FILE] = self.main_file
                        f_in.write(json.dumps(config_content, indent=4))
                    logger.info(
                        "Successfully added main_file = '%s'.",
                        self.main_file)
                else:
                    logger.info(
                        "Key '%s' not found in config file.", MAIN_FILE)
            except Exception as e:
                logger.warning(
                    "Failed to add 'main_file' to config file (%s).", e)

    def get_path_app_folder(self) -> str | None:
        """Return the app folder path."""
        return str(self.app_folder) if self.app_folder else None

    def set_path_app_folder(self, path: str):
        """Define the app folder path.

        Args:
        path (str) = app folder path
        """
        if path:
            self.app_folder = Path(path)

    def remove_app_folder(self):
        """Delete the app folder and its contents."""
        if self.app_folder and self.app_folder.exists():
            self.remove_item(str(self.app_folder))
            self.app_folder = None

    def prepare_app_folder(self):
        """Set up the default app folder path."""
        self.app_folder = self.current_parent.joinpath(
            APP_ENVIRONMENT_FOLDER, APP_DEFAULT_FOLDER)
        if not self.app_folder.exists():
            try:
                self.app_folder.mkdir()
                logger.info("Created app folder %s.",  self.app_folder)
            except Exception as e:
                self.app_folder = None
                logger.error("Failed to prepare app folder %s (%s).",
                             self.app_folder, e)
                raise

    def get_path_context_file(self) -> str | None:
        """Return the context file path."""
        return str(self.context_file) if self.context_file else None

    def remove_context_file(self):
        """Delete the context file."""
        if self.context_file and self.context_file.exists():
            self.remove_item(str(self.context_file))
            self.context_file = None

    def prepare_context_file(self):
        """Set up file and path for context content."""
        self.context_file = self.current_parent.joinpath(
            APP_ENVIRONMENT_FOLDER, VENV_CONTEXT_FILE)
        if not self.context_file.exists():
            try:
                with open(
                        str(self.context_file), "w", encoding='utf-8') as f_in:
                    f_in.write(json.dumps({}, indent=4))
                logger.info("Prepared context file %s.", self.context_file)
            except Exception as e:
                self.context_file = None
                logger.error("Failed to create context file %s (%s).",
                             self.context_file, e)
                raise

    def folder_is_empty(self, folder_path: str, filters=[]) -> bool:
        """Verify if the folder is not empty.

        Args:
        folder_path (str)= folder to check
        filters = Files to exclude from search results.

        Returns:
        Returns True if the folder contains any files or subfolders,
        else False.
        """
        empty = True
        if folder_path and Path(folder_path).exists():
            founded = list(Path(folder_path).glob("*"))
            if filters:
                founded = [file for file in os.listdir(folder_path)
                           if Path(file).name not in filters]
            if founded:
                empty = False
        return empty

    def remove_item(self, item: str):
        """Deletes the given item.

        Args:
        item (str)= path of the file or folder to remove.
        """
        if item and Path(item).exists() and Path(item).is_dir():
            # Remove folder
            try:
                shutil.rmtree(str(item), ignore_errors=True)
                logger.info(
                    "The folder %s has been successfully removed.", item)
            except Exception as e:
                logger.error(
                    "Failed to remove the folder %s (%s).", item, e)
                raise
        elif item and Path(item).exists() and Path(item).is_file():
            # Remove file
            try:
                os.remove(str(item))
                logger.info(
                    "The file %s has been successfully removed.", item)
            except Exception as e:
                logger.error("Failed to remove the file %s (%s).", item, e)
                raise
