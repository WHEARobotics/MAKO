# MAKO
Repository of example code and good practices for the Mutable Autonomous Kinetic Object

MAKO is a learning tool for robotics programming and component design.

## Installation

Follow the FRC2025 installation methods.

## Use

Double-click on `Start Command Prompt.bat` from Windows to start a command-
line prompt that has a virtual environment already activated.  You
will know because the prompt will start with something like:

`(.venv) c:\Users\username\Desktop\MAKO>`

The same usage patterns as the FRC2025 repository apply

**Code development and deployment**

* Change directories to the folder with the sub-project code (e.g. code\hello_robot)
* `robotpy --main filename.py deploy` deploys.
* If the filename is robot.py, `robotpy deploy` is sufficient.

**Updating to a new robotpy version, if you are the first**

* Edit the pyproject.toml file in one of the sub-projects to change the robotpy
   version number in the [tool.robotpy] section.
* Run `robotpy sync` from that sub folder, which will fetch the new versions.
* Deploy your code.
* If things work, copy the changed pyproject.toml to the rest of the sub-project
folders.

**Updating to a new robotpy version, if you are not first**

* Pull from GitHub to get the changed pyproject.toml files.
* Run `robotpy sync` from one of the sub-project folders to fetch the new versions.




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

