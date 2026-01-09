"""Discovers what handler needs to be used based on platform"""
import logging
import platform

from starter.app_preparation_by_platform.linux import LinuxPlatform
from starter.app_preparation_by_platform.windows import WindowsPlatform

__all__ = ['PlatformHandler']

logger = logging.getLogger(__name__)


class PlatformHandler():
    """Basic wrapper around platform handler."""
    def __init__(self, **kwargs):
        self.handler = None
        self.set_platform_handler(**kwargs)

    def set_platform_handler(self, **kwargs):
        """Set platform handler."""
        if platform.system().lower() == "windows":
            self.handler = WindowsPlatform(**kwargs)
        elif platform.system().lower() == "linux":
            self.handler = LinuxPlatform(**kwargs)

    def get_handler(self):
        """Gets platform handler."""
        return self.handler
