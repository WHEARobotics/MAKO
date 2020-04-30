:: Batch file to get all the latest PYFRC code onto the PC, and download updates for the robot.
@echo off
echo ==
echo == Updating PC with pyfrc/robotpy/wpilib, and the CTRE and REV color libraries
echo ==
@echo on
python -m pip install --upgrade pyfrc wpilib
:: Update all the other libraries that don't always update when the above do.
python -m pip install --upgrade pynetconsole pynetworktables pyntcore robotpy-hal robotpy-halsim-gui
python -m pip install --upgrade robotpy-installer robotpy-wpilib-utilities robotpy-wpiutil
python -m pip install --upgrade robotpy-ctre robotpy-rev robotpy-rev-color
@echo off
echo ==
echo == Downloading roboRIO packages to PC.
echo ==
@echo on
python -m robotpy_installer download-robotpy
python -m robotpy_installer download-opkg python38-robotpy-ctre
python -m robotpy_installer download-opkg robotpy-rev
python -m robotpy_installer download-opkg robotpy-rev-color
@echo off
echo ==
echo == Don't forget to connect to the robot and run update_robot.bat
echo == to download the latest robotpy packages to the roboRIO.
echo ==
