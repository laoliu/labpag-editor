"""
快速测试 libpag 中的图层变换 API
"""
import sys
import os

# 添加项目根目录到路径
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.insert(0, project_root)

try:
    import libpag
    print("✅ libpag 导入成功")
    print(f"版本: {libpag.__version__ if hasattr(libpag, '__version__') else '未知'}")
except ImportError as e:
    print(f"❌ 无法导入 libpag: {e}")
    sys.exit(1)

print("\n" + "="*60)
print("检查 PAGImageLayer 的方法")
print("="*60)

if hasattr(libpag, 'PAGImageLayer'):
    # 获取所有方法
    all_methods = [x for x in dir(libpag.PAGImageLayer) if not x.startswith('_')]
    
    # 检查关键的变换方法
    transform_methods = {
        '位置': ['setPosition', 'getPosition', 'position'],
        '锚点': ['setAnchorPoint', 'getAnchorPoint', 'anchorPoint', 'getOriginalAnchorPoint'],
        '缩放': ['setScale', 'getScale', 'scale'],
        '旋转': ['setRotation', 'getRotation', 'rotation'],
        '矩阵': ['setMatrix', 'getMatrix', 'matrix'],
        '变换': ['setTransform', 'getTransform', 'transform'],
    }
    
    print("\n📊 变换相关方法检查:")
    for category, methods in transform_methods.items():
        print(f"\n{category}:")
        for method in methods:
            exists = method in all_methods
            status = "✅" if exists else "❌"
            print(f"  {status} {method}")
    
    print(f"\n📋 所有可用方法 ({len(all_methods)} 个):")
    for i, method in enumerate(sorted(all_methods), 1):
        print(f"  {i}. {method}")
else:
    print("❌ PAGImageLayer 类不存在")

print("\n" + "="*60)
print("完成")
print("="*60)
