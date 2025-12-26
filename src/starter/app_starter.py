"""Main croosroad to start 'app starter'.add()

Processing args, init all required instance, etc.
"""
import argparse
import logging
import sys
from starter.app_run_preparation import AppPreparationAndRun
from starter.config import ConfigHandler
from starter.context import ContextHandler
from starter.common import path_to_valid_path
from starter.environment_structure import EnvironmentStructure
from starter.logging_settings import set_logging_settings

logger = logging.getLogger(__name__)


def main_starter(app_path=None, clear_environment=None, app_params=None):
    # Set logging settings
    set_logging_settings()

    logger.info("Startting app starter")

    env_structure = EnvironmentStructure()
    env_structure.prepare_env_structure()
    try:
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
            valid_path = path_to_valid_path(app_path)
            # Set app folder
            env_structure.set_path_app_folder(valid_path)
            config_handler.set_value_for_key("app_folder", valid_path)
        else:
            # Get app path from config
            config_app_path = config_handler.get_app_folder()
            config_app_path = path_to_valid_path(config_app_path)
            if config_app_path:
                env_structure.set_path_app_folder(config_app_path)
        # Fill config with path to app folder
        if app_params:
            config_handler.set_app_params(app_params)
        # App run prepraration instance
        app_preparation_and_run = AppPreparationAndRun(
            context_handler=context_handler,
            config_handler=config_handler,
            env_structure=env_structure)
        # Detect if app's content changed or flag to start over is set
        start_fresh = clear_environment \
            or app_preparation_and_run.app_files_changed()
        
        # if clear_environment or app_preparation_and_run.app_files_changed():
        if start_fresh:
            logger.info("Clearing environment")
            env_structure.remove_venv_folder()
            env_structure.prepare_venv_folder()
            # Remove context file, config file
            env_structure.remove_context_file()
            env_structure.prepare_context_file()
            config_handler.clean_config_file_from_not_required_items()
            # Recreate
            env_structure.prepare_env_structure()
            # Reload context, config
            context_handler.set_context_file(
                env_structure.get_path_context_file())
            context_handler.load_context()
            config_handler.set_config_file(
                env_structure.get_path_config_file())
            config_handler.load_config()

        # Time to prepare and start the app, if its possible
        app_preparation_and_run.venv_preparation()
        app_preparation_and_run.ready_and_start(start_fresh)
    except Exception as e:
        logger.error("Problem with preparing venv for app {%s}" % e)
        logger.info("Removing everything except folder with app.")
        env_structure.clear_environment_exclude_app_folder()


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
                        help='Flag to signal, clear environment.',
                        default=False)

    parser.add_argument('--app_params',
                        dest='app_params',
                        help='Params to pass to app',
                        default="")

    options = parser.parse_args()

    app_path = None
    clear_environment = False
    params = None
    try:
        app_path = options.app_path
        clear_environment = options.clear_environment
        params = options.app_params
    except Exception as e:
        # Something weng wrong, show me the error
        print("Error: %s", e, file=sys.stderr)

    # Default rc code
    rc = 1
    try:
        # Vzdy se preinstaluje vse.
        main_starter(app_path,
                     clear_environment,
                     params)
        rc = 0
    except Exception as e:
        print("Error:", e)
        logger.error("Error: {%s}" % e)
    sys.exit(rc)
