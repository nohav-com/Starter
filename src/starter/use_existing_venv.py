"""Use already existing venv for running the app."""
import logging
import venv
# from pathlib import Path


__all__ = ['UseExistingVenv']


logger = logging.getLogger(__name__)


class UseExistingVenv(venv.EnvBuilder):
    def __init__(self, *args, **kwargs):
        self.context_handler = kwargs.get("context_handler", None)
        self.context = None
        super().__init__()

    def get_context(self):
        """Return context."""
        return self.context

    def ensure_directories(self):
        """Do everything like parent method but for existing venv"""
        if self.context_handler:
            self.context_handler.load_context()
            self.context = self.context_handler.get_context()

    def create(self):
        """Hook to existing venv."""
        self.ensure_directories()
        if self.context:
            self.setup_python(self.context)
            self.setup_scripts(self.context)
            self.post_setup()

    def post_setup(self):
        """Let do something."""
        logger.info("Successfully loaded env context.")
