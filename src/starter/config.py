# -*- coding: utf-8 -*-
"""Class is managing everything related to config file."""

import json
import logging
from pathlib import Path

__all__ = ['ConfigHandler']


logger = logging.getLogger(__name__)

# Keys for config file
CONFIG_APP_FILES = "app_files"
CONFIG_APP_PARAMS = "app_params"
CONFIG_SPECIFIED_MAIN_FILE = "main_file"
CONFIG_APP_FOLDER = "app_folder"

# List of keys to keep from config
KEEP_KEYS = ["app_folder", "main_file"]


class ConfigHandler():
    """Config handler."""
    def __init__(self, /, **kwargs):
        self.config_file = kwargs.get("config_file", None)
        self.config = None
        self.load_config()

    def clean_config_file_from_not_required_items(self):
        """Remove all required items related to app, except app_folder."""
        if self.config:
            new_config_content = {}
            for key, value in self.config.items():
                if key in KEEP_KEYS and key in new_config_content:
                    new_config_content[key] = value
            self.set_config(new_config_content)
            self.save_config()
            self.load_config()

    def set_config_file(self, config_file):
        """Set config file path.

        Args:
        config_file = path to config file
        """
        if config_file:
            self.config_file = config_file
            self.load_config()

    def get_config_file(self) -> str | None:
        """Get path to config file"""
        return self.config_file

    def set_config(self, config=None):
        """Set config to new value.

        Args:
        config = new config content(json object)
        """
        if config is not None:
            self.config = config

    def get_config(self):
        """Get config object."""
        return self.config

    def get_path_to_config_file(self):
        """Returns path to config file, otherwise None."""
        return self.config_file

    def get_app_files(self):
        """Get list of files + timestamps from config file."""
        key = CONFIG_APP_FILES
        values = None
        if key:
            values = self.get_value_for_key(key)
        return values

    def set_app_files(self, value: dict):
        """Set app files to config.

        Args:
        values = value for 'app_files' key
        """
        key = CONFIG_APP_FILES
        if key and value is not None:
            self.set_value_for_key(key, value)

    def remove_app_files(self):
        """Remove app files from config."""
        key = CONFIG_APP_FILES
        if key:
            self.set_value_for_key(key, {})

    def get_app_params(self) -> str | None:
        """Get app's parameters."""
        key = CONFIG_APP_PARAMS
        value = None
        if key:
            value = self.get_value_for_key(key)
        return value

    def set_app_params(self, value):
        """Set app's parameters.

        Args:
        value = value for 'app_params' key
        """
        key = CONFIG_APP_PARAMS
        if key and value is not None:
            self.set_value_for_key(key, value)

    def get_app_folder(self) -> str | None:
        """Get app folder path."""
        key = CONFIG_APP_FOLDER
        value = None
        if key:
            value = self.get_value_for_key(key)
        return value

    def set_app_folder(self, path: str):
        """Set app's folder.

        Args:
        path = value for 'app_folder' key
        """
        key = CONFIG_APP_FOLDER
        if key and path is not None:
            self.set_value_for_key(key, path)

    def get_main_file(self) -> str | None:
        """Get app's main file."""
        key = CONFIG_SPECIFIED_MAIN_FILE
        value = None
        if key:
            value = self.get_value_for_key(key)
        return value

    def set_main_file(self, path):
        """Set app's main file.

        Args:
        path = value for 'main_file' key
        """
        key = CONFIG_SPECIFIED_MAIN_FILE
        if key and path is not None:
            self.set_value_for_key(key, path)

    def get_root_keys_from_config_object(self) -> list | None:
        """Get all root config keys.

        Returns:
        List of keys or None.
        """
        if self.config is not None:
            list_of_keys = self.config.keys()
            return list(list_of_keys)
        return None

    def load_config(self):
        """Load config to variable."""
        try:
            if self.config_file and Path(self.config_file).exists():
                with open(self.config_file, "r") as config:
                    self.config = json.loads(config.read())
        except Exception as e:
            logger.error(
                "Config file has not a valid content, json format(%s).", e)

    def save_config(self):
        """Save config to file."""
        try:
            if self.config_file and not Path(self.config_file).exists():
                with open(self.config_file, "w") as config_in:
                    config_in.write(json.dumps({}, indent=4))
            elif self.config is not None \
                    and Path(self.config_file).exists():
                with open(self.config_file, "w") as config_out:
                    json_out = json.dumps(self.config, indent=4)
                    config_out.write(json_out)

        except Exception as e:
            logger.error("Saving config content to file failed(%s).", e)

    def get_value_for_key(self, key) -> str | None:
        """Get value for specified key from config.

        If key doesnt exists returns None.

        Args:
        key = key to search for
        """
        value = None
        if self.config is not None and key and key in self.config:
            # Expecting one level json
            value = self.config.get(key, None)

        return value

    def set_value_for_key(self, key, value):
        """Set value for specified key in config.

        If key doesn't exist, create it.

        Args:
        key = key to search for
        value = value to store
        """
        if self.config is not None and key and value is not None:
            self.config[key] = value
            self.save_config()
            self.load_config()
