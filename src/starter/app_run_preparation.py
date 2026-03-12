# -*- coding: utf-8 -*-
"""Main entry point to prepare the app for startup."""

import logging
from pathlib import Path

from starter.app_preparation_by_platform.platform_handler import (
    PlatformHandler
)
from starter.app_preparation_by_type.other import OtherProcessing
from starter.app_preparation_by_type.setup import SetupProcessing
from starter.app_preparation_by_type.wheel import WheelProcessing
from starter.create_venv import CreateVenv
from starter.use_existing_venv import UseExistingVenv

__all__ = ['AppPreparationAndRun']

logger = logging.getLogger(__name__)


class AppPreparationAndRun():
    """Manages everything related to creating a virtual environment,
    loading an existing one, etc."""
    def __init__(self, /, **kwargs):
        # Gets the context handler
        self.context_handler = kwargs.get("context_handler", None)
        # Gets the config handler
        self.config_handler = kwargs.get("config_handler", None)
        # Gets the environment structure
        self.env_structure = kwargs.get("env_structure", None)
        # App folder
        self.app_folder = self.get_app_folder_from_environment()
        # Platform handler
        self.platform_handler = None
        self.set_plaform_handler()
        # Instances of processing classes for the supported types
        self.setup = SetupProcessing(
            app_path=self.app_folder,
            config_handler=self.config_handler,
            platform_handler=self.platform_handler)
        self.wheel = WheelProcessing(
            app_path=self.app_folder,
            config_handler=self.config_handler,
            platform_handler=self.platform_handler,
            env_structure=self.env_structure,
            context_handler=self.context_handler)
        self.other = OtherProcessing(
            app_path=self.app_folder,
            config_handler=self.config_handler,
            platform_handler=self.platform_handler)

    def get_app_folder_from_environment(self) -> str | None:
        """Gets the app folder for the environment structure."""
        if self.env_structure:
            return self.env_structure.get_path_app_folder()

    def get_platform_handler(self):
        """Gets the platform handler instance."""
        return self.platform_handler

    def set_plaform_handler(self):
        """Initializes the platform handler and gets the instance."""
        platform = PlatformHandler(
            context_handler=self.context_handler,
            cwd=Path(__file__),
            venv_folder=Path(self.env_structure.get_path_venv_folder())
        )
        # Gets the specific handler
        if platform:
            self.platform_handler = platform.get_handler()
        else:
            logger.error("Cannot get the platform handler.")
            raise RuntimeError

    def venv_preparation(self):
        """Prepares the venv and its content."""
        if self.env_structure and self.platform_handler\
                and self.context_handler:
            try:
                # Creates the venv from scratch
                if self.env_structure.folder_is_empty(
                        self.env_structure.get_path_venv_folder()):
                    venv = CreateVenv(
                        context_handler=self.context_handler,
                        platform_handler=self.platform_handler)
                    venv.create(str(self.env_structure.get_path_venv_folder()))
                # Loads the existing venv
                if not self.env_structure.folder_is_empty(
                        self.env_structure.get_path_venv_folder()):
                    venv = UseExistingVenv(
                        context_handler=self.context_handler)
                    venv.create()
            except Exception as e:
                logger.error(
                    "Problem with the venv preparation(%s).", e)
                raise

    def ready_and_start(self, start_fresh=False):
        """Check if the venv needs to be updated, set it, and start
        the app.

        Args:
        start_fresh (bool)= the flag for start over
        """
        logger.info("Installing the app and starting it.")
        try:
            should_continue = self.other.install_and_start(
                start_fresh, True)
            should_continue = self.setup.install_and_start(
                start_fresh, should_continue)
            should_continue = self.wheel.install_and_start(
                start_fresh, should_continue)
        except Exception:
            logger.error("Cannot install and start the app.")
            raise

    def app_files_changed(self) -> bool:
        """Check if the files related to the app changed.

        If the app's files have changed, the existing venv needs to
        be updated.

        Returns:
        True if the files have changed otherwise False
        """
        # Its need to be done the "old-school-way", because "setup"
        # can falsely detect changes due to wheel packages
        # (extra files/folders).
        if self.wheel.it_is_me():
            return self.wheel.files_changed()
        elif self.other.it_is_me():
            return self.other.files_changed()
        elif self.setup.it_is_me():
            return self.setup.files_changed()
        else:
            return False
