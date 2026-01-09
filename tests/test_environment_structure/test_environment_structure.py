import shutil
from pathlib import Path

import pytest

VENV_FOLDER_NAME = "app_venv"
VENV_CONFIG_FILE = "app_starter_config.json"
APP_DEFAULT_FOLDER = "app"
VENV_CONTEXT_FILE = "context.json"
APP_ENVIRONMENT_FOLDER = "app_environment"


def test_prepare_structure_step_by_step(environment_structure_designated):
    """Preparte struct step-by-step.

    Run preparation of each part separately.
    """
    env_struct = environment_structure_designated[0]
    # App environment folder
    env_struct.prepare_app_environment_folder()
    assert Path(env_struct.get_path_app_environment_folder()).exists()
    # App folder
    env_struct.prepare_app_folder()
    assert Path(env_struct.get_path_app_folder()).exists()
    # Config file
    env_struct.prepare_config_file()
    assert Path(env_struct.get_path_config_file()).exists()
    # Context file
    env_struct.prepare_context_file()
    assert Path(env_struct.get_path_context_file()).exists()
    # Venv folder
    env_struct.prepare_venv_folder()
    assert Path(env_struct.get_path_venv_folder()).exists()


def test_venv_folder_prepare_get_remove_struct_not_prepared(
        environment_structure_designated):
    """Venv folder - prepared environment structure

    1. Get path to venv folder
    2. Remove venv folder
    3. Get path to venv folder
    """
    env_struct = environment_structure_designated[0]
    # Prepare
    with pytest.raises(Exception):
        env_struct.prepare_venv_folder()
    # Get venv
    assert not env_struct.get_path_venv_folder()
    # Remove
    env_struct.remove_venv_folder()
    # Get venv
    assert not env_struct.get_path_venv_folder()


def test_venv_folder_get_remove_struct_prepared(
        environment_structure_designated):
    """Venv folder - prepared environment structure.

    1. Get path to venv folder
    2. Remove venv folder
    3. Get path to venv folder
    """
    env_struct = environment_structure_designated[0]
    # Prep structure
    env_struct.prepare_env_structure()
    # Get venv
    assert Path(env_struct.get_path_venv_folder()).exists()
    # Remove
    env_struct.remove_venv_folder()
    # Get venv
    assert not env_struct.get_path_venv_folder()


def test_context_file_get_remove_struct_not_prepared(
         environment_structure_designated):
    """Context file - not preparing environment structure.

    1. Get path to context file
    2. Remmove context file
    3. Get path to context file
    """
    env_struct = environment_structure_designated[0]
    # Get context file
    assert not env_struct.get_path_context_file()
    # Remove context file
    env_struct.remove_context_file()
    # Get context file
    assert not env_struct.get_path_context_file()


def test_context_file_get_remove_struct_prepared(
        environment_structure_designated):
    """Context file - prepare environment structure.

    1. Get path to context file
    2. Remmove context file
    3. Get path to context file
    """
    env_struct = environment_structure_designated[0]
    # Prep structure
    env_struct.prepare_env_structure()
    # Get context file
    assert Path(env_struct.get_path_context_file()).exists()
    # Remove context file
    env_struct.remove_context_file()
    # Get context file
    assert not env_struct.get_path_context_file()


def test_config_file_prepare_get_remove_struct_not_prepared(
        environment_structure_designated):
    """Config file - not preparing environment structure.

    1. Get path to config
    2. Remove config file
    3. Get path to config
    """
    env_struct = environment_structure_designated[0]
    # Prepare
    with pytest.raises(Exception):
        env_struct.prepare_config_file()
    # Get config path
    assert not env_struct.get_path_config_file()
    # Remove config file
    env_struct.remove_config_file()
    # Get config path
    assert not env_struct.get_path_config_file()


def test_config_file_get_remove_struct_prepared(
        environment_structure_designated):
    """Config file - prepare environment structure.

    1. Get path to config
    2. Remove config file
    3. Get path to config
    """
    root_location = environment_structure_designated[1]
    env_struct = environment_structure_designated[0]
    # Prep structure
    env_struct.prepare_env_structure()
    # Get config path
    assert str(
        Path(root_location).joinpath(
            APP_ENVIRONMENT_FOLDER, VENV_CONFIG_FILE)) == \
        env_struct.get_path_config_file()
    # Remove config
    env_struct.remove_config_file()
    # Get config again
    assert not env_struct.get_path_config_file()
    assert not Path(root_location).joinpath(
            APP_ENVIRONMENT_FOLDER, VENV_CONFIG_FILE).exists()


def test_init_no_prepare_all_get(environment_structure_designated):
    """Init env structure instance, no prepare, check items"""
    root_location = environment_structure_designated[1]
    env_struct = environment_structure_designated[0]
    # Path to app_environment
    env_folder_path = Path(root_location).joinpath(APP_ENVIRONMENT_FOLDER)
    assert not env_struct.get_path_app_environment_folder()
    # Context file - not exists
    assert not Path(env_folder_path).joinpath(VENV_CONTEXT_FILE).exists()
    # Config file - not exists
    assert not Path(env_folder_path).joinpath(VENV_CONFIG_FILE).exists()
    # Venv folder - not exists
    assert not Path(env_folder_path).joinpath(VENV_FOLDER_NAME).exists()
    # App folder - exists
    assert not Path(env_folder_path).joinpath(APP_DEFAULT_FOLDER).exists()


def test_create_valid_structure(environment_structure_designated):
    """Env structure is at designated location."""
    root_location = environment_structure_designated[1]
    env_struct = environment_structure_designated[0]
    # Prep structure
    env_struct.prepare_env_structure()
    # Path to root "app_environment"
    assert str(Path(root_location).joinpath(APP_ENVIRONMENT_FOLDER)) == \
        str(env_struct.get_path_app_environment_folder())


def test_create_valid_structure_fail(
        environment_structure_designated, monkeypatch):
    """Creation of valid env structure failed, because of exception."""
    # root_location = environment_structure_designated[1]
    env_struct = environment_structure_designated[0]
    monkeypatch.setattr(Path, "mkdir", Exception)
    with pytest.raises(Exception):
        # Prep structure
        env_struct.prepare_env_structure()


def test_clear_environment_exclude_app_folder(
        environment_structure_designated):
    root_location = environment_structure_designated[1]
    env_struct = environment_structure_designated[0]
    # Prep structure
    env_struct.prepare_env_structure()
    env_struct.clear_environment_exclude_app_folder()
    # Path to app_environment
    env_folder_path = Path(root_location).joinpath(APP_ENVIRONMENT_FOLDER)
    # Context file - not exists
    assert not Path(env_folder_path).joinpath(VENV_CONTEXT_FILE).exists()
    # Config file - not exists
    assert not Path(env_folder_path).joinpath(VENV_CONFIG_FILE).exists()
    # Venv folder - not exists
    assert not Path(env_folder_path).joinpath(VENV_FOLDER_NAME).exists()
    # App folder - exists
    assert Path(env_folder_path).joinpath(APP_DEFAULT_FOLDER).exists()


def test_clear_environment(environment_structure_designated):
    """Clear the whole environment."""
    root_location = environment_structure_designated[1]
    env_struct = environment_structure_designated[0]
    # Prep structure
    env_struct.prepare_env_structure()
    # Clear it
    env_struct.clear_environment()
    assert not Path(root_location).joinpath(APP_ENVIRONMENT_FOLDER).exists()


def test_remove_item_folder(environment_structure_designated):
    """Remove item - folder."""
    # root_location = environment_structure_designated[1]
    env_struct = environment_structure_designated[0]
    # Prep structure
    env_struct.prepare_env_structure()
    # Remove
    venv_folder = env_struct.get_path_venv_folder()
    env_struct.remove_item(venv_folder)
    # not existing
    assert not Path(venv_folder).exists()


def test_remove_item_fail(
        environment_structure_designated, tmp_path):
    """TNBD"""
    # monkeypatch.setitem(EnvironmentStructure, "remove_item", Exception)
    root_location = environment_structure_designated[1]
    env_struct = environment_structure_designated[0]
    env_struct.prepare_env_structure()
    # monkeypatch.setitem(EnvironmentStructure, "remove_item", Exception)
    shutil.rmtree(root_location, ignore_errors=True)
    env_struct.remove_item(tmp_path)


def test_folder_is_empty(environment_structure_designated):
    """Folder is empty."""
    root_location = environment_structure_designated[1]
    env_struct = environment_structure_designated[0]

    assert env_struct.folder_is_empty(root_location)


def test_folder_is_not_empty(environment_structure_designated):
    """Folder is not empty."""
    root_location = environment_structure_designated[1]
    env_struct = environment_structure_designated[0]

    # Prepare struct
    env_struct.prepare_env_structure()
    assert not env_struct.folder_is_empty(root_location)
