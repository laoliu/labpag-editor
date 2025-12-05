# PAG 模板编辑器 - 服务端导出功能

## 🎉 新功能：真实 PAG 文件导出

通过**客户端-服务端架构**，实现了真正的 PAG 文件导出功能！

---

## 🏗️ 架构设计

```
┌─────────────────┐         ┌──────────────────┐
│  Web 编辑器     │         │  Python 服务器    │
│  (浏览器)       │         │  (Flask)          │
├─────────────────┤         ├──────────────────┤
│ 1. 加载 PAG     │         │                   │
│ 2. 预览修改     │         │                   │
│ 3. 保存原始文件 │         │                   │
│ 4. 保存修改记录 │         │                   │
│                 │         │                   │
│ 5. 导出请求 ────┼────────>│ 6. 接收数据       │
│    - 原始PAG    │         │                   │
│    - 修改配置   │         │ 7. 应用修改       │
│    - 图片数据   │         │    (libpag SDK)   │
│                 │         │                   │
│ 9. 下载文件 <───┼─────────│ 8. 返回新PAG      │
└─────────────────┘         └──────────────────┘
```

---

## 🚀 快速开始

### 步骤 1: 启动导出服务器

```powershell
# Windows
.\start_pag_export_server.bat

# 或手动启动
cd python
python pag_export_server.py
```

**服务器启动后：**
```
╔═══════════════════════════════════════╗
║   🚀 PAG 导出服务器                    ║
╚═══════════════════════════════════════╝

服务地址: http://localhost:5000
API 文档: http://localhost:5000/

PAG SDK 状态: ✅ 已安装

按 Ctrl+C 停止服务器
```

### 步骤 2: 启动 Web 服务器

```powershell
# 另开一个终端
.\start_pag_player.bat
```

### 步骤 3: 使用模板编辑器

```
1. 访问: http://localhost:8000/pag_template_editor.html
2. 上传 PAG 模板文件
3. 修改文本和图片内容
4. 点击"💾 服务端导出 PAG"按钮
5. 等待处理完成
6. 自动下载修改后的 PAG 文件
```

---

## 📋 完整功能对比

| 功能 | 配置导出 | 服务端导出 |
|------|---------|-----------|
| 实时预览 | ✅ | ✅ |
| 修改文本 | ✅ | ✅ |
| 替换图片 | ✅ | ✅ |
| **导出 PAG** | ❌ | ✅ |
| 需要服务器 | ❌ | ✅ |
| 导出格式 | JSON | PAG 文件 |
| 使用场景 | 批量处理 | 单文件编辑 |

---

## 🔧 技术实现

### Web 端（JavaScript）

```javascript
// 1. 保存原始 PAG 文件
let originalPagBuffer = null;

async function handleFile(file) {
    const buffer = await file.arrayBuffer();
    originalPagBuffer = buffer.slice(0); // 保存副本
    pagFile = await PAG.PAGFile.load(buffer);
}

// 2. 记录修改（包含图片 base64）
async function updateImage() {
    const imageBase64 = await readFileAsBase64(file);
    
    modifications.push({
        layerIndex: currentLayerIndex,
        type: 'image',
        value: file.name,
        imageData: imageBase64 // 完整的图片数据
    });
}

// 3. 发送到服务器
async function downloadPAGViaServer() {
    const formData = new FormData();
    formData.append('pagFile', new Blob([originalPagBuffer]));
    formData.append('modifications', JSON.stringify(modifications));
    
    const response = await fetch('http://localhost:5000/api/export-pag', {
        method: 'POST',
        body: formData
    });
    
    const blob = await response.blob();
    // 下载文件...
}
```

### 服务端（Python + Flask）

```python
from flask import Flask, request, send_file
import libpag
import tempfile

@app.route('/api/export-pag', methods=['POST'])
def export_pag():
    # 1. 接收原始 PAG 文件
    pag_file = request.files['pagFile']
    
    # 2. 接收修改配置
    modifications = json.loads(request.form.get('modifications'))
    
    # 3. 加载 PAG
    pag = libpag.PAGFile.Load(temp_path)
    
    # 4. 应用修改
    for mod in modifications:
        if mod['type'] == 'text':
            text_data = pag.getTextData(mod['layerIndex'])
            text_data.text = mod['value']
            pag.replaceText(mod['layerIndex'], text_data)
        
        elif mod['type'] == 'image':
            # 解码 base64 图片
            image_data = base64.b64decode(mod['imageData'].split(',')[1])
            # 创建 PAGImage
            image = libpag.PAGImage.FromPath(temp_image_path)
            pag.replaceImage(mod['layerIndex'], image)
    
    # 5. 保存并返回
    pag.save(output_path)
    return send_file(output_path, as_attachment=True)
```

---

## 📦 安装依赖

### Web 端（无需安装）
```
只需浏览器即可
```

### 服务端（Python）
```bash
# 基础依赖
pip install flask flask-cors

# PAG SDK（可选，未安装则使用模拟模式）
pip install libpag
```

**注意：** libpag 的安装可能需要特定的系统要求，请参考官方文档。

---

## 🎯 使用场景

### 场景 1: 单个文件快速编辑
```
设计师修改一个名片模板：
1. 上传名片.pag
2. 修改姓名、职位
3. 替换照片
4. 点击"服务端导出"
5. 获得 modified_名片.pag
```

### 场景 2: 测试后批量生成
```
运营人员测试活动海报：
1. 在 Web 编辑器中测试各种内容组合
2. 确认效果后，导出配置 JSON
3. 使用 Python 批量编辑器生成 100+ 海报
```

### 场景 3: API 集成
```
开发者集成到后端服务：
1. 前端发送修改请求到自己的 API
2. 后端调用 PAG 导出服务器
3. 返回生成的 PAG 文件给用户
```

---

## 🐛 故障排除

### 问题 1: "无法连接到导出服务器"

**症状：**
```
❌ 无法连接到导出服务器

请确保已启动服务器：
python pag/pag_export_server.py
```

**解决：**
```bash
# 1. 检查服务器是否运行
.\start_pag_export_server.bat

# 2. 检查端口是否被占用
netstat -ano | findstr :5000

# 3. 查看服务器日志
# 检查终端输出，是否有错误信息
```

### 问题 2: "PAG SDK 未安装"

**症状：**
```json
{
  "error": "PAG SDK 未安装",
  "message": "请运行: pip install libpag"
}
```

**解决：**
```bash
# 方案 1: 安装 libpag
pip install libpag

# 方案 2: 使用配置导出
# 点击"导出配置 JSON"按钮
# 使用 Python 批量编辑器处理
```

### 问题 3: 图片替换失败

**症状：**
服务器日志显示图片处理错误

**解决：**
```python
# 检查图片格式
支持的格式: PNG, JPG, WebP

# 检查图片大小
建议: < 5MB

# 检查 base64 编码
确保 imageData 字段包含完整的 data:image/...;base64,...
```

---

## 🔄 数据流程

### 上传 PAG 文件
```
浏览器选择文件
  ↓
File API 读取为 ArrayBuffer
  ↓
originalPagBuffer = buffer.slice(0) // 保存副本
  ↓
PAG.PAGFile.load(buffer) // 加载用于预览
```

### 修改内容
```
用户修改文本/图片
  ↓
读取图片为 base64
  ↓
modifications.push({
  layerIndex: 0,
  type: 'image',
  imageData: 'data:image/png;base64,...'
})
  ↓
实时预览更新
```

### 导出文件
```
点击"服务端导出"
  ↓
FormData 准备：
  - pagFile: Blob(originalPagBuffer)
  - modifications: JSON.stringify(modifications)
  ↓
POST http://localhost:5000/api/export-pag
  ↓
服务器接收 → 应用修改 → 保存 PAG
  ↓
返回 modified.pag
  ↓
浏览器自动下载
```

---

## 📊 性能考虑

| 操作 | 耗时 | 影响因素 |
|------|------|---------|
| 加载 PAG | < 1s | 文件大小 |
| 预览修改 | < 0.5s | 图层数量 |
| **服务端导出** | 2-5s | 修改数量、图片大小 |
| 配置导出 | < 0.1s | - |

**优化建议：**
- 图片压缩到合理大小（< 2MB）
- 批量编辑使用配置导出 + Python 批处理
- 单文件编辑使用服务端导出

---

## 🔒 安全考虑

### CORS 配置
```python
from flask_cors import CORS
CORS(app)  # 开发环境

# 生产环境
CORS(app, resources={
    r"/api/*": {
        "origins": ["https://yourdomain.com"]
    }
})
```

### 文件大小限制
```python
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB
```

### 临时文件清理
```python
# 自动清理临时文件
try:
    # ... 处理 ...
finally:
    os.unlink(temp_path)
```

---

## 📚 API 参考

### POST /api/export-pag

**请求：**
```
Content-Type: multipart/form-data

pagFile: <binary>
modifications: <JSON string>
```

**响应：**
```
Content-Type: application/octet-stream
Content-Disposition: attachment; filename="modified_template.pag"

<PAG file binary data>
```

**错误响应：**
```json
{
  "error": "错误描述",
  "traceback": "详细堆栈信息"
}
```

---

## 🎓 教程示例

### 示例 1: 修改名片

```javascript
// 1. 加载模板
handleFile(namecard_pag);

// 2. 修改文本
selectLayer(0, 'text');
document.getElementById('textInput').value = '张三';
await updateText();

selectLayer(1, 'text');
document.getElementById('textInput').value = '高级工程师';
await updateText();

// 3. 替换照片
selectLayer(2, 'image');
document.getElementById('imageInput').files = [photo_file];
await updateImage();

// 4. 导出
await downloadPAGViaServer();
```

### 示例 2: 批量处理

```python
# data.csv
姓名,职位,照片
张三,工程师,photos/zhang.jpg
李四,设计师,photos/li.jpg

# batch.py
import csv
from pag_batch_editor import PAGTemplateBatchEditor

with open('data.csv', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        editor = PAGTemplateBatchEditor('template.pag')
        editor.replace_text(0, row['姓名'])
        editor.replace_text(1, row['职位'])
        editor.replace_image(2, row['照片'])
        editor.save(f'output/{row["姓名"]}_namecard.pag')
```

---

## 🌟 总结

### ✅ 优势
- **真实导出** - 生成可用的 PAG 文件
- **实时预览** - 所见即所得
- **简单易用** - 无需命令行
- **灵活部署** - 可集成到现有系统

### ⚠️ 限制
- 需要运行服务器
- 依赖 libpag SDK
- 图片需要 base64 编码（文件稍大）

### 💡 最佳实践
- **单文件编辑** → 使用服务端导出
- **批量生成** → 使用配置导出 + Python
- **API 集成** → 调用导出服务器 API
- **快速测试** → Web 编辑器预览

---

**最后更新**: 2025-11-29  
**版本**: 3.0 - 服务端导出功能  
**状态**: ✅ 已实现并测试
