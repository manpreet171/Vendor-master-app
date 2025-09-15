@echo off
echo SDGNY Vendor Management System - Data Import
echo ==========================================
echo.
echo This script will import data from your Excel file into the SQL Server database.
echo.

REM Check if Python is installed
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Python is not installed or not in your PATH.
    echo Please install Python and try again.
    goto :end
)

REM Check if required packages are installed
echo Checking required packages...
pip show pandas pyodbc python-dotenv >nul 2>nul
if %errorlevel% neq 0 (
    echo Installing required packages...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo Failed to install required packages.
        goto :end
    )
)

echo.
echo Starting data import...
python import_data.py

:end
echo.
echo Press any key to exit...
pause >nul
