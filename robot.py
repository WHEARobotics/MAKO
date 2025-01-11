import wpilib

class MyRobot(wpilib.TimedRobot):
    def robotInit(self):
        """Dummy file to simplify robotpy sync"""
        This is an error to stop you from deploying.
        Deploy from the root folder with "robotpy --main code\foldername\filename.py deploy".
        Or cd to the subproject folder you are working on and deploy from there.

        But the existence of this file lets you run "robotpy sync" from the root directory
        where it will pick up the main pyproject.toml file and download the dependencies you
        want.  If you don't have a file here, sync will error.  If you do execute 
        "robotpy --main code\foldername\filename.py sync", it will create a generic 
        pyproject.toml file in `code\foldername` that doesn't have any 
        extras like apriltags included.  You won't get the installation you want.
        print("Failure")

