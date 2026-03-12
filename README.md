# Starter
A simple app that lets you run your Python application without installing anything else. No Docker, VirtualBox, or similar tools are required.
The **Starter** is provided as an .exe file and is primarily intended for Linux and Windows. It has not been tested on macOS..

# How it works
The application uses the built-in venv package to create a virtual environment where both the dependencies and the application are installed. Supported formats include Python repositories with a pyproject.toml file, wheel packages, or the traditional setup.py format. 
An internet connection is required during the first two runs of **Starter** to download dependencies. This applies when running the application in stable mode, where the source code is not updated on every launch.
 
# First run
Download the application in .exe format. Place it in any location and run it (app_starter.exe).
During the first run, the application will create the folder and file structure required to prepare the environment where your app will be installed and managed.
You should see the following directory structure:
```
app_environment
  |- app
  |- app_venv
  |- context.json
  |- app_starter_config.json
```
The file _'app_starter_config.json'_ is important because it contains configuration 'keys' related to your application (such as the entry point file, startup parameters, and the application folder containing the source code) as well as keys used internally by **Starter** to store information about the application.

The _'app'_ folder is the default source directory for your application. It is the first location where **Starter** searches for the application source code if no custom path is defined in the configuration file.
```
app_files - internal info used by Starter
app_folder - location of your application code
app_params - argsument for your application
main_file - main file(e.g. "if __name__ = '__main__'")  
```

# Second run
Before running **Starter** a second time, you must update the _app_starter_config.json_ file.
It's straightforward; see the example below.
At a minimum, the following settings must be provided:
```
{
    "app_files": {},
    "app_folder": "/path/to/app/folder",
    "app_params": "",
    "main_file": "main.py" 
}
```
**Note**
- By setting 'main_file', you can speed up the startup of your application (**Starter** won’t search through every possible option).
- By setting 'app_folder', you are not forced to copy your application’s code into the default 'app' folder.
- Keep in mind that you need to escape your values when using **Starter** on the Windows platform (the JSON file will throw an error if the string is not properly escaped).

# Every run after that
At this point, you have set up **Starter** and your app to work together. This means that every time you run **Starter**, your app should start and be up and running within a few seconds (be patient—sometimes it may literally take a few seconds to start).

# Something went south
In this case, check the _app_starter.log_ file. It contains log messages from the **Starter** application, not your application.

# More info
Check HOWTO.pdf file.