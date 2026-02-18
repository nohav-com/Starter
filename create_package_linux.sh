#!/bin/bash

# Version of pyinstaller to use
PYINSTALLER=pyinstaller==6.17.0
# Set the python shortcut you are using on your OS
PYTHON=python3.12
# Name of the venv for pyinstaller
VENVNAME=starter_linux
# Create venv using specified python
$PYTHON -m venv $VENVNAME
# Activate venv
ACTIVATE=`source $VENVNAME/bin/activate`
echo $ACTIVATE
# Install pyinstaller
INSTALL_PYINSTALLER=`$VENVNAME/bin/pip install $PYINSTALLER`
echo $INSTALL_PYINSTALLER
# Create output
CONVERT=`$VENVNAME/bin/pyinstaller src/starter/app_starter.py --add-data $VENVNAME/pyvenv.cfg:. --add-data src/starter/maginician.py:. --add-data $VENVNAME/bin/python:.`
echo $CONVERT
# Clean up
rm -r $VENVNAME