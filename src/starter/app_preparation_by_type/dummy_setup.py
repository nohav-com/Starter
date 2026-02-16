# -*- coding: utf-8 -*-
"""For creating dummy setup.py so we can use setuptools for installation."""

import logging
from pathlib import Path

DUMMY_SETUP_CONTENT = """
from setuptools import setup, find_packages

setup(
    name='%s',
    version='%s',
    description='%s',
    packages=find_packages("%s"),
    package_dir={"": "%s"},)
"""

logger = logging.getLogger(__name__)


class DummySetup():
    """
    Class for creating dummy setup.py required ny setupttols to install app.
    """

    def create_dummy_setup(self,
                           folder_to_create=None,
                           name="Application",
                           version="0.0.1",
                           description="Application",
                           app_root_folder=None) -> str | None:
        """Create dummy setup.py file indedicated folder."""
        if Path(folder_to_create).exists()\
                and Path(app_root_folder).exists():
            setup_path = Path(folder_to_create).joinpath("setup.py")
            try:
                with open(str(setup_path), "w")\
                        as setup_out:
                    filled = DUMMY_SETUP_CONTENT % \
                        (name,
                         version,
                         description,
                         app_root_folder,
                         app_root_folder)
                    setup_out.write(filled)
                return setup_path
            except Exception as e:
                logger.error("Cannot create dummy setup.py file(%s).", e)
        return None

    def remove(self, setup_file=None):
        """Remove file(in our case setup file).

        Args:
        setup_file = file to remove
        """
        if setup_file and Path(setup_file).exists():
            # Remove
            setup_file.unlink(True)
