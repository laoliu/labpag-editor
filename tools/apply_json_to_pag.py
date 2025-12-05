"""
从 JSON 配置应用到 PAG 文件

使用方法：
    python apply_json_to_pag.py template.pag config.json output.pag

功能：
    - 读取 Web 编辑器导出的 JSON 配置
    - 应用到 PAG 模板文件
    - 生成修改后的 PAG 文件

示例 JSON 格式：
{
  "modifications": [
    {
      "layerIndex": 0,
      "type": "text",
      "value": "新文本内容"
    },
    {
      "layerIndex": 1,
      "type": "image",
      "value": "photo.jpg"
    }
  ]
}
"""

import json
import sys
import os
from pathlib import Path

def apply_json_to_pag(pag_template, json_config, output_path, images_dir=None):
    """
    应用 JSON 配置到 PAG 文件
    
    Args:
        pag_template: PAG 模板文件路径
        json_config: JSON 配置文件路径
        output_path: 输出 PAG 文件路径
        images_dir: 图片文件目录（可选）
    """
    try:
        import libpag
    except ImportError:
        print("❌ 错误：未安装 libpag")
        print("请运行: pip install libpag")
        return False
    
    # 读取 JSON 配置
    print(f"📖 读取配置: {json_config}")
    with open(json_config, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    modifications = config.get('modifications', [])
    if not modifications:
        print("⚠️ 警告：配置中没有修改项")
        return False
    
    print(f"✅ 找到 {len(modifications)} 项修改")
    
    # 加载 PAG 模板
    print(f"📂 加载模板: {pag_template}")
    pag = libpag.PAGFile.Load(pag_template)
    
    if not pag:
        print(f"❌ 错误：无法加载 PAG 文件: {pag_template}")
        return False
    
    print(f"✅ PAG 加载成功 ({pag.width()}x{pag.height()})")
    
    # 应用修改
    success_count = 0
    error_count = 0
    
    for i, mod in enumerate(modifications):
        layer_index = mod.get('layerIndex')
        mod_type = mod.get('type')
        value = mod.get('value')
        image_data = mod.get('imageData')  # base64 数据
        
        print(f"\n[{i+1}/{len(modifications)}] 处理图层 {layer_index} ({mod_type})")
        
        try:
            if mod_type == 'text':
                # 替换文本
                text_data = pag.getTextData(layer_index)
                if text_data:
                    text_data.text = value
                    pag.replaceText(layer_index, text_data)
                    print(f"  ✅ 文本已更新: {value[:30]}...")
                    success_count += 1
                else:
                    print(f"  ⚠️ 无法获取文本数据")
                    error_count += 1
            
            elif mod_type == 'image':
                # 替换图片
                image_path = None
                
                # 方法 1: 使用 base64 数据（如果有）
                if image_data and image_data.startswith('data:image'):
                    import base64
                    import tempfile
                    
                    # 提取 base64 数据
                    base64_data = image_data.split(',')[1]
                    image_bytes = base64.b64decode(base64_data)
                    
                    # 保存到临时文件
                    ext = '.png'
                    if 'jpeg' in image_data or 'jpg' in image_data:
                        ext = '.jpg'
                    elif 'webp' in image_data:
                        ext = '.webp'
                    
                    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
                    temp_file.write(image_bytes)
                    temp_file.close()
                    image_path = temp_file.name
                    print(f"  📦 使用 base64 图片数据")
                
                # 方法 2: 使用文件路径
                elif value:
                    # 尝试多个路径
                    possible_paths = [
                        value,  # 直接路径
                        os.path.join(os.path.dirname(json_config), value),  # 相对于配置文件
                        os.path.join(images_dir or '.', value) if images_dir else None,  # 指定的图片目录
                    ]
                    
                    for path in possible_paths:
                        if path and os.path.exists(path):
                            image_path = path
                            print(f"  📁 找到图片: {os.path.basename(path)}")
                            break
                
                if image_path:
                    image = libpag.PAGImage.FromPath(image_path)
                    if image:
                        pag.replaceImage(layer_index, image)
                        print(f"  ✅ 图片已更新")
                        success_count += 1
                        
                        # 清理临时文件
                        if image_data:
                            os.unlink(image_path)
                    else:
                        print(f"  ❌ 无法加载图片: {image_path}")
                        error_count += 1
                else:
                    print(f"  ⚠️ 找不到图片文件: {value}")
                    print(f"     请确保图片文件存在，或配置包含 imageData")
                    error_count += 1
        
        except Exception as e:
            print(f"  ❌ 错误: {e}")
            error_count += 1
    
    # 保存结果
    print(f"\n💾 保存文件: {output_path}")
    
    # 确保输出目录存在
    os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
    
    if pag.save(output_path):
        print(f"✅ 成功！")
        print(f"\n📊 统计:")
        print(f"   成功: {success_count}")
        print(f"   失败: {error_count}")
        print(f"   总计: {len(modifications)}")
        return True
    else:
        print(f"❌ 保存失败")
        return False


def main():
    """命令行入口"""
    if len(sys.argv) < 4:
        print("""
╔══════════════════════════════════════════════════════════╗
║  从 JSON 配置应用到 PAG 文件                              ║
╚══════════════════════════════════════════════════════════╝

使用方法:
    python apply_json_to_pag.py <模板.pag> <配置.json> <输出.pag> [图片目录]

参数:
    模板.pag   - PAG 模板文件路径
    配置.json  - Web 编辑器导出的 JSON 配置
    输出.pag   - 生成的 PAG 文件路径
    图片目录   - 图片文件所在目录（可选）

示例:
    # 基本用法
    python apply_json_to_pag.py template.pag config.json output.pag
    
    # 指定图片目录
    python apply_json_to_pag.py template.pag config.json output.pag ./images
    
    # 批量生成
    python apply_json_to_pag.py namecard.pag zhang_config.json zhang.pag
    python apply_json_to_pag.py namecard.pag li_config.json li.pag

JSON 配置格式:
    {
      "modifications": [
        {
          "layerIndex": 0,
          "type": "text",
          "value": "新文本"
        },
        {
          "layerIndex": 1,
          "type": "image",
          "value": "photo.jpg",
          "imageData": "data:image/png;base64,..."  // 可选
        }
      ]
    }

提示:
    - 如果 JSON 包含 imageData (base64)，会优先使用
    - 如果只有 value (文件名)，会在以下位置查找:
      1. 配置文件所在目录
      2. 指定的图片目录
      3. 当前工作目录
        """)
        sys.exit(1)
    
    pag_template = sys.argv[1]
    json_config = sys.argv[2]
    output_path = sys.argv[3]
    images_dir = sys.argv[4] if len(sys.argv) > 4 else None
    
    # 验证输入文件
    if not os.path.exists(pag_template):
        print(f"❌ 错误：模板文件不存在: {pag_template}")
        sys.exit(1)
    
    if not os.path.exists(json_config):
        print(f"❌ 错误：配置文件不存在: {json_config}")
        sys.exit(1)
    
    if images_dir and not os.path.exists(images_dir):
        print(f"⚠️ 警告：图片目录不存在: {images_dir}")
    
    # 执行转换
    success = apply_json_to_pag(pag_template, json_config, output_path, images_dir)
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
