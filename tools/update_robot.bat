:: Batch file to put the latest robotpy packages downloaded with update_pc.bat onto the robot.
@echo off
echo ==
echo == You are connected to the robot, right?
echo == Updating robot with latest robotpy, CTRE, and REV libraries
echo ==
@echo on
python -m robotpy_installer install-robotpy
python -m robotpy_installer install-opkg python38-robotpy-ctre
python -m robotpy_installer install-opkg robotpy-rev
python -m robotpy_installer install-opkg robotpy-rev-color
