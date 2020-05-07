:: Batch file to change to the proper folder and set up the environment.
:: You might want to copy this file onto your desktop, or into a "Documents" folder
:: for ease of finding it.  Don't edit this master copy in the GitHub repository
:: unless something more universal changes.
::
:: This file assumes that you have Anaconda installed and there is an environment
:: set up for PyFRC code.  It also uses the folder path as on Rod Hinman's computer.
:: You may want to edit the path below.

@echo off
color 2
echo ===================================================================================
echo ==== Setup batch file for robotpy for the MAKO project ====
echo =
echo    Usage:
echo    For python, use "python", not "py -3".
echo    To develop code, change directories/folders to the folder where the code is,
echo       for example: cd code\component_examples
echo =
echo    To deploy, "python robot.py deploy" when you are in that same folder.
echo = 
echo    To update parts of the installation, "python -m pip install --upgrade <package_name>".
echo    To get the executables for the roboRIO  "python -m robotpy_installer download-robotpy".
echo                          or other packages "python -m robotpy_installer download-opkg <package_name>".
echo    To put those executables on the roboRIO "python -m robotpy_installer install-robotpy".
echo                          or other packages "python -m robotpy_installer install-opkg <package_name>".
echo    I would suggest that you always do updates from a consistent folder.  Rod is using
echo       the FRC2020 repository at the moment, because that's where 2020 code was originally
echo       updated.
echo =
echo ===================================================================================
echo .

:: Change to the proper directory, the git repository for the MAKO project.
:: Edit the folder path to the location on your machine.
cd c:\gh\wh\MAKO

:: Activate the virtual environment set up for robotpy.
call c:\ProgramData\Anaconda3\Scripts\activate.bat frc2020a

rem Stop in a command prompt.
cmd /k
