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
:: Rename because python 3.12 vs. >=3.13
:: Install pyinstaller to created venv
CALL pip install %pyinstaller%
:: Create output using pyinstaller
CALL pyinstaller src\\starter\\app_starter.py --add-data %venv%\\pyvenv.cfg:. --add-data %venv%\\Scripts\\python.exe:. --add-data src\\starter\\maginician.py:.
:: Copy pyvenv.cfg
COPY /B dist\\app_starter\\_internal\\pyvenv.cfg dist\\pyvenv.cfg
:: Copy python.exe --> app_starter
COPY /B dist\\app_starter\\_internal\\python.exe dist\\app_starter\\python.exe /B
:: Deativate venv
CALL %venv%\\Scripts\\deactivate
:: Remove venv
@RD /S /Q %venv%
:: Clean console
::CLS