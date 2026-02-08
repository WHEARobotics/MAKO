# MAKO
Repository of example code and good practices for the Mutable Autonomous Kinetic Object

MAKO is a learning tool for robotics programming and component design.

## Installation

Follow the FRC2026 installation methods.

## Use

Double-click on `Start Command Prompt.bat` from Windows to start a command-
line prompt that has a virtual environment already activated.  You
will know because the prompt will start with something like:

`(.venv) c:\Users\username\Desktop\MAKO>`

The same usage patterns as the FRC2026 repository apply.

**Code development and deployment**

* Change directories to the folder with the sub-project code (e.g. code\hello_robot)
* `robotpy --main filename.py deploy` deploys.
* If the filename is robot.py, `robotpy deploy` is sufficient.

**Updating to a new robotpy version, if you are the first**

* Edit the pyproject.toml file in the root folder to change the robotpy version number in the [tool.robotpy] section.
* Execute `uv sync` from the root folder to update the robotpy/wpilib libraries on your machine.
* Copy the changed pyproject.toml to the rest of the sub-project
folders.
* Run `robotpy sync` from the sub-project folder you are currently working with, which will fetch the other dependencies needed for your computer and the roboRIO.
* Run `robotpy deploy` from the sub-project to deploy the new versions to the roboRIO along with your code.
* Commit and push the changes to the repository.

**Updating to a new robotpy version, if you are not first**

* Pull from GitHub to get the changed pyproject.toml files.
* Run `uv sync` from the root folder (in the proper virtual environment)
* Run `robotpy sync` from one of the sub-project folders to fetch the new versions of the dependencies.




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

## Some explanation

This procedure is a bit cumbersome; here are the reasons (copied from FRC2026 and edited to align with MAKO fodler naming).

"uv" is useful because it combines managing virtual environments and the Python packages installed within them.  It helps every developer on a team have the same environment and thus minimize the "but it works on my computer" problem.

"robotpy" is the official implementation of the FRC libraries for Python.  But in addition to the libraries, it includes some commands that simplify getting the code onto your computer and the robot.  These commands have some assumptions built in:

- `robotpy sync` and `robotpy deploy` (when the latter is changing libraries on the roboRIO) expect `pyproject.toml` to exist in the **same** folder as the robot.py file in order to get/deploy the extra libraries for REV and CTRE/phoenix6 motor controllers as well as Apriltag and the commands2 framework.  This is perfect if you just have one `robot.py` code at the top level of your repository.  In our case with multiple `code\<foldername>\robot.py` robot files for different purposes (testing motors, vision, etc.), it is possible to your command prompt in an activated environment at the top level folder and execute `robotpy --main code\hello_robot\hello_robot.py sync` (or deploy), and it will sync/deploy some stuff, but not the components/requires fields.  "import phoenix6" will fail when executing on the robot.

- `robotpy deploy` uploads everything in the folder containing the robot.py file onto the roboRIO. For us, that means that if we had `robot.py` at the top level folder, deploying also loads all the documentation files onto the robot.  This file isn't a problem because it is small, but the images, unnecessarily take up space and slow deployment.

The solution for now is to have a top-level `pyproject.toml` and to execute `uv` when in that folder.  This also manages the virtual environment and keeps its folder at the top level.  When we `robotpy sync` and `robotpy deploy`, we do it in one of the program folders (`code\<foldername>\robot.py`), using the program folder copy of `pyproject.toml`.  This avoids loading the documentation onto the roboRIO.
