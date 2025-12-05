#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
简单检查 pypag API

检查 PAGImageLayer 类中是否有变换相关的方法
"""

import sys

try:
    # 尝试导入 pypag 或 libpag
    pag = None
    module_name = None
    
    try:
        import pypag as pag
        module_name = 'pypag'
    except ImportError:
        try:
            import libpag as pag
            module_name = 'libpag'
        except ImportError:
            pass
    
    if pag is None:
        raise ImportError("未找到 pypag 或 libpag 模块")
    
    print(f"✅ 成功导入 {module_name}")
    print(f"📦 版本: {getattr(pag, '__version__', '未知')}")
    print(f"📂 路径: {pag.__file__}")
    print()
    
    # 检查是否有 PAGImageLayer
    if hasattr(pag, 'PAGImageLayer'):
        print("✅ 找到 PAGImageLayer 类")
        
        # 列出所有方法
        layer_methods = [x for x in dir(pag.PAGImageLayer) if not x.startswith('_')]
        print(f"\n📋 PAGImageLayer 的所有方法 ({len(layer_methods)} 个):")
        print("-" * 50)
        for method in sorted(layer_methods):
            print(f"  - {method}")
        
        # 检查关键变换方法
        print("\n" + "=" * 50)
        print("🔍 变换相关方法检查:")
        print("=" * 50)
        
        transform_methods = {
            'setPosition': '设置位置',
            'setAnchorPoint': '设置锚点',
            'setScale': '设置缩放',
            'setRotation': '设置旋转',
            'setOpacity': '设置不透明度',
            'setMatrix': '设置矩阵',
            'getMatrix': '获取矩阵',
            'getOriginalAnchorPoint': '获取原始锚点',
            'getOriginalScaleFactor': '获取原始缩放',
            'getOriginalImageBounds': '获取原始边界',
            'getOriginalImageMatrix': '获取原始矩阵',
        }
        
        for method_name, description in transform_methods.items():
            has_method = hasattr(pag.PAGImageLayer, method_name)
            status = "✅" if has_method else "❌"
            print(f"{status} {method_name:<30} - {description}")
    else:
        print("❌ 未找到 PAGImageLayer 类")
        print("\n可用的类:")
        for item in dir(pag):
            if item[0].isupper() and not item.startswith('_'):
                print(f"  - {item}")
    
except ImportError as e:
    print(f"❌ 导入 libpag 失败: {e}")
    print(f"\nPython 路径:")
    for path in sys.path:
        print(f"  - {path}")
except Exception as e:
    print(f"❌ 发生错误: {e}")
    import traceback
    traceback.print_exc()
