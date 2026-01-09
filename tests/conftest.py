import pytest
import shutil
from pathlib import Path

from starter.environment_structure import EnvironmentStructure
from starter.config import ConfigHandler
from starter.context import ContextHandler

VENV_FOLDER_NAME = "app_venv"
VENV_CONFIG_FILE = "app_starter_config.json"
APP_DEFAULT_FOLDER = "app"
VENV_CONTEXT_FILE = "context.json"
APP_ENVIRONMENT_FOLDER = "app_environment"


@pytest.fixture(scope="function")
def environment_structure_designated(tmp_path):
    """Environment structure"""
    env_struct = EnvironmentStructure(app_environment_parent=tmp_path)
    # env_struct.prepare_env_structure()

    yield (env_struct, tmp_path)

    # Clean up
    if Path(tmp_path).exists():
        shutil.rmtree(str(tmp_path), ignore_errors=True)
    del env_struct


@pytest.fixture(scope="function")
def config_handler(environment_structure_designated):
    """Config handler."""
    env_struct = environment_structure_designated[0]
    env_struct.prepare_env_structure()
    config_file = env_struct.get_path_config_file()
    handler = ConfigHandler(config_file=config_file)

    yield handler

    del handler


@pytest.fixture(scope="function")
def context_handler(environment_structure_designated):
    """Context handler."""
    env_struct = environment_structure_designated[0]
    env_struct.prepare_env_structure()
    context_file = env_struct.get_path_context_file()

    handler = ContextHandler(context_file=context_file)

    yield handler

    del handler