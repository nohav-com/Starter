"""For creating dummy setup.py so we can use setuptools for installation."""
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


class DummySetup():
    """Class for creating dummy setup.py required ny setupttols to install app."""

    def create_dummy_setup(self,
                           folder_to_create=None,
                           name="Application",
                           version="0.0.1",
                           description="Application",
                           main_folder=None):
        """Create dummy setup.py file indedicated folder."""
        if Path(folder_to_create).exists()\
                and Path(main_folder).exists():
            setup_path = Path(folder_to_create).joinpath("setup.py")
            with open(str(setup_path), "w")\
                    as setup_out:
                filled = DUMMY_SETUP_CONTENT % \
                    (name, version, description, main_folder, main_folder)
                setup_out.write(filled)
            return setup_path
        return None

    def remove(self, setup_file=None):
        """Remove file(in our case setup file)."""
        if setup_file:
            setup_file.unlink(True)
