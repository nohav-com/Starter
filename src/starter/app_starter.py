# -*- coding: utf-8 -*-
"""Main crossroad to start 'app starter'.

Processing args, init all required instance, etc.
"""

import argparse
import logging
import sys

from starter.app_run_preparation import AppPreparationAndRun
from starter.common import escape_string
from starter.config import ConfigHandler
from starter.context import ContextHandler
from starter.environment_structure import EnvironmentStructure
from starter.logging_settings import set_logging_settings

logger = logging.getLogger(__name__)


def main_starter(app_path=None, clear_environment=False):
    try:
        # Set logging settings
        set_logging_settings()

        logger.info("Startting app starter")
        env_structure = EnvironmentStructure()
        env_structure.prepare_env_structure()

        # Argument clear_environment passed - clear the house
        # Everything is removed(app_folder included as well)
        if clear_environment:
            env_structure.clear_environment()
            # Create env structure - from scratch
            env_structure.prepare_env_structure()

        # Context handler
        context_handler = ContextHandler(
            context_file=env_structure.get_path_context_file()
        )
        # Config handler
        config_handler = ConfigHandler(
            config_file=env_structure.get_path_config_file()
        )
        # Check if patht to app folder is set)
        if app_path:
            valid_path = escape_string(app_path)
            # Set app folder
            env_structure.set_path_app_folder(valid_path)
            config_handler.set_value_for_key("app_folder", valid_path)
        else:
            # Get app path from config
            config_app_path = config_handler.get_app_folder()
            config_app_path = escape_string(config_app_path)
            if config_app_path:
                env_structure.set_path_app_folder(config_app_path)

        # App run prepraration instance
        app_preparation_and_run = AppPreparationAndRun(
            context_handler=context_handler,
            config_handler=config_handler,
            env_structure=env_structure)

        start_fresh = app_preparation_and_run.app_files_changed()

        if start_fresh:
            logger.info("Fresh start - removing venv")
            env_structure.remove_venv_folder()
            env_structure.prepare_venv_folder()

        # Time to prepare and start the app, if its possible
        app_preparation_and_run.venv_preparation()
        app_preparation_and_run.ready_and_start(start_fresh)
    except Exception:
        logger.error("Problem with preparing venv for app.")
        # Clearing the whole app_environment(folder)
        # logger.info("Removing almost everything(app folder excluded).")
        # env_structure.clear_environment_exclude_app_folder()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog="App start",
        description="Preparing enviroment for app.")

    parser.add_argument('--app_path',
                        dest='app_path',
                        help='Specifying where is app code stored,\
                              to be used.',
                        default="")

    parser.add_argument('--clear_environment',
                        dest='clear_environment',
                        action='store_true',
                        help='Flag to signal, clear environment\
                              (completely everything).',
                        default=False)

    options = parser.parse_args()

    app_folder = None

    try:
        app_folder = options.app_path
        clear = options.clear_environment
    except Exception as e:
        # Something weng wrong, show me the error
        print("Error: %s", e)

    # Default rc code
    rc = 1
    try:
        main_starter(app_folder,
                     clear)
        rc = 0
    except Exception as e:
        print("Error:", e)
        logger.error("Error: %s",  e)
    sys.exit(rc)
