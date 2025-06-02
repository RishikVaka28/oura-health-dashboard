# we can run app.py i modified it so that it automatically runs both files
@echo off
echo Launching app.py and oura.py silently...

start "" /min pythonw "C:\path\to\app.py"
start "" /min pythonw "C:\path\to\oura.py"
