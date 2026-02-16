# -*- coding: utf-8 -*-
"""Test of config logic."""

import json
from pathlib import Path


def test_create_config_handler(config_handler):
    """Create confign handler."""
    assert Path(config_handler.get_config_file()).exists()


def test_clean_config_file_from_not_required_items(config_handler):
    """Strip config file from all not required keys+values."""
    config_before = config_handler.get_config()
    config_handler.clean_config_file_from_not_required_items()
    config_after = config_handler.get_config()
    assert config_after != config_before


def test_set_get_config_file(config_handler, tmp_path):
    """Set new config file path, try to get it and validate."""
    config_path = Path(tmp_path).joinpath("new_config.json")
    config_handler.set_config_file(str(config_path))
    assert config_handler.get_config_file() == str(config_path)


def test_set_get_config(config_handler):
    """Set config content, try to get it and validate."""
    value = '{"key1": "value1"}'
    config_content = json.loads(value)
    config_handler.set_config(config_content)
    config = config_handler.get_config()
    assert config
    assert len(config) == 1


def test_get_path_to_cofig_file(config_handler):
    """Get path to config file."""
    assert Path(config_handler.get_path_to_config_file()).exists()


def test_set_get_remove_app_files(config_handler):
    """Set app files, get them -->validate, remove them + validate."""
    value = {"file": "file_timestamp"}
    config_handler.set_app_files(value)
    assert config_handler.get_app_files() == value
    config_handler.remove_app_files()
    assert config_handler.get_app_files() == {}


def test_set_get_app_params(config_handler):
    """Set app params and try to recover the and validate."""
    value = "--test_param test1"
    config_handler.set_app_params(value)
    assert config_handler.get_app_params() == value 


def test_set_get_app_folder(config_handler, tmp_path):
    """Set app folder path and try to recover it and validate."""
    key = "app_folder"
    value = Path(tmp_path).joinpath(key)
    config_handler.set_app_folder(str(value))
    assert config_handler.get_app_folder() == str(value)


def test_set_get_main_file(config_handler, tmp_path):
    """Set main file path and try to recover it and validate."""
    key = "main_file"
    value = Path(tmp_path).joinpath(key)
    config_handler.set_main_file(str(value))
    assert config_handler.get_main_file() == str(value)


def test_get_root_keys_from_config_object(config_handler):
    """Get root keys from config file."""
    keys = config_handler.get_root_keys_from_config_object()
    assert keys
    # Add your own
    key = "test"
    value = "test_value"
    config_handler.set_value_for_key(key, value)
    keys = config_handler.get_root_keys_from_config_object()
    assert key in keys


def test_set_get_value_for_key(config_handler):
    """Set specific value for key and get back and validate."""
    key = "test"
    value = "test_value"
    config_handler.set_value_for_key(key, value)

    get_value = config_handler.get_value_for_key(key)
    assert get_value == value
