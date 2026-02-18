# -*- coding: utf-8 -*-
"""Class is managing everythin releated to context and context file."""

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
        """Return context object."""
        return self.context

    def get_context_file(self) -> str:
        """Get full path to context file."""
        return self.context_file

    def set_context_file(self, context_file=None):
        """Set context file path.

        Args:
        context_file = path to context file
        """
        if context_file is not None:
            self.context_file = context_file
            self.load_context()

    def get_value_for_key(self, key) -> str | None:
        """Get value for specified key from context.

        Args:
        key = key to search for (e.g. app_files)
        """
        value = None
        if key and self.context:
            value = self.context.__getattribute__(key)
        return value

    def set_value_for_key(self, key, value):
        """Set value for specified key.add()

        Args:
        key = key to store value for
        value = value to store
        """
        if key and value:
            self.context.__setattr__(key, value)
            self.store_context_to_file(self.context)
            self.load_context()

    def store_context_to_file(self, context):
        """Store current context to file.

        This context is going to be used when we are only changing venv
        (reinstall app or reinstall dependencies) not creating fresh one.
        Used in class 'use_existing_venv'

        Args:
        context = The context you wan tot store to file
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
                logger.error("Cannot store current context to file. %s", e)

    def get_context_keys(self):
        """Returns a list of keys from config."""
        keys = None
        try:
            keys = [key for key in dir(self.context) if
                    not re.search("__(.*)__", key)]
        except Exception as e:
            logger.warning("Can not get list of keys form context(%s).", e)
        return keys

    def alter_context(self, exe_file: str, pyinstaller_exe_name: str):
        """Alter context's values.

        Args:
        exe_file = new exe file name
        pyinstaller_exe_name = name to look for
        Required by Windows platform.
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
        """Load context from a file."""
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
                    "Could not load stored context from file. %s", e)
                raise
            # Load context to instance's variable
            self.context = context if context else {}
        else:
            logger.warning("Context file is available(cannot be found).")
