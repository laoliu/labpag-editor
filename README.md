# 🎨 PAG 模板编辑器

这是一个功能完整的 After Effects PAG 模板编辑器，支持在浏览器中可视化编辑 PAG 文件，无需 After Effects。

## 🚀 快速开始

### 启动服务器

```bash
# Windows
cd scripts
.\restart_clean.bat

# 或使用 PowerShell
.\restart_clean.ps1
```

访问: http://localhost:8000/pag_template_editor.html

### 功能特性

- ✅ **可视化编辑** - 在浏览器中直接编辑 PAG 文件
- ✅ **文本替换** - 修改文本内容、字体、大小
- ✅ **图片替换** - 替换图层图片，保持原始变换
- ✅ **图层变换** - 调整位置、旋转、缩放、不透明度
- ✅ **实时预览** - 即时查看修改效果
- ✅ **导出功能** - 导出修改后的 PAG 或 JSON 配置
- ✅ **批量处理** - 支持批量生成多个 PAG 文件

## 📁 目录结构

```
libpag-editor/
├── 📚 docs/                       # 文档
│   ├── api/                       # API 参考
│   ├── features/                  # 功能说明
│   ├── guides/                    # 使用指南
│   └── troubleshooting/           # 故障排除
│
├── 🎯 core/                       # 核心功能（Python）
│   ├── pag_export_server.py       # 导出服务器 API
│   ├── pag_runtime_renderer.py    # 运行时渲染器
│   ├── pag_batch_editor.py        # 批量编辑器
│   └── pag_generator.py           # PAG 生成器
│
├── 🌐 web/                        # Web 前端
│   ├── pag_template_editor.html   # 主编辑器界面
│   ├── pag_player.html            # PAG 播放器
│   └── lib/                       # 前端库文件
│
├── 🔧 scripts/                    # 辅助脚本
│   ├── restart_clean.bat          # 重启服务器
│   ├── start_pag_export_server.bat # 启动导出服务器
│   └── start_pag_player.bat       # 启动播放器
│
├── 📦 pylib/                      # Python 库（本地 pypag）
│   ├── pypag.pyd                  # PAG Python 绑定
│   └── libpag.dll                 # PAG 核心库
│
├── 🧪 tests/                      # 测试文件
└── 🛠️ tools/                     # 工具脚本
```

## 🎯 核心功能

### 1. Web 编辑器

**访问**: http://localhost:8000/pag_template_editor.html

**功能**:
- 📂 上传 PAG 模板文件
- 📋 查看和选择图层
- ✏️ 编辑文本和图片
- 🎨 调整图层变换（位置、旋转、缩放等）
- 👁️ 实时预览效果
- 💾 导出修改后的 PAG 或 JSON 配置

### 2. PAG 导出服务器

**文件**: `core/pag_export_server.py`  
**端口**: http://localhost:5000

**API 端点**:
```
POST /api/export-pag          # 导出修改后的 PAG 文件
POST /api/analyze-layers      # 分析 PAG 图层信息
GET  /api/health              # 健康检查
GET  /api/debug-matrix        # 调试 Matrix API
```

**启动方式**:
```bash
cd core
D:\Python312\python.exe pag_export_server.py
```

### 3. PAG 运行时渲染器

**文件**: `core/pag_runtime_renderer.py`

支持运行时应用变换的渲染器，无需重新保存 PAG 文件。

```python
from core.pag_runtime_renderer import PAGRuntimeRenderer

renderer = PAGRuntimeRenderer('template.pag')
renderer.load().load_config(config)
renderer.apply_image_replacements()
renderer.render_frame(0.5)
```

### 4. PAG 批量编辑器

**文件**: `core/pag_batch_editor.py`

批量处理 PAG 文件，适用于大规模内容生成。

```python
from core.pag_batch_editor import PAGTemplateBatchEditor

editor = PAGTemplateBatchEditor('template.pag')
editor.replace_text(0, '新文本')
editor.replace_image(0, 'new_image.png')
editor.save('output.pag')
```

## 📖 文档导航

- [JSON 导出指南](docs/JSON_TO_PAG_IN_BROWSER.md) - 浏览器中导出 PAG
- [PAG 编辑器完整文档](docs/PAG_EDITOR_COMPLETE.md) - 全面的技术文档
- [快速参考](docs/PAG_EDITOR_QUICK_REF.md) - 常用操作
- [服务器导出指南](docs/SERVER_EXPORT_GUIDE.md) - 后端导出完整流程

## 🛠️ 安装和配置

### 环境要求

- **Python**: 3.8+ (推荐 3.12)
- **操作系统**: Windows 10/11
- **浏览器**: Chrome, Edge, Firefox (现代浏览器)

### 依赖安装

```bash
# 安装 Python 依赖
pip install -r requirements_export_server.txt

# 主要依赖:
# - Flask (Web 服务器)
# - Flask-CORS (跨域支持)
# - pypag (已包含在 pylib/ 目录)
```

### 配置 Python 环境

项目包含本地 pypag 库（`pylib/` 目录），无需额外安装 libpag。

如果需要使用其他 pypag 版本，可以修改 `core/pag_export_server.py` 中的路径：

```python
# 获取项目根目录
project_root = Path(__file__).parent.parent
pypag_path = str(project_root / 'pylib')
```

## 🧪 测试

### 运行测试

```bash
# 变换功能完整测试
python tests/test_transform_complete.py

# 持久化方法测试
python tests/test_persistence_methods.py

# API 简单测试
python tests/test_api_simple.py
```

### 快速测试脚本

```bash
# 测试 JSON 导出
scripts\test_json_export.bat

# 完整测试编辑器
scripts\test_pag_editor_full.bat

# 检查 PyPAG API
scripts\check_pypag_api.bat
```

## 🔧 工具脚本

### apply_json_to_pag.py
从 JSON 配置应用修改到 PAG 文件

```bash
python tools/apply_json_to_pag.py config.json template.pag output.pag
```

### check_api_simple.py
检查 pypag API 可用性

```bash
python tools/check_api_simple.py
```

### render_with_transforms.py
使用运行时变换渲染示例

```bash
python tools/render_with_transforms.py
```

## 📝 使用流程

### 1. 基础编辑流程

1. **启动服务器**
   ```bash
   cd scripts
   .\restart_clean.bat
   ```

2. **打开编辑器**
   访问 http://localhost:8000/pag_template_editor.html

3. **上传 PAG 模板**
   拖拽或点击上传 `.pag` 文件

4. **编辑内容**
   - 选择图层
   - 修改文本或替换图片
   - 调整变换参数

5. **预览效果**
   点击"刷新预览"查看修改效果

6. **导出文件**
   - 导出 PAG：生成新的 .pag 文件
   - 导出 JSON：保存配置用于批量处理

### 2. 批量处理流程

1. **在编辑器中设计模板**
   编辑并导出 JSON 配置

2. **准备批量数据**
   创建包含多个配置的 JSON 文件

3. **批量生成**
   ```bash
   python core/pag_batch_editor.py
   ```

4. **使用生成的文件**
   在 `output/` 目录查看生成的 PAG 文件

## 🎬 示例场景

### 场景 1: 个性化名片生成

```python
from core.pag_batch_editor import PAGTemplateBatchEditor

configs = [
    {'name': '张三', 'title': '产品经理', 'phone': '138****1234'},
    {'name': '李四', 'title': '设计师', 'phone': '139****5678'},
]

for config in configs:
    editor = PAGTemplateBatchEditor('namecard_template.pag')
    editor.replace_text(0, config['name'])
    editor.replace_text(1, config['title'])
    editor.replace_text(2, config['phone'])
    editor.save(f"output/{config['name']}_namecard.pag")
```

### 场景 2: 活动海报批量生成

1. 在编辑器中设计基础模板
2. 导出 JSON 配置
3. 修改 JSON 配置中的文本和图片路径
4. 使用批量脚本生成多个版本

### 场景 3: 动态内容更新

使用运行时渲染器，无需重新生成 PAG：

```python
renderer = PAGRuntimeRenderer('template.pag')
renderer.load_config({
    'modifications': [
        {'type': 'text', 'layerIndex': 0, 'value': '动态标题'},
        {'type': 'image', 'layerIndex': 0, 'value': 'dynamic_image.png'}
    ]
})
renderer.render_video('output.mp4')
```

## 🐛 故障排除

### 问题 1: 服务器启动失败

**症状**: 运行 restart_clean.bat 后无法访问页面

**解决方案**:
1. 检查端口是否被占用
   ```bash
   netstat -ano | findstr :8000
   netstat -ano | findstr :5000
   ```
2. 确认 Python 路径正确
3. 查看终端输出的错误信息

### 问题 2: 图层位置不正确

**症状**: 替换图片后位置偏移

**原因**: 使用了错误的 Matrix API

**解决方案**:
- 确保使用 `getTotalMatrix()` 而非 `getOriginalImageMatrix()`
- 检查 pylib 中的 pypag.pyd 是否是最新版本

### 问题 3: 导出 PAG 失败

**症状**: 点击导出按钮没有反应或报错

**解决方案**:
1. 确认导出服务器正在运行
2. 检查浏览器控制台（F12）的错误信息
3. 确认 pypag 版本支持 `save()` 方法

更多问题参考: [故障排除文档](docs/troubleshooting/)

## 📊 性能优化

### 大文件处理

- 建议 PAG 文件大小 < 10MB
- 图片替换建议使用压缩后的图片
- 批量处理时使用多进程

### 内存优化

```python
# 处理完及时释放资源
renderer.dispose()
del renderer
```

## 🔗 相关资源

- [libpag 官方网站](https://pag.art/)
- [libpag GitHub](https://github.com/Tencent/libpag)
- [libpag 文档](https://pag.art/docs/)
- [After Effects 官方文档](https://helpx.adobe.com/after-effects/user-guide.html)

## 📝 更新日志

### 2025-12-05
- ✅ 使用 `getTotalMatrix()` 获取正确的图层位置
- ✅ 将 pypag 和 libpag.dll 集成到项目本地 `pylib/` 目录
- ✅ 修复图层位置显示不正确的问题
- ✅ 优化 favicon 加载，消除 404 错误

### 2025-12-04
- ✅ 实现运行时变换渲染系统
- ✅ 添加前端变换预览功能
- ✅ 创建完整的测试套件
- ✅ 重组文件结构

### 2024-12-03
- ✅ 图层变换功能
- ✅ 图片预览功能
- ✅ 自动预览功能

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

本项目基于 MIT 许可证。

---

**维护者**: GitHub Copilot  
**最后更新**: 2025-12-05
