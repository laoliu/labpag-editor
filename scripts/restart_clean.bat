@echo off
chcp 65001 >nul
echo ========================================
echo  强制重启所有 PAG 服务器
echo ========================================
echo.

echo [1/4] 关闭所有旧的 Python 服务器进程...
taskkill /F /FI "WINDOWTITLE eq PAG Export Server*" 2>nul
taskkill /F /FI "WINDOWTITLE eq PAG Web Server*" 2>nul
timeout /t 1 >nul

echo [2/4] 检查端口占用...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5000') do (
    echo    关闭端口 5000 的进程 %%a
    taskkill /F /PID %%a 2>nul
)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000') do (
    echo    关闭端口 8000 的进程 %%a
    taskkill /F /PID %%a 2>nul
)
timeout /t 2 >nul

REM 设置 PYTHONPATH 指向新版本 pypag（支持 save 功能）
set "PAG_LIBPATH=H:\work\python\libpag\python\venv\Lib\site-packages"

echo [3/4] 启动导出服务器（新配置：100MB 限制）...
start "PAG Export Server" cmd /c "set PYTHONPATH=%PAG_LIBPATH% && cd /d h:\work\python\libpag-editor\core && d:\Python312\python.exe pag_export_server.py"
timeout /t 3 >nul

echo [4/4] 启动 Web 服务器...
start "PAG Web Server" cmd /c "cd /d h:\work\python\libpag-editor\web && d:\Python312\python.exe -m http.server 8000"
timeout /t 2 >nul

echo.
echo ========================================
echo  ✅ 所有服务器已重启！
echo ========================================
echo.
echo  导出服务器: http://localhost:5000
echo  最大文件: 100 MB（新配置）
echo  Web 编辑器: http://localhost:8000/pag_template_editor.html
echo.
echo  请按任意键打开浏览器...
pause >nul

start http://localhost:8000/pag_template_editor.html

echo.
echo  浏览器已打开！
echo  请按 Ctrl+F5 强制刷新页面
echo.
pause
