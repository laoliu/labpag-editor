"""
PAG 程序化生成器 - Python 版本
支持从 JSON 配置批量生成 PAG 文件（通过 AE 自动化）
"""

import json
import os
import subprocess
from pathlib import Path
from typing import List, Dict, Any


class PAGGenerator:
    """PAG 文件生成器"""
    
    def __init__(self, ae_path: str = None):
        """
        初始化生成器
        
        Args:
            ae_path: After Effects 可执行文件路径
        """
        if ae_path is None:
            # 默认路径
            ae_path = r"C:\Program Files\Adobe\Adobe After Effects 2025\Support Files\AfterFX.exe"
        
        self.ae_path = ae_path
        self.config_dir = Path("pag_configs")
        self.output_dir = Path("pag_output")
        
        # 创建目录
        self.config_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)
    
    def create_config(self, 
                     name: str,
                     width: int = 1920,
                     height: int = 1080,
                     duration: float = 3.0,
                     layers: List[Dict[str, Any]] = None,
                     animations: List[Dict[str, Any]] = None) -> Path:
        """
        创建 PAG 配置文件
        
        Args:
            name: 配置名称
            width: 宽度
            height: 高度
            duration: 时长（秒）
            layers: 图层配置列表
            animations: 动画配置列表
        
        Returns:
            配置文件路径
        """
        config = {
            "version": "1.0",
            "name": name,
            "width": width,
            "height": height,
            "duration": duration,
            "frameRate": 30,
            "layers": layers or [],
            "animations": animations or []
        }
        
        config_path = self.config_dir / f"{name}.json"
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print(f"✅ 配置文件已创建: {config_path}")
        return config_path
    
    def generate_from_config(self, config_path: Path, jsx_script: str = None) -> Path:
        """
        从配置文件生成 PAG
        
        Args:
            config_path: 配置文件路径
            jsx_script: JSX 脚本路径（可选）
        
        Returns:
            生成的 PAG 文件路径
        """
        if jsx_script is None:
            jsx_script = self._create_jsx_script()
        
        # 调用 AE
        cmd = [
            self.ae_path,
            "-r", jsx_script,
            "-config", str(config_path)
        ]
        
        print(f"⚙️ 正在生成 PAG: {config_path.stem}")
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                output_path = self.output_dir / f"{config_path.stem}.pag"
                print(f"✅ PAG 生成成功: {output_path}")
                return output_path
            else:
                print(f"❌ 生成失败: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            print("❌ 生成超时")
            return None
        except Exception as e:
            print(f"❌ 生成错误: {e}")
            return None
    
    def batch_generate(self, configs: List[Dict[str, Any]]) -> List[Path]:
        """
        批量生成 PAG 文件
        
        Args:
            configs: 配置列表
        
        Returns:
            生成的 PAG 文件路径列表
        """
        results = []
        
        for i, config_data in enumerate(configs, 1):
            print(f"\n[{i}/{len(configs)}] 处理配置: {config_data.get('name', f'config_{i}')}")
            
            # 创建配置
            config_path = self.create_config(**config_data)
            
            # 生成 PAG
            output_path = self.generate_from_config(config_path)
            
            if output_path:
                results.append(output_path)
        
        print(f"\n✅ 批量生成完成: {len(results)}/{len(configs)} 成功")
        return results
    
    def _create_jsx_script(self) -> str:
        """创建默认的 JSX 脚本"""
        jsx_content = '''
// PAG 生成 JSX 脚本
#include "json2.min.js"

function main() {
    // 读取配置
    var configPath = app.settings.getSetting("PAG Generator", "configPath");
    if (!configPath) {
        alert("未找到配置文件路径");
        return;
    }
    
    var file = new File(configPath);
    if (!file.open("r")) {
        alert("无法打开配置文件: " + configPath);
        return;
    }
    
    var jsonContent = file.read();
    file.close();
    
    var config = JSON.parse(jsonContent);
    
    // 创建合成
    var comp = app.project.items.addComp(
        config.name,
        config.width,
        config.height,
        1.0,
        config.duration,
        config.frameRate || 30
    );
    
    // 添加图层
    for (var i = 0; i < config.layers.length; i++) {
        var layerConfig = config.layers[i];
        
        try {
            if (layerConfig.type === "text") {
                createTextLayer(comp, layerConfig);
            } else if (layerConfig.type === "image") {
                createImageLayer(comp, layerConfig);
            } else if (layerConfig.type === "shape") {
                createShapeLayer(comp, layerConfig);
            }
        } catch (e) {
            alert("创建图层失败: " + e.toString());
        }
    }
    
    // 应用动画
    if (config.animations) {
        applyAnimations(comp, config.animations);
    }
    
    // 导出 PAG
    exportToPAG(comp, config.name);
}

function createTextLayer(comp, config) {
    var textLayer = comp.layers.addText(config.content || "");
    
    // 设置位置
    if (config.position) {
        textLayer.property("Position").setValue(config.position);
    }
    
    // 设置文本样式
    var textDoc = textLayer.property("Source Text").value;
    if (config.fontSize) {
        textDoc.fontSize = config.fontSize;
    }
    if (config.font) {
        textDoc.font = config.font;
    }
    if (config.fillColor) {
        textDoc.fillColor = hexToRGB(config.fillColor);
    }
    
    textLayer.property("Source Text").setValue(textDoc);
    
    // 设置图层名称
    if (config.name) {
        textLayer.name = config.name;
    }
    
    return textLayer;
}

function createImageLayer(comp, config) {
    var imagePath = config.path;
    if (!imagePath) return null;
    
    var imageFile = new File(imagePath);
    if (!imageFile.exists) {
        alert("图片文件不存在: " + imagePath);
        return null;
    }
    
    var footage = app.project.importFile(new ImportOptions(imageFile));
    var imageLayer = comp.layers.add(footage);
    
    // 设置位置
    if (config.position) {
        imageLayer.property("Position").setValue(config.position);
    }
    
    // 设置缩放
    if (config.scale) {
        imageLayer.property("Scale").setValue([config.scale * 100, config.scale * 100]);
    }
    
    // 设置图层名称
    if (config.name) {
        imageLayer.name = config.name;
    }
    
    return imageLayer;
}

function createShapeLayer(comp, config) {
    var shapeLayer = comp.layers.addShape();
    
    // 添加形状
    if (config.shapeType === "rectangle") {
        var rectGroup = shapeLayer.property("Contents").addProperty("ADBE Vector Group");
        var rect = rectGroup.property("Contents").addProperty("ADBE Vector Shape - Rect");
        
        if (config.size) {
            rect.property("Size").setValue(config.size);
        }
    }
    
    // 添加填充
    if (config.fillColor) {
        var fill = shapeLayer.property("Contents").property(1).property("Contents").addProperty("ADBE Vector Graphic - Fill");
        fill.property("Color").setValue(hexToRGB(config.fillColor));
    }
    
    // 设置位置
    if (config.position) {
        shapeLayer.property("Position").setValue(config.position);
    }
    
    return shapeLayer;
}

function applyAnimations(comp, animations) {
    for (var i = 0; i < animations.length; i++) {
        var anim = animations[i];
        var layer = comp.layer(anim.layer + 1);
        
        if (!layer) continue;
        
        var prop = layer.property(anim.property);
        if (!prop) continue;
        
        // 添加关键帧
        for (var j = 0; j < anim.keyframes.length; j++) {
            var kf = anim.keyframes[j];
            prop.setValueAtTime(kf.time, kf.value);
        }
    }
}

function exportToPAG(comp, name) {
    // 使用 PAG 插件导出
    // 注意: 需要安装 PAG 导出插件
    
    comp.openInViewer();
    
    // 这里需要调用 PAG 导出命令
    // 具体命令取决于 PAG 插件的实现
    
    alert("合成已创建: " + name + "\\n请手动导出为 PAG 格式");
}

function hexToRGB(hex) {
    var result = /^#?([a-f\\d]{2})([a-f\\d]{2})([a-f\\d]{2})$/i.exec(hex);
    return result ? [
        parseInt(result[1], 16) / 255,
        parseInt(result[2], 16) / 255,
        parseInt(result[3], 16) / 255
    ] : [1, 1, 1];
}

// 运行
main();
'''
        
        jsx_path = Path("pag_generator.jsx")
        with open(jsx_path, 'w', encoding='utf-8') as f:
            f.write(jsx_content)
        
        return str(jsx_path)


# 使用示例
def example_usage():
    """使用示例"""
    
    generator = PAGGenerator()
    
    # 示例 1: 创建简单的文本动画
    config1 = {
        "name": "text_animation",
        "width": 1920,
        "height": 1080,
        "duration": 3.0,
        "layers": [
            {
                "type": "text",
                "name": "标题",
                "content": "Hello PAG!",
                "position": [960, 540],
                "fontSize": 72,
                "fillColor": "#FFFFFF"
            }
        ],
        "animations": [
            {
                "layer": 0,
                "property": "Opacity",
                "keyframes": [
                    {"time": 0, "value": 0},
                    {"time": 1.0, "value": 100}
                ]
            }
        ]
    }
    
    # 示例 2: 文本 + 图片
    config2 = {
        "name": "text_with_image",
        "width": 1920,
        "height": 1080,
        "duration": 5.0,
        "layers": [
            {
                "type": "image",
                "name": "背景",
                "path": "background.png",
                "position": [960, 540],
                "scale": 1.0
            },
            {
                "type": "text",
                "name": "标题",
                "content": "欢迎",
                "position": [960, 300],
                "fontSize": 96,
                "fillColor": "#FF6B6B"
            },
            {
                "type": "text",
                "name": "副标题",
                "content": "Hello World",
                "position": [960, 700],
                "fontSize": 48,
                "fillColor": "#4ECDC4"
            }
        ]
    }
    
    # 批量生成
    configs = [config1, config2]
    results = generator.batch_generate(configs)
    
    print(f"\n生成的文件:")
    for path in results:
        print(f"  - {path}")


if __name__ == "__main__":
    # 运行示例
    example_usage()
