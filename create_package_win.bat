@echo off
:: Version of pyinstaller you want to use
SET pyinstaller=pyinstaller==6.17.0
:: Set the python shortcut you are using on your OS
SET python=python312
:: Name of the venv for pyinstaller
SET venv=starter_win
:: Create venv using specified python
CALL %python% -m venv %venv%
:: Activate venv
CALL %venv%\\Scripts\\activate
:: Install pyinstaller to created venv
CALL pip install %pyinstaller%
:: Create output using pyinstaller
CALL pyinstaller src\\starter\\app_starter.py --add-data src\\starter\\maginician.py:. --add-data %venv%\\Scripts\\%python%.exe:.
:: Rename python exe file related to your python version to default name
SET current_python_path=dist\\starter\\_internal\\%python%.exe
SET new_python_name=python.exe
IF EXIST %current_python_path% (
    REN %current_python_path% %new_python_name%
)
:: Deativate venv
CALL %venv%\\Scripts\\deactivate
:: Remove venv
::@RD /S /Q %venv%
:: Clean console
::CLS