# -*- coding: utf-8 -*-
"""Main entry point to start the 'Starter' app.

Processes the input arguments, initializes all required instances,
and performs necessary setup tasks.
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


def main_starter(app_path=None, clear_environment=False, main_file=None):
    try:
        # Sets upt logging configuration
        set_logging_settings()

        logger.info("Starts the Starter instance")
        env_structure = EnvironmentStructure(
            main_file=main_file
        )
        env_structure.prepare_env_structure()

        # Argument `clear_environment` is passed - clearing the 
        # environment.
        # All items, including the app folder, will be removed.
        if clear_environment:
            env_structure.clear_environment()
            # Create the environment structure from scratch.
            env_structure.prepare_env_structure()

        # Context handler
        context_handler = ContextHandler(
            context_file=env_structure.get_path_context_file()
        )
        # Config handler
        config_handler = ConfigHandler(
            config_file=env_structure.get_path_config_file()
        )
        # Check if the path to the app folder is set
        if app_path:
            valid_path = escape_string(app_path)
            # Set the path for the app folder
            env_structure.set_path_app_folder(valid_path)
            config_handler.set_value_for_key("app_folder", valid_path)
        else:
            # Get the app path from the config file
            config_app_path = config_handler.get_app_folder()
            config_app_path = escape_string(config_app_path)
            if config_app_path:
                env_structure.set_path_app_folder(config_app_path)

        # Initialize the app preparation instance.
        app_preparation_and_run = AppPreparationAndRun(
            context_handler=context_handler,
            config_handler=config_handler,
            env_structure=env_structure)

        start_fresh = app_preparation_and_run.app_files_changed()
        if start_fresh:
            env_structure.remove_venv_folder()
            env_structure.prepare_venv_folder()

        # Prepare and start the app, if possible.
        app_preparation_and_run.venv_preparation()
        app_preparation_and_run.ready_and_start(start_fresh)
    except Exception as e:
        logger.error(
            "Problem with preparing the venv for the app(%s).", e)
        # Clearing the whole app_environment(folder)
        # logger.info("Removing almost everything(app folder excluded).")
        # env_structure.clear_environment_exclude_app_folder()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog="App start",
        description="Preparing the enviroment for the app.")

    parser.add_argument('--app_path',
                        dest='app_path',
                        help='Specify the location where the app code is \
                              stored, to be used.',
                        default="")

    parser.add_argument('--clear_environment',
                        dest='clear_environment',
                        action='store_true',
                        help='Flag to signal to clearing the environment\
                              (removes everything completely).',
                        default=False)
    parser.add_argument('--main_file',
                        dest='main_file',
                        help='Specify the  name of the main file to start.',
                        default="")

    options = parser.parse_args()

    app_folder = None
    clear = None
    main_file = None

    try:
        app_folder = options.app_path
        clear = options.clear_environment
        main_file = options.main_file
    except Exception as e:
        # Something weng wrong, show the error
        print("Error: %s", e)

    # Default rc code
    rc = 1
    try:
        main_starter(app_folder,
                     clear,
                     main_file)
        rc = 0
    except Exception as e:
        print("Error:", e)
        logger.error("Error: %s",  e)
    sys.exit(rc)
