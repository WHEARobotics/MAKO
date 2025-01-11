:: Batch file to change to the proper folder and set up the environment.
:: This file assumes that python poetry is on your computer and you have already
:: run "poetry install" to create a virtual environment for the project.
:: This file should only be used on Rod's computer because I use a different
:: folder structure than WHEA's computers.
@echo off


:: Change to the proper directory, the git repository for the MAKO project.
cd c:\gh\wh\MAKO

:: Activate the virtual environment set up for robotpy.
poetry env activate > temp.bat
call temp.bat
del temp.bat

:: Stop in a command prompt.
cmd /k
@echo on
