# MAKO
Repository of example code and good practices for the Mutable Autonomous Kinetic Object

MAKO is a learning tool for robotics programming and component design.

## Installation

Follow the FRC2025 installation methods.

## Use

Double-click on `Start Command Prompt.bat` from Windows to start a command-
line prompt that has a poetry virtual environment already activated.  You
will know because the prompt will start with something like:

`(mako-py3.12) c:\Users\username\Desktop\MAKO>`

The same usage patterns as the FRC2025 repository apply

**Code development and deployment**

* If you are at the root of the repo: `robotpy --main code\foldename\filename.py deploy` deploys.
* If you are in the code\foldername\ folder already and the filename is robot.py,
   `robotpy deploy` is sufficient.

**Updating to a new robotpy version, if you are the first**

* Edit the pyproject.toml file to change the robotpy version number (2 places,
    in the [tool.poetry.dependencies] section and the [tool.robotpy] section).
* Run `poetry update` from the root folder, which will fetch the new versions.
* (Open question: I think we need to also run `robotpy sync` to get libraries
    like apriltag that are "extras" poetry doesn't know about.)
* Commit the changed pyproject.toml and poetry.lock files (the latter changed
    by poetry), and push them to GitHub.

**Updating to a new robotpy version, if you are not first**

* Pull from GitHub to get the changed pyproject.toml and poetry.lock files.
* Run `poetry install` from the root folder to fetch the new versions.
* (Open question: I think we need to also run `robotpy sync` to get libraries
    like apriltag that are "extras" poetry doesn't know about.)

**Updating the robot's robotpy libraries to new versions**
* First, do one of the updates above.
* (Open question: if we need to sync above, then the next step isn't needed.)
* Run `robotpy sync` from the root folder.  This will fetch both library files
    for your computer and the robot.  Many of them will have already been
    done by the update.
* When you deploy next, robotpy will download the proper files to the robot.


## Structure of folders in this repository

* `code\`
* `code\sensors\` - reading various sensors
* `code\command_based\` - exploration of the "command based" robot framework.
* `code\elevator\` - TimedRobot implementation of drivetrain and elevator
* `code\hello_robot\` - A basic robot that prints a message to verify installation
* `code\mecanum\` - TimedRobot implementation of mecanum-like omni wheel drivetrain
* `code\motor_test\` - simple TimedRobot to drive a motor.  Useful to connect MAKO 
  to an external motor or mechanism.
* `code\pixyvision\` - vision processing with the Pixy camera
* `doc\` - various documentation
* `doc\datasheets` – datasheets for roboRIO, VRM, other components
* `tools\` - 


## Miscellaneous details

Items you probably don't need to know about, but I want to document somewhere.

Robotpy and Poetry both manage Python packages, but Poetry does not know about
the "robotpy_extras", packages like Rev robotics (rev) and CTRE (phoenix6)
libraries.  Poetry also doesn't know about the Python interpreter and
packages that are needed for the robot.  So you will need to run both commands
when updating.

Robotpy is kind of designed to work with one "robot.py" file in the root folder.
It can work in other ways, because you can execute "robotpy --main other.py deploy",
but isn't optimal for syncing.

The command to get the extras onto your computer and also get the files for
the robot is "robotpy sync".  Here are some of its ideosyncracies (pun intended):

* Run `robotpy sync` from the root folder, and it will error if there is no 
    robot.py file.  That's not so good, because we want several subprojects
    in subfolders, not a single project.
* Run `robotpy --main path\to\file.py sync` from the root folder, and it will
    create a new pyproject.toml file in `path\to\`, and this will be a generic
    file without any of the extras included.  Then it will download the minimal set.
    You could edit that file, but we don't want to have to edit multiple
    pyproject.toml files every time we update Robotpy versions.
* Run `robotpy sync` from a subfolder that has a robot.py file in it, and you
    get the same minimal set and a new pyproject.toml.  Also not great.
* But you can pick up the main project's pyproject.toml file if you have a 
    robot.py file at the root and run `robotpy sync`.  The file can even have
    an error in it, because sync doesn't compile or run tests.  This is good,
    and more on that in a minute.
* You don't want to deploy the robot.py file in the root directory, because
    that will also copy everything in the repo (like the large datasheets)
    to the robot.  

This leads us to have a robot.py file in the root, but one with an error
in it.  Sync works as we want, and if someone accidentally tries to deploy,
there will be a syntax error and the deploy will fail.

It is kind of a hack, I know.
