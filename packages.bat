@echo off
echo Installing or updating required packages...

:: Install or update pandas
echo Installing or updating pandas...
pip install --upgrade pandas

:: Install or update openpyxl
echo Installing or updating openpyxl...
pip install --upgrade openpyxl

:: Install or update tabulate
echo Installing or updating tabulate...
pip install --upgrade tabulate

:: Install or update matplotlib
echo Installing or updating matplotlib...
pip install --upgrade matplotlib

:: Install or update pillow
echo Installing or updating pillow...
pip install --upgrade pillow

:: Install or update sqlparse
echo Installing or updating sqlparse...
pip install --upgrade sqlparse

:: Install or update requests
echo Installing or updating requests...
pip install --upgrade requests

:: Install or update rich
echo Installing or updating rich...
pip install --upgrade rich

:: Install or update prompt_toolkit
echo Installing or updating prompt_toolkit...
pip install --upgrade prompt_toolkit

:: Install or update setuptools
echo Installing or updating setuptools...
pip install --upgrade setuptools

echo.
echo All packages installed/updated successfully!
pause
