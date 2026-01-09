# Starter
Simple app to help you run your python app without necesity to install anything else. No docker, virtual box, etc. is required.
**Starter** is in exe file format, primary suited for linux, windows use(never tested at mac OS platform).

# How it works
Its using venv(build-in) package, where we install dependencies and app itself. Supported format are python repo with pyproject.toml file, wheel format or just good oldschool setup.py format. 
Internet connection is required for first two runs of Starter to download dependencies in case you plan to use **Starter** to start app with stable, not "updated source code every single time", app.
 
# First run
Get the app in exe file format. Place it to location of your desire and run it(app_starter.exe). First run of app should prepare folder, files
structure used for preparation of environment where your app will be installed and managed.
You should see structure tree
```
app_environment
  |- app
  |- app_venv
  |- context.json
  |- app_starter_config.json
```
File _'app_starter_config.json'_ is important because it contains mix of 'keys' related to your app(name of the main file - entry point, params to use to start your app with, app folder - location of you app souce code) and some 'keys' used by Starter itself to keep info about your app.
The folder _'app'_ is default source folder for your app(first place to search for source code/file) in case you are not using config to set it from there. 

```
app_files - internal info for Starter
app_folder - location of you app source code
app_params - args for your app
main_file - main file(e.g. "if __name__ = '__main__'")  
```

# Second run
Before you run the **Starter** second time you have to fill the _app_starter_config.json_. Its very simple, see example.
The minimum setting should be
```
{
    "app_files": {},
    "app_folder": "/path/to/app/folder",
    "app_params": "",
    "main_file": "main.py" 
}
```
**Note**
- By setting _'main_file'_ you speed up the starting of your app(**Starter** is not searching for every possibility).
- Setting _'app_folder'_ you are not forced to copy the code of your app to default _'app'_ folder.
- Bear in mind to escape your set up value in case using **Starter** at windows platform(json file is going to scream at you if you fill not escaped string)


# Every run after that
Right now you had setup **Starter** and your app to cooperate. That mean everytime you run **Starter**, your app should up and running in few seconds(be patient, some times it can take literallz few second to start).

# Something went south
It case of this, look for file _app_starter.log_ file. It contains log messages from **Starter** app NOT your app.

# More info
Check HOWTO.pdf file.