@echo off
chcp 65001 >nul

REM 加载环境配置
call "%~dp0setup_env.bat"
if errorlevel 1 exit /b 1

cd /d "%~dp0..\tools"
%PYTHON% check_pypag_api.py
pause
