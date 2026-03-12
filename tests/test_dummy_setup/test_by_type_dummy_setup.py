# -*- coding: utf-8 -*-
"""Test for dummy setup."""

import os
from pathlib import Path

import pytest

from starter.app_preparation_by_type.dummy_setup import DummySetup


@pytest.fixture(scope="function")
def dummy_setup_instance():
    """Create an instance of the dummy setup class."""
    dummy_setup = DummySetup()

    yield dummy_setup

    del dummy_setup


def test_create_dummy_setup_file(dummy_setup_instance, tmp_path):
    """Create a dummy setup file."""
    # Create a setup.py file
    dummy_setup_path = dummy_setup_instance.create_dummy_setup(
        folder_to_create=tmp_path,
        app_root_folder=tmp_path
    )
    # Check if it exists
    assert dummy_setup_path
    assert dummy_setup_path.exists()
    dummy_setup_instance.remove(dummy_setup_path)


def test_create_dummy_setup_file_failed(
        dummy_setup_instance, tmp_path, monkeypatch):
    """Failed to create the dummy setup file."""
    monkeypatch.setattr(Path, "joinpath", Exception("Exception"))
    with pytest.raises(Exception):
        # Create a setup.py file
        _ = dummy_setup_instance.create_dummy_setup(
            folder_to_create=tmp_path,
            app_root_folder=tmp_path
        )


def test_create_dummy_setup_file_remove_fail(
        dummy_setup_instance, tmp_path, monkeypatch):
    """Create the dummy setup file, but removal of the file failed."""
    # Create a setup.py file
    dummy_setup_path = dummy_setup_instance.create_dummy_setup(
        folder_to_create=tmp_path,
        app_root_folder=tmp_path
    )
    # Check if it exists
    assert dummy_setup_path
    assert dummy_setup_path.exists()
    # Try to remove it
    monkeypatch.setattr(Path, "unlink", Exception("Exception"))
    with pytest.raises(Exception):
        dummy_setup_instance.remove(dummy_setup_path)

    # Clean up
    os.remove(dummy_setup_path)
