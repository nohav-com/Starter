# -*- coding: utf-8 -*-
"""Set up a new virtual environment to run the app."""

import logging
import venv

__all__ = ['CreateVenv']

logger = logging.getLogger(__name__)


class CreateVenv(venv.EnvBuilder):
    """Set up a virtual environment and install the necessary packages."""

    def __init__(self, /, **kwargs):
        self.progress = None
        self.verbose = True
        self.context_handler = kwargs.get("context_handler", None)
        self.platform_handler = kwargs.get("platform_handler", None)

        super().__init__()

    def post_setup(self, context):
        """Basic tasks like installing minimal dependencies and saving
        context.

        Args:
        context = the current context object (types.SimpleNamespace)
        """
        # Move some files because of pyinstaller
        if self.platform_handler and self.context_handler:
            try:
                # Store context
                self.context_handler.store_context_to_file(context)
                self.context_handler.load_context()
                alter, exe_name, pyinst_exe_name = \
                    self.platform_handler.context_needs_to_be_altered()
                if alter and exe_name:
                    self.context_handler.alter_context(
                        exe_name, pyinst_exe_name)

                self.platform_handler.pyinstaller_magic()
                # Necessary
                self.platform_handler.install_dependency(
                    name="pip"
                )
                self.platform_handler.install_dependency(
                    name="setuptools"
                )
            except Exception as e:
                logger.error("Failed to create virtual environment (%s).", e)
                raise
