# -*- coding: utf-8 -*-
"""This class manages all operations related to the context and its file."""

import json
import logging
import re
import types
from pathlib import Path

__all_ = ['Contexthandler']

logger = logging.getLogger(__name__)


class ContextHandler():
    def __init__(self, /, **kwargs):
        self.context_file = kwargs.get("context_file", None)
        self.context = {}
        self.load_context()

    def get_context(self):
        """Returns the current context object."""
        return self.context

    def get_context_file(self) -> str:
        """Returns the full path of the context file."""
        return self.context_file

    def set_context_file(self, context_file=None):
        """Set the context file path.

        Args:
        context_file = path to the context file
        """
        if context_file is not None:
            self.context_file = context_file
            self.load_context()

    def get_value_for_key(self, key: str) -> str | None:
        """Returns the value associated with the given key in the context.

        Args:
        key (str) = key to look up in the context(e.g. app_files)
        """
        value = None
        if key and self.context:
            value = self.context.__getattribute__(key)
        return value

    def set_value_for_key(self, key, value):
        """Sets the value associated with the given key in the context.

        Args:
        key = the key to store the value for
        value = the value to store
        """
        if key and value:
            self.context.__setattr__(key, value)
            self.store_context_to_file(self.context)
            self.load_context()

    def store_context_to_file(self, context):
        """Saves the current context object to the context file.

        This context is applied when modifying the existing virtual
        environment (such as reinstalling the app or dependencies),
        not when creating a new one. Used in the 'use_existing_venv'
        class.

        Args:
        context = the context object that you wish to store in a file.
        """
        if context:
            context_object = {}
            try:
                keys = [key for key in dir(context) if
                        not re.search("__(.*)__", key)]
                for key in keys:
                    context_object[key] = context.__getattribute__(key)
                if len(context_object) != 0:
                    with open(str(self.context_file), "w") as context_in:
                        context_in.write(json.dumps(context_object, indent=4))
            except Exception as e:
                logger.error(
                    "Failed to store the current context to the file: %s.", e)

    def get_context_keys(self):
        """Returns a list of all keys present in the config file."""
        keys = None
        try:
            keys = [key for key in dir(self.context) if
                    not re.search("__(.*)__", key)]
        except Exception as e:
            logger.warning(
                "Failed to get the list of keys from the context (%s).", e)
        return keys

    def alter_context(self, exe_file: str, pyinstaller_exe_name: str):
        """Modify the values within the context.

        Args:
        exe_file (str)= the name of the new executable file
        pyinstaller_exe_name (str)= the name to look for in the search
        This is required for the Windows platform.
        """
        if exe_file and pyinstaller_exe_name:
            # Get all keys
            keys = self.get_context_keys()
            # print("keys:", keys)
            # Start altering
            for key in keys:
                value = self.get_value_for_key(key)
                # print("value:", value)
                if Path(value).name == pyinstaller_exe_name:
                    # Lets change it
                    new_value = Path(value).parent.joinpath(exe_file)
                    # print("new_value:", str(new_value))
                    self.set_value_for_key(key, str(new_value))

    def load_context(self):
        """Loads the context object from the specified file."""
        context = None
        if self.context_file and Path(self.context_file).exists():
            try:
                with open(self.context_file, "r") as context_in:
                    context_dict = json.loads(context_in.read())
                    if context_dict:
                        context = types.SimpleNamespace()
                        for key, value in context_dict.items():
                            context.__setattr__(key, value)
            except Exception as e:
                logger.error(
                    "Failed to load the stored context from the file: %s.", e)
                raise
            # Load context to instance's variable
            self.context = context if context else {}
        else:
            logger.warning(
                "The context file is unavailable and cannot be found.")
