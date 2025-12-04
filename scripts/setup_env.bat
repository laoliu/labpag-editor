@echo off
REM ========================================
REM Project Environment Configuration
REM ========================================

REM Set project root directory
set "PROJECT_ROOT=%~dp0.."

REM Set pypag library path
REM Check if PYPAG_PATH environment variable is set (for custom pypag location)
if defined PYPAG_PATH (
    set "PAG_LIBPATH=%PYPAG_PATH%"
) else (
    REM Try project lib directory first
    if exist "%PROJECT_ROOT%\lib\pypag.pyd" (
        set "PAG_LIBPATH=%PROJECT_ROOT%\lib"
    ) else (
        REM Fallback to original pypag location
        set "PAG_LIBPATH=H:\work\python\libpag\python\venv\Lib\site-packages"
    )
)

REM Add pypag DLL directory to PATH for dependency resolution
set "PATH=%PAG_LIBPATH%\pypag;%PAG_LIBPATH%;%PATH%"

REM Set PYTHONPATH to include lib directory
set "PYTHONPATH=%PAG_LIBPATH%;%PYTHONPATH%"

REM Set Python interpreter path
REM Priority: PYTHON_EXE environment variable > Common paths > System PATH
if defined PYTHON_EXE (
    set "PYTHON=%PYTHON_EXE%"
) else (
    REM Check common Python installation paths
    if exist "d:\Python312\python.exe" (
        set "PYTHON=d:\Python312\python.exe"
    ) else if exist "C:\Python312\python.exe" (
        set "PYTHON=C:\Python312\python.exe"
    ) else if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
        set "PYTHON=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
    ) else (
        REM Use python from system PATH
        set "PYTHON=python.exe"
    )
)

REM Validate Python availability
%PYTHON% --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ========================================
    echo Warning: Python interpreter not found
    echo ========================================
    echo.
    echo Please do one of the following:
    echo.
    echo 1. Set PYTHON_EXE environment variable:
    echo    set PYTHON_EXE=D:\Python312\python.exe
    echo.
    echo 2. Add Python to system PATH
    echo.
    echo 3. Install Python 3.12 to default location:
    echo    - D:\Python312\
    echo    - C:\Python312\
    echo    - %%LOCALAPPDATA%%\Programs\Python\Python312\
    echo.
    echo ========================================
    exit /b 1
)

exit /b 0
