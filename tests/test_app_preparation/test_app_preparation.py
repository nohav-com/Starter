from pathlib import Path

import pytest

from starter.app_run_preparation import AppPreparationAndRun


@pytest.fixture(scope="function")
def app_run_preparation_instance(
        config_handler, context_handler, environment_structure_designated):
    """Preprate instance of app run preparation class."""
    env_struct = environment_structure_designated[0]
    env_struct.prepare_env_structure()

    prepare = AppPreparationAndRun(
        config_handler=config_handler,
        context_handler=context_handler,
        env_structure=env_struct
    )

    yield (prepare, env_struct)

    del prepare


def test_get_app_folder_from_environment(app_run_preparation_instance):
    """Just get app folder path."""
    assert Path(
            app_run_preparation_instance[0].get_app_folder_from_environment()
        ).exists()


def test_get_plaform_handler(app_run_preparation_instance):
    """Get platform handler."""
    assert app_run_preparation_instance[0].get_platform_handler() is not None


@pytest.mark.skip(reason="Not properly working without internet connection.")
def test_venv_preparation(app_run_preparation_instance):
    """Just prepare venv. It takes"""
    app_run_preparation_instance[0].venv_preparation()


def test_ready_and_start_nothing_to_install(app_run_preparation_instance):
    """Call ready and start with nothing to install."""
    app_run_preparation_instance[0].ready_and_start()


def test_ready_and_start_fail(app_run_preparation_instance, monkeypatch):
    """Call ready and start method and fail."""
    monkeypatch.setattr(Path, "joinpath", Exception("Exception"))
    with pytest.raises(Exception):
        app_run_preparation_instance[0].ready_and_start()


def test_app_files_changed_nothing_to_check(app_run_preparation_instance):
    """Call method detecting if files changed with nothing to check."""
    # Everytime the list of file from config file is empty
    # --> handled as fresh start
    changed = app_run_preparation_instance[0].app_files_changed()
    assert not changed


def test_app_files_changed(app_run_preparation_instance):
    """Call app file changed method."""
    # Create some file
    app_folder = app_run_preparation_instance[1].get_path_app_folder()
    file = Path(app_folder).joinpath("test.py")
    with open(str(file), "w") as f_in:
        f_in.write("#comment 1")
    # Check files
    changed = app_run_preparation_instance[0].app_files_changed()
    assert not changed
