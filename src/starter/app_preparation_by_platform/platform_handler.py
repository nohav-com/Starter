# -*- coding: utf-8 -*-
"""Determines which handler needs to be used based on the platform."""

import logging
import platform

from starter.app_preparation_by_platform.linux import LinuxPlatform
from starter.app_preparation_by_platform.windows import WindowsPlatform

__all__ = ['PlatformHandler']

logger = logging.getLogger(__name__)


class PlatformHandler():
    """A basic wrapper around the platform handler."""
    def __init__(self, **kwargs):
        self.handler = None
        self.set_platform_handler(**kwargs)

    def set_platform_handler(self, **kwargs):
        """Set the platform handler."""
        if platform.system().lower() == "windows":
            self.handler = WindowsPlatform(**kwargs)
        elif platform.system().lower() == "linux":
            self.handler = LinuxPlatform(**kwargs)

    def get_handler(self):
        """Gets the platform handler."""
        return self.handler
