"""Prepare fresh, new venv for running the app."""
import logging
import venv

__all__ = ['CreateVenv']

logger = logging.getLogger(__name__)


class CreateVenv(venv.EnvBuilder):
    """Create virtual environment and install what needs to be installed."""

    def __init__(self, *args, **kwargs):
        self.progress = None
        self.verbose = True  # Always full output
        # Get context handler
        self.context_handler = kwargs.get("context_handler", None)
        self.platform_handler = kwargs.get("platform_handler", None)

        super().__init__()

    def post_setup(self, context):
        """Basic operation like install minimal dependencies, store context."""
        # Move some files because of pyinstaller
        if self.platform_handler and self.context_handler:
            # Store context
            self.context_handler.store_context_to_file(context)
            self.context_handler.load_context()

            self.platform_handler.pyinstaller_magic()

            self.platform_handler.install_dependency(
                name="pip"
            )
            self.platform_handler.install_dependency(
                name="setuptools"
            )
