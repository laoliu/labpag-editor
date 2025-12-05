@echo off
chcp 65001 >nul

REM 加载环境配置
call "%~dp0setup_env.bat"
if errorlevel 1 exit /b 1

echo ========================================
echo  PAG 模板编辑器 - 完整测试
echo ========================================
echo.

REM 设置 PYTHONPATH 指向项目内的 pypag 库
set "PAG_LIBPATH=%~dp0..\lib"

echo [步骤 1/3] 启动导出服务器...
start "PAG Export Server" cmd /c "set PYTHONPATH=%PAG_LIBPATH% && cd /d %~dp0..\core && d:\Python312\python.exe pag_export_server.py"
timeout /t 3 >nul

echo [步骤 2/3] 启动 Web 服务器...
start "PAG Web Server" cmd /c "cd /d %~dp0..\web && d:\Python312\python.exe -m http.server 8000"
timeout /t 2 >nul

echo [步骤 3/3] 打开浏览器...
start http://localhost:8000/pag_template_editor.html

echo.
echo ========================================
echo  服务器已启动！
echo ========================================
echo.
echo  导出服务器: http://localhost:5000
echo  Web 编辑器: http://localhost:8000/pag_template_editor.html
echo.
echo  使用方法:
echo  1. 上传 PAG 模板文件
echo  2. 修改文本和图片
echo  3. 点击"服务端导出 PAG"按钮
echo  4. 等待下载完成
echo.
echo  按任意键停止所有服务器...
pause >nul

echo.
echo 正在停止服务器...
taskkill /F /FI "WindowTitle eq PAG Export Server*" 2>nul
taskkill /F /FI "WindowTitle eq PAG Web Server*" 2>nul

echo 已停止。
pause
