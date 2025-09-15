@echo off
echo Setting up virtual environment for SDGNY Vendor Management System...

REM Check if Python is installed
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Python is not installed or not in your PATH.
    echo Please install Python and try again.
    goto :end
)

REM Create virtual environment if it doesn't exist
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
) else (
    echo Virtual environment already exists.
)

REM Activate virtual environment and install requirements
echo Activating virtual environment and installing requirements...
call venv\Scripts\activate.bat
pip install -r requirements.txt

echo.
echo Virtual environment setup complete!
echo.
echo To activate the virtual environment, run:
echo     venv\Scripts\activate.bat
echo.
echo To test the database connection, run:
echo     python test_connection.py
echo.
echo To run the Streamlit app (once created), run:
echo     streamlit run app.py
echo.

:end
pause
