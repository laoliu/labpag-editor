# 🌐 在浏览器中导出 JSON 配置并生成 PAG 文件

## 🎯 新功能介绍

现在 `pag_template_editor.html` 页面支持**一键应用 JSON 配置并导出 PAG 文件**！

### ✨ 功能亮点

1. **在线预览** - 实时查看 PAG 模板效果
2. **可视化编辑** - 修改文本和图片图层
3. **导出 JSON 配置** - 保存修改配置
4. **⚡ 一键应用并导出** - 将 JSON 配置直接应用到模板，生成新 PAG 文件（新增）

---

## 🚀 使用方法

### 方法 1: 编辑后直接导出

```
步骤：
1. 打开 http://localhost:8000/pag_template_editor.html
2. 上传 PAG 模板文件
3. 选择图层进行编辑（文本/图片）
4. 滚动到页面底部"高级：JSON 批量配置"区域
5. 点击"⚡ 应用配置并导出 PAG"按钮
6. 等待生成完成，自动下载新 PAG 文件
```

**特点：**
- 使用当前编辑的修改记录
- 无需手动复制 JSON
- 一键完成

---

### 方法 2: 导入 JSON 配置后导出

```
步骤：
1. 打开编辑器页面
2. 上传 PAG 模板文件
3. 在"高级：JSON 批量配置"文本框中粘贴 JSON 配置
4. 点击"⚡ 应用配置并导出 PAG"按钮
5. 等待生成完成
```

**JSON 配置示例：**

```json
{
  "modifications": [
    {
      "layerIndex": 0,
      "type": "text",
      "value": "新的标题"
    },
    {
      "layerIndex": 1,
      "type": "image",
      "imageData": "data:image/jpeg;base64,/9j/4AAQSkZJRg..."
    }
  ]
}
```

**特点：**
- 支持批量配置
- 可复用之前导出的 JSON
- 适合测试不同内容

---

## 📊 三种导出方式对比

| 方式 | 位置 | 用途 | 优点 |
|------|------|------|------|
| **📋 导出配置 JSON** | 预览区域 | 保存修改配置 | 可批量处理 |
| **💾 服务端导出 PAG** | 顶部提示区 | 导出当前修改 | 直接生成 PAG |
| **⚡ 应用配置并导出 PAG** | JSON 配置区 | 应用 JSON 生成 PAG | 灵活性强 |

---

## 🎬 完整工作流程

### 场景 1: 单文件编辑

```
1. 上传模板 ─→ 2. 可视化编辑 ─→ 3. 点击"应用配置并导出 PAG"
                                        ↓
                                    生成新 PAG 文件
```

### 场景 2: 测试多个版本

```
1. 上传模板
   ↓
2. 修改内容 → 导出 JSON (version1.json)
   ↓
3. 清空修改，再次编辑 → 导出 JSON (version2.json)
   ↓
4. 分别粘贴 version1.json 和 version2.json
   ↓
5. 每个都点击"应用配置并导出 PAG"
   ↓
6. 获得两个不同的 PAG 文件
```

### 场景 3: 结合批量工具

```
Web 编辑器:
1. 设计并测试一个模板
2. 导出 JSON 配置作为样本

Python 脚本:
3. 基于样本生成100个不同配置
4. 使用 apply_json_to_pag.py 批量生成

如需单独调整:
5. 将某个配置粘贴到 Web 编辑器
6. 使用"应用配置并导出 PAG"生成单个文件
```

---

## ⚙️ 技术说明

### 前提条件

**必须启动后端服务器：**

```bash
# 方式 1: 使用批处理脚本
.\start_pag_export_server.bat

# 方式 2: 手动启动
python pag_export_server.py

# 方式 3: 完整测试环境
.\test_pag_editor_full.bat
```

**服务器状态检查：**

访问 http://localhost:5000 应该显示服务器信息。

### 工作原理

```
浏览器
  ├─ 上传 PAG 模板（保存为 ArrayBuffer）
  ├─ 编辑或导入 JSON 配置
  └─ 点击"应用配置并导出 PAG"
       ↓
       发送到 Flask 服务器 (localhost:5000)
       ├─ 原始 PAG 文件 (二进制)
       └─ JSON 配置（包含 base64 图片）
            ↓
       Python libpag 处理
       ├─ 加载 PAG 模板
       ├─ 应用文本修改
       ├─ 应用图片修改（解码 base64）
       └─ 保存新 PAG 文件
            ↓
       浏览器下载新 PAG 文件
```

### 数据格式

**发送到服务器的数据：**

```javascript
FormData {
  pagFile: Blob(原始 PAG 文件),
  modifications: JSON.stringify([
    {
      layerIndex: 0,
      type: "text",
      value: "文本内容"
    },
    {
      layerIndex: 1,
      type: "image",
      value: "data:image/jpeg;base64,..." // base64 编码的图片
    }
  ])
}
```

**服务器返回：**

```
Content-Type: application/octet-stream
Content-Disposition: attachment; filename="modified.pag"

[二进制 PAG 文件数据]
```

---

## 🔧 故障排除

### 问题 1: 点击按钮后提示"无法连接到导出服务器"

**原因：** 后端服务器未启动

**解决：**

```bash
# 检查服务器是否运行
curl http://localhost:5000

# 如果没有响应，启动服务器
.\start_pag_export_server.bat

# 或者
python pag_export_server.py
```

### 问题 2: 导出时提示"JSON 格式错误"

**原因：** 手动输入的 JSON 配置有语法错误

**解决：**

1. 使用 JSON 验证工具检查格式
2. 或者使用"导出当前配置"功能生成标准 JSON
3. 确保 JSON 包含 `modifications` 数组

**正确格式：**

```json
{
  "modifications": [
    {
      "layerIndex": 0,
      "type": "text",
      "value": "内容"
    }
  ]
}
```

### 问题 3: 图片没有应用成功

**原因：** JSON 中缺少 `imageData` 字段

**解决：**

1. 在 Web 编辑器中上传图片会自动包含 `imageData`
2. 手动编写时确保包含 base64 数据：

```json
{
  "layerIndex": 1,
  "type": "image",
  "imageData": "data:image/jpeg;base64,/9j/4AAQ..."
}
```

### 问题 4: 服务器报错"未安装 libpag"

**解决：**

```bash
# 安装 libpag（注意：可能需要特定的 Python 版本）
pip install libpag

# 如果安装失败，可能需要预编译的 wheel 文件
# 查看项目文档获取安装指导
```

---

## 📝 与其他工具对比

| 功能 | Web 编辑器 | apply_json_to_pag.py | 批处理脚本 |
|------|-----------|---------------------|-----------|
| 可视化预览 | ✅ | ❌ | ❌ |
| 在线导出 | ✅ | ❌ | ❌ |
| 批量处理 | ❌ | ✅ | ✅ |
| 离线使用 | ❌ | ✅ | ✅ |
| 易用性 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| 灵活性 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

---

## 🎯 最佳实践

### 1. 设计阶段

**使用 Web 编辑器：**

```
目的: 测试模板，确认图层布局
方法:
  1. 上传多个测试 PAG 模板
  2. 尝试修改不同图层
  3. 实时预览效果
  4. 确定最终模板和图层索引
```

### 2. 原型阶段

**Web 编辑器 + JSON 导出：**

```
目的: 创建标准配置样本
方法:
  1. 在 Web 编辑器中完成一个完整案例
  2. 导出 JSON 配置
  3. 作为后续批量生成的模板
```

### 3. 生产阶段

**批量工具：**

```
目的: 大规模生成 PAG 文件
方法:
  1. 使用样本 JSON 配置
  2. 结合 CSV 数据
  3. Python 脚本批量生成
  4. 偶尔需要单独调整时，使用 Web 编辑器
```

---

## 💡 使用技巧

### 技巧 1: 快速测试多个文案

```
1. 准备好 PAG 模板
2. 在 JSON 文本框中准备多个配置（分别复制粘贴）

配置 A:
{
  "modifications": [
    {"layerIndex": 0, "type": "text", "value": "春季促销"}
  ]
}

配置 B:
{
  "modifications": [
    {"layerIndex": 0, "type": "text", "value": "夏季特惠"}
  ]
}

3. 逐个应用并导出，比较效果
```

### 技巧 2: 图片测试

```
1. 在 Web 编辑器中上传测试图片
2. 导出 JSON 配置（自动包含 base64 数据）
3. 保存这个 JSON 作为参考
4. 后续可以替换 imageData 字段测试不同图片
```

### 技巧 3: 版本管理

```
项目结构:
pag_project/
├── template.pag          # 原始模板
├── configs/
│   ├── version1.json     # 第一版配置
│   ├── version2.json     # 第二版配置
│   └── final.json        # 最终版本
└── output/
    ├── version1.pag      # Web 编辑器导出
    ├── version2.pag
    └── final.pag
```

---

## 🎓 学习路径

### 新手

```
1. 阅读本文档
2. 启动服务器: test_pag_editor_full.bat
3. 打开 Web 编辑器
4. 上传样例 PAG 模板
5. 尝试修改文本
6. 点击"应用配置并导出 PAG"
7. 检查生成的文件
```

### 进阶

```
1. 学习 JSON 配置格式
2. 手动编写配置
3. 测试图片替换
4. 导出多个版本
5. 结合批量工具
```

### 专家

```
1. 自定义服务器配置
2. 扩展 Flask API
3. 集成到自动化流程
4. 优化批量生成性能
```

---

## 📚 相关文档

- **JSON_CONFIG_MASTER.md** - JSON 配置完整指南
- **HOW_TO_USE_YOUR_JSON.md** - 针对导出的 JSON 使用说明
- **JSON_QUICK_START.md** - 快速入门
- **PAG_EDITOR_COMPLETE.md** - 编辑器完整功能说明

---

## 🎉 总结

### ✅ 新功能特点

1. **一键操作** - 点击按钮即可生成 PAG
2. **支持 JSON** - 灵活应用配置
3. **实时预览** - 所见即所得
4. **自动下载** - 生成后自动保存

### 🚀 典型工作流

```
上传模板 → 编辑内容 → 应用并导出 → 获得新 PAG
   ↓          ↓           ↓
 可视化     实时预览    一键完成
```

### 🎯 适用场景

- ✅ 快速测试不同内容效果
- ✅ 单个文件快速生成
- ✅ 验证批量配置正确性
- ✅ 原型设计和演示

---

**开始使用：** 运行 `test_pag_editor_full.bat` 启动完整环境

**在线编辑：** http://localhost:8000/pag_template_editor.html

**最后更新：** 2025-11-29  
**版本：** 2.0  
**状态：** ✅ 已完成并可用
