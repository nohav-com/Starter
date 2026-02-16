# -*- coding: utf-8 -*-
"""Class managing already existing venv."""

import logging
import traceback
import venv

__all__ = ['UseExistingVenv']


logger = logging.getLogger(__name__)


class UseExistingVenv(venv.EnvBuilder):
    """Use already existing venv for running the app."""
    def __init__(self, **kwargs):
        self.context_handler = kwargs.get("context_handler", None)
        self.context = None
        super().__init__()

    def get_context(self):
        """Return context."""
        return self.context

    def ensure_directories(self):
        """Do everything like parent method but for existing venv."""
        if self.context_handler:
            self.context_handler.load_context()
            self.context = self.context_handler.get_context()

    def create(self):
        """Hook to existing venv."""
        self.ensure_directories()
        if self.context:
            try:
                self.setup_python(self.context)
                self.setup_scripts(self.context)
                self.post_setup()
            except Exception as e:
                logger.error("Loading context of existing venv failed(%s).", e)
                logger.error(traceback.format_exc())
                raise

    def post_setup(self):
        """Let do something."""
        logger.info("Successfully loaded env context.")
