@echo off
chcp 65001 > nul
setlocal EnableDelayedExpansion

echo ========================================
echo  测试 JSON 配置导出功能
echo ========================================
echo.

:: 检查 Python
where python > nul 2>&1
if errorlevel 1 (
    echo ❌ 未找到 Python
    echo.
    echo 请安装 Python 3.7 或更高版本
    pause
    exit /b 1
)

echo ✅ Python 已安装
echo.

:: 检查 libpag
python -c "import libpag" 2> nul
if errorlevel 1 (
    echo ⚠️ 未安装 libpag
    echo.
    echo 正在尝试安装 libpag...
    pip install libpag
    echo.
    
    python -c "import libpag" 2> nul
    if errorlevel 1 (
        echo ❌ libpag 安装失败
        echo.
        echo 注意：某些系统可能需要预编译的 wheel 文件
        echo 服务端导出功能将不可用
        echo.
        echo 不过，您仍然可以：
        echo 1. 使用 Web 编辑器导出 JSON 配置
        echo 2. 在其他安装了 libpag 的环境中使用 apply_json_to_pag.py
        echo.
        pause
    ) else (
        echo ✅ libpag 安装成功
    )
) else (
    echo ✅ libpag 已安装
)

echo.
echo ========================================
echo  启动测试环境
echo ========================================
echo.

:: 停止已有服务器
taskkill /F /IM python.exe /FI "WINDOWTITLE eq 导出服务器*" > nul 2>&1
taskkill /F /IM python.exe /FI "WINDOWTITLE eq Web服务器*" > nul 2>&1

echo [1/3] 启动导出服务器 (端口 5000)...
cd /d "%~dp0..\core"
start "导出服务器 - Port 5000" /MIN python pag_export_server.py
cd /d "%~dp0.."
timeout /t 2 /nobreak > nul

echo [2/3] 启动 Web 服务器 (端口 8000)...
cd web
start "Web服务器 - Port 8000" /MIN python -m http.server 8000
cd ..
timeout /t 2 /nobreak > nul

echo [3/3] 打开浏览器...
start http://localhost:8000/pag_template_editor.html
timeout /t 1 /nobreak > nul

echo.
echo ========================================
echo  ✅ 测试环境已启动！
echo ========================================
echo.
echo  📝 Web 编辑器: http://localhost:8000/pag_template_editor.html
echo  🔧 导出服务器: http://localhost:5000
echo.
echo ========================================
echo  📖 使用指南
echo ========================================
echo.
echo 步骤 1: 上传 PAG 模板文件
echo   - 拖放或点击上传
echo   - 查看图层列表
echo.
echo 步骤 2: 编辑内容
echo   - 选择文本图层，修改文字
echo   - 选择图片图层，上传新图片
echo   - 实时预览效果
echo.
echo 步骤 3A: 导出 JSON 配置
echo   - 点击"导出修改配置 (JSON)"
echo   - 保存配置文件
echo   - 后续可以批量使用
echo.
echo 步骤 3B: 一键导出 PAG ✨
echo   - 滚动到"高级：JSON 批量配置"区域
echo   - 点击"⚡ 应用配置并导出 PAG"
echo   - 自动生成并下载新 PAG 文件
echo.
echo 步骤 4: 导入已有 JSON 配置
echo   - 在 JSON 配置文本框中粘贴配置
echo   - 点击"⚡ 应用配置并导出 PAG"
echo   - 生成对应的 PAG 文件
echo.
echo ========================================
echo  🎯 测试要点
echo ========================================
echo.
echo 1. 文本修改测试
echo    - 修改任意文本图层
echo    - 查看预览效果
echo    - 导出 JSON 查看配置格式
echo.
echo 2. 图片修改测试
echo    - 上传新图片
echo    - 预览图片效果
echo    - 导出 JSON（自动包含 base64）
echo.
echo 3. JSON 配置导出测试
echo    - 完成上述修改后导出
echo    - 查看 JSON 文件内容
echo    - 确认包含所有修改
echo.
echo 4. 一键导出 PAG 测试 ✨
echo    - 不输入 JSON，直接点击导出
echo    - 或粘贴已有 JSON，点击导出
echo    - 确认生成的 PAG 文件可用
echo.
echo ========================================
echo  📁 测试文件建议
echo ========================================
echo.
echo 如果您没有 PAG 文件，可以：
echo 1. 使用 After Effects 导出一个简单的 PAG
echo 2. 从网上下载 PAG 样例文件
echo 3. 使用团队提供的模板文件
echo.
echo ========================================
echo  ❓ 故障排除
echo ========================================
echo.
echo 问题1: 点击"应用配置并导出 PAG"没反应
echo 解决: 
echo   - 检查浏览器控制台 (F12)
echo   - 确认导出服务器正在运行
echo   - 访问 http://localhost:5000 检查服务器状态
echo.
echo 问题2: 导出 JSON 后不知道如何使用
echo 解决:
echo   - 查看文档: JSON_CONFIG_MASTER.md
echo   - 查看文档: HOW_TO_USE_YOUR_JSON.md
echo   - 使用工具: apply_json_to_pag.py
echo.
echo 问题3: 服务器报错
echo 解决:
echo   - 检查 libpag 是否正确安装
echo   - 查看服务器窗口的错误信息
echo   - 重启服务器: 关闭后重新运行此脚本
echo.
echo ========================================
echo  📚 相关文档
echo ========================================
echo.
echo • JSON_TO_PAG_IN_BROWSER.md - 浏览器导出指南
echo • JSON_CONFIG_MASTER.md - JSON 配置完整指南
echo • HOW_TO_USE_YOUR_JSON.md - 使用导出的 JSON
echo • JSON_QUICK_START.md - 快速入门
echo.
echo ========================================
echo  按任意键停止所有服务器...
echo ========================================
pause > nul

echo.
echo 正在停止服务器...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq 导出服务器*" > nul 2>&1
taskkill /F /IM python.exe /FI "WINDOWTITLE eq Web服务器*" > nul 2>&1

echo ✅ 所有服务器已停止
echo.
echo 感谢测试！
pause
