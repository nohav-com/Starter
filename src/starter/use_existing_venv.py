# -*- coding: utf-8 -*-
"""Class that manages an existing virtual environment (venv)."""

import logging
import traceback
import venv

__all__ = ['UseExistingVenv']


logger = logging.getLogger(__name__)


class UseExistingVenv(venv.EnvBuilder):
    """Use an existing virtual environment (venv) to run the app."""
    def __init__(self, **kwargs):
        self.context_handler = kwargs.get("context_handler", None)
        self.context = None
        super().__init__()

    def get_context(self):
        """Returns the context."""
        return self.context

    def ensure_directories(self):
        """Performs the same actions as the parent method,
        but using an existing virtual environment (venv)."""
        if self.context_handler:
            self.context_handler.load_context()
            self.context = self.context_handler.get_context()

    def create(self):
        """Hook for an existing virtual environment (venv)."""
        self.ensure_directories()
        if self.context:
            try:
                self.setup_python(self.context)
                self.setup_scripts(self.context)
                self.post_setup()
            except Exception as e:
                logger.error(
                    "Failed to load the context of the existing virtual \
                     environment(%s).", e)
                logger.error(traceback.format_exc())
                raise

    def post_setup(self):
        """Let do something."""
        logger.info("Successfully loaded the venv context.")
