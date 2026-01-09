import os
from pathlib import Path

import pytest

from starter.app_preparation_by_type.dummy_setup import DummySetup


@pytest.fixture(scope="function")
def dummy_setup_instance():
    """Create instance of dummy setup class."""
    dummy_setup = DummySetup()

    yield dummy_setup

    del dummy_setup


def test_create_dummy_setup_file(dummy_setup_instance, tmp_path):
    """Create dummy setup file."""
    # Create setup.py file
    dummy_setup_path = dummy_setup_instance.create_dummy_setup(
        folder_to_create=tmp_path,
        app_root_folder=tmp_path
    )
    # Check if exists
    assert dummy_setup_path
    assert dummy_setup_path.exists()
    dummy_setup_instance.remove(dummy_setup_path)
    
    
def test_create_dummy_setup_file_fail(
        dummy_setup_instance, tmp_path, monkeypatch):
    """Creation of dummy setup file failed."""
    monkeypatch.setattr(Path, "joinpath", Exception("Exception"))
    with pytest.raises(Exception):
        # Create setup.py file
        _ = dummy_setup_instance.create_dummy_setup(
            folder_to_create=tmp_path,
            app_root_folder=tmp_path
        )


def test_create_dummy_setup_file_remove_fail(
        dummy_setup_instance, tmp_path, monkeypatch):
    """Create dummy setup file, remove of file failed."""
    # Create setup.py file
    dummy_setup_path = dummy_setup_instance.create_dummy_setup(
        folder_to_create=tmp_path,
        app_root_folder=tmp_path
    )
    # Check if exists
    assert dummy_setup_path
    assert dummy_setup_path.exists()
    # Try to remove it
    monkeypatch.setattr(Path, "unlink", Exception("Exception"))
    with pytest.raises(Exception):
        dummy_setup_instance.remove(dummy_setup_path)

    # Clean up
    os.remove(dummy_setup_path)
