"""
PAG 导出服务器 - 处理 Web 编辑器的导出请求

功能：
1. 接收原始 PAG 文件和修改配置
2. 使用服务端 PAG SDK 应用修改
3. 返回修改后的 PAG 文件

新版本说明：
    使用新编译的 pypag (H:\work\python\libpag\python\venv\Lib\site-packages\pypag.pyd)
    ✅ 支持 save() 方法，可以保存 .pag 文件

使用方法：
    python pag_export_server.py

然后在浏览器中访问：
    http://localhost:5000/

API 端点：
    POST /api/export-pag
        - 参数：原始 PAG 文件 + JSON 配置
        - 返回：修改后的 PAG 文件
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import io
import json
import base64
from pathlib import Path
import tempfile
import os

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 配置 Flask 允许大文件上传
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB
app.config['JSON_AS_ASCII'] = False  # 支持中文

# 注意：需要安装 PAG Python SDK
# pip install libpag

# 优先使用项目本地的 pypag.pyd（包含 Matrix.getTranslateX/Y 等方法）
import sys
from pathlib import Path

# 获取项目根目录
project_root = Path(__file__).parent.parent
pypag_path = str(project_root / 'pylib')

if pypag_path not in sys.path:
    sys.path.insert(0, pypag_path)
    print(f"✅ 添加本地 pypag 路径到 sys.path: {pypag_path}")

PAG_AVAILABLE = False
PAG_MODULE = None
IMPORT_ERROR_MSG = ""

try:
    import pypag as libpag
    PAG_AVAILABLE = True
    PAG_MODULE = libpag
    print("✅ 成功导入 pypag (作为 libpag)")
    print(f"   模块位置: {libpag.__file__ if hasattr(libpag, '__file__') else '内置模块'}")
    
    # 验证 Matrix API
    if hasattr(libpag, 'Matrix'):
        test_matrix = libpag.Matrix.MakeTrans(100, 200)
        has_new_api = hasattr(test_matrix, 'getTranslateX')
        print(f"   Matrix API 状态: {'✅ 新版 (支持 getTranslateX/Y)' if has_new_api else '⚠️ 旧版 (不支持 getTranslateX/Y)'}")
        if has_new_api:
            print(f"   测试 Matrix.MakeTrans(100, 200): X={test_matrix.getTranslateX()}, Y={test_matrix.getTranslateY()}")
except ImportError as e1:
    try:
        import libpag
        PAG_AVAILABLE = True
        PAG_MODULE = libpag
        print("✅ 成功导入 libpag (系统安装版)")
        print(f"   ⚠️ 警告: 系统版本可能不支持新的 Matrix API")
    except ImportError as e2:
        PAG_AVAILABLE = False
        IMPORT_ERROR_MSG = f"pypag: {str(e1)}, libpag: {str(e2)}"
        print("⚠️ 警告：未安装 libpag 或 pypag，将使用模拟模式")
        print(f"   详细错误: {IMPORT_ERROR_MSG}")


def apply_transforms_to_layers(pag, modifications):
    """
    应用变换到图层（运行时应用，需要在渲染前调用）
    
    Args:
        pag: PAG 文件对象
        modifications: 修改配置列表
    
    Returns:
        int: 应用的变换数量
    """
    if not PAG_AVAILABLE:
        return 0
    
    applied_count = 0
    
    for mod in modifications:
        if mod.get('type') != 'imageTransform':
            continue
        
        layer_index = mod.get('layerIndex', mod.get('editableIndex', 0))
        transform = mod.get('transform', {})
        
        try:
            # 获取对应的图层
            if hasattr(libpag, 'LayerType') and hasattr(libpag.LayerType, 'Image'):
                layers = pag.getLayersByEditableIndex(layer_index, libpag.LayerType.Image)
                
                if layers and len(layers) > 0:
                    layer = layers[0]
                    
                    # 提取变换参数
                    position = transform.get('position', {})
                    anchor_point = transform.get('anchorPoint', {})
                    scale = transform.get('scale', {})
                    rotation = transform.get('rotation', 0)
                    opacity = transform.get('opacity', 1)
                    
                    # 应用位置
                    if position:
                        try:
                            layer.setPosition(position.get('x', 0), position.get('y', 0))
                        except Exception as e:
                            print(f"[DEBUG] ⚠️ setPosition 失败: {e}")
                    
                    # 应用锚点
                    if anchor_point:
                        try:
                            layer.setAnchorPoint(anchor_point.get('x', 0), anchor_point.get('y', 0))
                        except Exception as e:
                            print(f"[DEBUG] ⚠️ setAnchorPoint 失败: {e}")
                    
                    # 应用缩放
                    if scale:
                        try:
                            layer.setScale(scale.get('x', 1), scale.get('y', 1))
                        except Exception as e:
                            print(f"[DEBUG] ⚠️ setScale 失败: {e}")
                    
                    # 应用旋转
                    if rotation != 0:
                        try:
                            layer.setRotation(rotation)
                        except Exception as e:
                            print(f"[DEBUG] ⚠️ setRotation 失败: {e}")
                    
                    # 应用不透明度
                    if opacity != 1:
                        try:
                            alpha_value = int(opacity * 255)
                            layer.setAlpha(alpha_value)
                        except Exception as e:
                            print(f"[DEBUG] ⚠️ setAlpha 失败: {e}")
                    
                    applied_count += 1
        
        except Exception as e:
            print(f"[ERROR] 应用变换失败 - 图层 {layer_index}: {str(e)}")
    
    return applied_count


@app.route('/')
def index():
    """API 文档页面"""
    return """
    <html>
    <head><title>PAG 导出服务器</title></head>
    <body style="font-family: Arial; padding: 40px; max-width: 800px; margin: 0 auto;">
        <h1>🚀 PAG 导出服务器</h1>
        <p>状态: <strong style="color: green;">运行中</strong></p>
        <p>PAG SDK: <strong>{status}</strong></p>
        
        <h2>📋 API 端点</h2>
        <ul>
            <li><code>POST /api/export-pag</code> - 导出修改后的 PAG 文件</li>
            <li><code>GET /api/health</code> - 健康检查</li>
        </ul>
        
        <h2>🔧 使用方法</h2>
        <pre style="background: #f5f5f5; padding: 15px; border-radius: 5px;">
// JavaScript 示例
const formData = new FormData();
formData.append('pagFile', pagFileBlob);
formData.append('modifications', JSON.stringify(modifications));

fetch('http://localhost:5000/api/export-pag', {{
    method: 'POST',
    body: formData
}})
.then(res => res.blob())
.then(blob => {{
    // 下载文件
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'modified.pag';
    a.click();
}});
        </pre>
        
        <h2>📦 依赖安装</h2>
        <pre style="background: #f5f5f5; padding: 15px; border-radius: 5px;">
pip install flask flask-cors libpag
        </pre>
    </body>
    </html>
    """.format(status="✅ 已安装" if PAG_AVAILABLE else "❌ 未安装")


@app.route('/api/health')
def health():
    """健康检查"""
    return jsonify({
        'status': 'ok',
        'pag_available': PAG_AVAILABLE
    })


@app.route('/api/debug-matrix')
def debug_matrix():
    """调试 Matrix API"""
    try:
        if not PAG_AVAILABLE:
            return jsonify({'error': 'PAG SDK 未安装'}), 500
        
        # 检查 Matrix 类是否存在
        matrix_info = {
            'module_file': libpag.__file__ if hasattr(libpag, '__file__') else 'built-in',
            'has_Matrix': hasattr(libpag, 'Matrix'),
        }
        
        if hasattr(libpag, 'Matrix'):
            # 创建一个测试 Matrix
            try:
                test_matrix = libpag.Matrix()
                matrix_methods = [m for m in dir(test_matrix) if not m.startswith('_')]
                matrix_info['matrix_methods'] = matrix_methods
                
                # 测试 MakeTrans
                if hasattr(libpag.Matrix, 'MakeTrans'):
                    trans_matrix = libpag.Matrix.MakeTrans(78.0, 104.0)
                    matrix_info['test_MakeTrans'] = {
                        'created': True,
                        'str': str(trans_matrix),
                        'repr': repr(trans_matrix) if hasattr(trans_matrix, '__repr__') else 'N/A'
                    }
                    
                    # 测试读取方法
                    if hasattr(trans_matrix, 'getTranslateX'):
                        matrix_info['test_MakeTrans']['translateX'] = trans_matrix.getTranslateX()
                        matrix_info['test_MakeTrans']['translateY'] = trans_matrix.getTranslateY()
                    
            except Exception as e:
                matrix_info['matrix_test_error'] = str(e)
        
        return jsonify(matrix_info)
    
    except Exception as e:
        import traceback
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


@app.route('/api/analyze-layers', methods=['POST'])
def analyze_layers():
    """
    分析 PAG 文件的图层详细信息
    
    请求参数：
        - pagFile: PAG 文件（multipart/form-data）
    
    返回：
        - JSON 包含所有图层的详细信息（位置、尺寸、变换等）
    """
    try:
        # 检查是否安装了 PAG SDK
        if not PAG_AVAILABLE:
            return jsonify({
                'error': 'PAG SDK 未安装',
                'message': '请运行: pip install libpag'
            }), 500
        
        # 获取上传的文件
        if 'pagFile' not in request.files:
            return jsonify({'error': '缺少 PAG 文件'}), 400
        
        pag_file = request.files['pagFile']
        
        # 读取 PAG 文件到临时文件
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pag') as temp_input:
            pag_file.save(temp_input.name)
            temp_input_path = temp_input.name
        
        try:
            # 加载 PAG 文件
            pag = libpag.PAGFile.Load(temp_input_path)
            
            if not pag:
                return jsonify({'error': '无法加载 PAG 文件'}), 400
            
            # 收集基本信息
            file_info = {
                'width': pag.width(),
                'height': pag.height(),
                'duration': pag.duration() / 1000000,  # 转换为秒
                'frameRate': pag.frameRate(),
                'numImages': pag.numImages(),
                'numTexts': pag.numTexts()
            }
            
            # 收集图片图层信息
            image_layers = []
            if hasattr(libpag, 'LayerType') and hasattr(libpag.LayerType, 'Image'):
                try:
                    image_indices = pag.getEditableIndices(libpag.LayerType.Image)
                    
                    for idx in image_indices:
                        layer_info = {
                            'index': idx,
                            'type': 'image'
                        }
                        
                        # 获取图层对象
                        try:
                            layers = pag.getLayersByEditableIndex(idx, libpag.LayerType.Image)
                            if layers and len(layers) > 0:
                                layer = layers[0]
                                
                                # 图层名称
                                if hasattr(layer, 'layerName'):
                                    layer_info['name'] = layer.layerName()
                                
                                # ✅ 使用 getTotalMatrix() 获取图层的完整变换矩阵（包括父图层变换）
                                if hasattr(layer, 'getTotalMatrix'):
                                    try:
                                        matrix = layer.getTotalMatrix()
                                        
                                        # 使用正确的 Matrix API 获取变换信息
                                        if hasattr(matrix, 'getTranslateX') and hasattr(matrix, 'getTranslateY'):
                                            pos_x = matrix.getTranslateX()
                                            pos_y = matrix.getTranslateY()
                                            
                                            layer_info['position'] = {
                                                'x': float(pos_x),
                                                'y': float(pos_y)
                                            }
                                            
                                            # 同时获取其他变换信息
                                            layer_info['matrix_values'] = {
                                                'translateX': float(pos_x),
                                                'translateY': float(pos_y),
                                                'scaleX': float(matrix.getScaleX()) if hasattr(matrix, 'getScaleX') else 1.0,
                                                'scaleY': float(matrix.getScaleY()) if hasattr(matrix, 'getScaleY') else 1.0,
                                                'skewX': float(matrix.getSkewX()) if hasattr(matrix, 'getSkewX') else 0.0,
                                                'skewY': float(matrix.getSkewY()) if hasattr(matrix, 'getSkewY') else 0.0,
                                            }
                                            
                                            print(f"[DEBUG] ✅ 从 getTotalMatrix 获取位置: ({pos_x}, {pos_y})")
                                            print(f"[DEBUG] Matrix 详情: {layer_info['matrix_values']}")
                                        else:
                                            print(f"[DEBUG] ⚠️ Matrix 没有 getTranslateX/Y 方法")
                                        
                                    except Exception as e:
                                        layer_info['matrix_error'] = str(e)
                                        import traceback
                                        print(f"[DEBUG] getTotalMatrix 解析错误: {traceback.format_exc()}")
                                
                                # 🔄 备用方案：尝试 getOriginalImageMatrix
                                elif hasattr(layer, 'getOriginalImageMatrix'):
                                    try:
                                        matrix = layer.getOriginalImageMatrix()
                                        
                                        if hasattr(matrix, 'getTranslateX') and hasattr(matrix, 'getTranslateY'):
                                            pos_x = matrix.getTranslateX()
                                            pos_y = matrix.getTranslateY()
                                            
                                            layer_info['position'] = {
                                                'x': float(pos_x),
                                                'y': float(pos_y)
                                            }
                                            layer_info['matrix_values'] = {
                                                'translateX': float(pos_x),
                                                'translateY': float(pos_y),
                                                'scaleX': float(matrix.getScaleX()) if hasattr(matrix, 'getScaleX') else 1.0,
                                                'scaleY': float(matrix.getScaleY()) if hasattr(matrix, 'getScaleY') else 1.0,
                                            }
                                            print(f"[DEBUG] ⚠️ 使用 getOriginalImageMatrix (备用): ({pos_x}, {pos_y})")
                                        
                                    except Exception as e:
                                        layer_info['matrix_error'] = str(e)
                                
                                if hasattr(layer, 'getOriginalImageBounds'):
                                    try:
                                        bounds = layer.getOriginalImageBounds()
                                        # Bounds 提供尺寸信息，但 left/top 通常是 0
                                        # 真实位置来自 Matrix 的 tx/ty
                                        layer_info['bounds'] = {
                                            'left': layer_info.get('position', {}).get('x', 0),  # 使用 Matrix 的 tx
                                            'top': layer_info.get('position', {}).get('y', 0),   # 使用 Matrix 的 ty
                                            'right': (layer_info.get('position', {}).get('x', 0) + 
                                                     (bounds.width() if hasattr(bounds, 'width') else 0)),
                                            'bottom': (layer_info.get('position', {}).get('y', 0) + 
                                                      (bounds.height() if hasattr(bounds, 'height') else 0)),
                                            'width': bounds.width() if hasattr(bounds, 'width') else None,
                                            'height': bounds.height() if hasattr(bounds, 'height') else None,
                                        }
                                    except Exception as e:
                                        layer_info['bounds_error'] = str(e)
                                
                                if hasattr(layer, 'getOriginalScaleFactor'):
                                    try:
                                        scale = layer.getOriginalScaleFactor()
                                        layer_info['scaleFactor'] = str(scale)
                                    except Exception as e:
                                        layer_info['scaleFactor_error'] = str(e)
                                
                                if hasattr(layer, 'getOriginalAnchorPoint'):
                                    try:
                                        anchor = layer.getOriginalAnchorPoint()
                                        # 尝试转换为坐标
                                        if hasattr(anchor, 'x') and hasattr(anchor, 'y'):
                                            layer_info['anchorPoint'] = {
                                                'x': anchor.x,
                                                'y': anchor.y
                                            }
                                        else:
                                            layer_info['anchorPoint'] = str(anchor)
                                    except Exception as e:
                                        layer_info['anchorPoint_error'] = str(e)
                                
                                # 🆕 尝试获取图层的图片（如果已被替换）
                                if hasattr(layer, 'getReplacedImage'):
                                    try:
                                        replaced_image = layer.getReplacedImage()
                                        if replaced_image:
                                            # 尝试导出为 base64（如果 API 支持）
                                            # 注意：pypag 可能不直接支持导出为图片数据
                                            # 这里我们标记图层已有替换图片
                                            layer_info['hasReplacedImage'] = True
                                        else:
                                            layer_info['hasReplacedImage'] = False
                                    except Exception as e:
                                        layer_info['hasReplacedImage'] = False
                                
                        except Exception as e:
                            layer_info['error'] = str(e)
                        
                        image_layers.append(layer_info)
                        
                except Exception as e:
                    print(f"[ERROR] 获取图片图层信息失败: {e}")
            
            # 收集文本图层信息
            text_layers = []
            for i in range(pag.numTexts()):
                try:
                    text_data = pag.getTextData(i)
                    layer_info = {
                        'index': i,
                        'type': 'text',
                        'text': text_data.text if hasattr(text_data, 'text') else '',
                        'fontFamily': text_data.fontFamily if hasattr(text_data, 'fontFamily') else None,
                        'fontSize': text_data.fontSize if hasattr(text_data, 'fontSize') else None,
                    }
                    text_layers.append(layer_info)
                except Exception as e:
                    text_layers.append({
                        'index': i,
                        'type': 'text',
                        'error': str(e)
                    })
            
            # 清理临时文件
            os.unlink(temp_input_path)
            
            return jsonify({
                'success': True,
                'fileInfo': file_info,
                'imageLayers': image_layers,
                'textLayers': text_layers
            })
            
        except Exception as e:
            # 清理临时文件
            if os.path.exists(temp_input_path):
                os.unlink(temp_input_path)
            raise e
        
    except Exception as e:
        import traceback
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


@app.route('/api/export-pag', methods=['POST'])
def export_pag():
    """
    导出修改后的 PAG 文件
    
    请求参数：
        - pagFile: 原始 PAG 文件（multipart/form-data）
        - modifications: JSON 字符串，包含修改配置
    
    返回：
        - 修改后的 PAG 文件（application/octet-stream）
    """
    try:
        # 检查是否安装了 PAG SDK
        if not PAG_AVAILABLE:
            return jsonify({
                'error': 'PAG SDK 未安装',
                'message': '请运行: pip install libpag'
            }), 500
        
        # 获取上传的文件
        if 'pagFile' not in request.files:
            return jsonify({'error': '缺少 PAG 文件'}), 400
        
        pag_file = request.files['pagFile']
        modifications_json = request.form.get('modifications', '[]')
        
        # 解析修改配置
        try:
            modifications = json.loads(modifications_json)
        except json.JSONDecodeError:
            return jsonify({'error': 'modifications 必须是有效的 JSON'}), 400
        
        print(f"[DEBUG] 收到 {len(modifications)} 个修改项")
        print(f"[DEBUG] FormData 字段: {list(request.files.keys())}")
        
        # 读取 PAG 文件到临时文件
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pag') as temp_input:
            pag_file.save(temp_input.name)
            temp_input_path = temp_input.name
        
        # 创建临时输出文件
        temp_output = tempfile.NamedTemporaryFile(delete=False, suffix='.pag')
        temp_output_path = temp_output.name
        temp_output.close()
        
        try:
            # 加载 PAG 文件
            pag = libpag.PAGFile.Load(temp_input_path)
            
            if not pag:
                return jsonify({'error': '无法加载 PAG 文件'}), 400
            
            print(f"[DEBUG] PAG 文件加载成功")
            print(f"[DEBUG] - 图片层数量: {pag.numImages()}")
            print(f"[DEBUG] - 文本层数量: {pag.numTexts()}")
            
            # 尝试获取可编辑的图片索引
            try:
                # 检查 LayerType 是否存在
                if hasattr(libpag, 'LayerType') and hasattr(libpag.LayerType, 'Image'):
                    image_editable_indices = pag.getEditableIndices(libpag.LayerType.Image)
                    print(f"[DEBUG] - 可编辑图片索引 (Image类型): {image_editable_indices}")
                else:
                    print(f"[DEBUG] - LayerType.Image 不可用，跳过索引检查")
            except Exception as e:
                print(f"[DEBUG] - 获取可编辑索引失败: {e}")
                print(f"[DEBUG] - 将直接使用 layerIndex 作为 editableImageIndex")
            
            # 应用修改
            for mod in modifications:
                layer_index = mod.get('layerIndex')
                mod_type = mod.get('type')
                value = mod.get('value')
                
                if mod_type == 'text':
                    # 替换文本
                    text_data = pag.getTextData(layer_index)
                    if text_data:
                        text_data.text = value
                        pag.replaceText(layer_index, text_data)
                    print(f"[DEBUG] 替换文本 - 图层 {layer_index}: {value}")
                
                elif mod_type == 'image':
                    # 替换图片
                    # ⚠️ 重要：pypag 的 replaceImage 需要 editableImageIndex，不是 layerIndex！
                    # layer_index 是前端传来的可编辑图片的索引（0, 1, 2...）
                    # 直接作为 editableImageIndex 使用
                    
                    editable_image_index = layer_index
                    
                    # value 可能是：
                    # 1. FormData 字段名（如 "image_0"）- 优先
                    # 2. base64 数据字符串
                    # 3. 文件路径
                    try:
                        # 情况 1：从 FormData 中获取图片文件
                        if value in request.files:
                            image_file = request.files[value]
                            print(f"[DEBUG] 从 FormData 获取图片 - EditableIndex {editable_image_index}: {image_file.filename}")
                            
                            # 保存到临时文件
                            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_img:
                                image_file.save(temp_img.name)
                                temp_img_path = temp_img.name
                            
                            try:
                                # ✨ 使用 libpag 新 API：从图层直接获取原始占位图的变换信息
                                # 先获取原始图层信息
                                original_layers = pag.getLayersByEditableIndex(editable_image_index, libpag.LayerType.Image)
                                print(f"[DEBUG] - 找到 {len(original_layers) if original_layers else 0} 个对应的图层")
                                
                                # 获取原始图片的 matrix 和 scaleMode
                                original_matrix = None
                                original_scale_mode = None
                                layer_name = None
                                
                                if original_layers and len(original_layers) > 0:
                                    original_layer = original_layers[0]
                                    if hasattr(original_layer, 'layerName'):
                                        layer_name = original_layer.layerName()
                                        print(f"[DEBUG] - 原始图层名称: {layer_name}")
                                    
                                    # ✅ 方案 1（优先）：使用 libpag 新 API - 从图层直接获取变换信息
                                    # pypag 实际提供的 API（已实现）：
                                    # - original_layer.getOriginalImageMatrix()  ✅ 获取原始图片矩阵
                                    # - original_layer.getOriginalImageBounds()  ✅ 获取原始图片边界
                                    # - original_layer.getOriginalScaleFactor()  ✅ 获取原始缩放因子
                                    # - original_layer.getOriginalAnchorPoint()  ✅ 获取原始锚点
                                    
                                    # 尝试获取原始图片的 matrix
                                    if hasattr(original_layer, 'getOriginalImageMatrix'):
                                        try:
                                            original_matrix = original_layer.getOriginalImageMatrix()
                                            print(f"[DEBUG] - ✅ 从图层获取原始 matrix: {original_matrix}")
                                        except Exception as e:
                                            print(f"[DEBUG] - ⚠️ getOriginalImageMatrix() 调用失败: {e}")
                                    
                                    # 尝试获取原始图片的边界（可选，用于调试）
                                    if hasattr(original_layer, 'getOriginalImageBounds'):
                                        try:
                                            original_bounds = original_layer.getOriginalImageBounds()
                                            print(f"[DEBUG] - 原始图片边界: {original_bounds}")
                                        except Exception as e:
                                            print(f"[DEBUG] - ⚠️ getOriginalImageBounds() 调用失败: {e}")
                                    
                                    # 注意：pypag 没有提供 getOriginalScaleMode()
                                    # scaleMode 需要从已替换的图片获取，或使用默认值
                                    
                                    # ⚠️ 方案 2（回退）：如果新 API 不可用，从已替换的图片获取（仅第二次替换时有效）
                                    if original_matrix is None and hasattr(original_layer, 'getReplacedImage'):
                                        try:
                                            original_image = original_layer.getReplacedImage()
                                            if original_image:
                                                print(f"[DEBUG] - 回退方案：从已替换图片获取变换信息")
                                                if hasattr(original_image, 'matrix'):
                                                    original_matrix = original_image.matrix()
                                                    print(f"[DEBUG] - 从已替换图片获取 matrix: {original_matrix}")
                                                if hasattr(original_image, 'scaleMode') and original_scale_mode is None:
                                                    original_scale_mode = original_image.scaleMode()
                                                    print(f"[DEBUG] - 从已替换图片获取 scaleMode: {original_scale_mode}")
                                            else:
                                                print(f"[DEBUG] - ⚠️ getReplacedImage() 返回 None（首次替换且新 API 不可用）")
                                        except Exception as e:
                                            print(f"[DEBUG] - 回退方案失败: {e}")
                                
                                # 加载新图片
                                new_image = libpag.PAGImage.FromPath(temp_img_path)
                                if new_image:
                                    print(f"[DEBUG] PAGImage 创建成功 - EditableIndex {editable_image_index}")
                                    print(f"[DEBUG] - 新图片尺寸: {new_image.width()}x{new_image.height()}")
                                    print(f"[DEBUG] - 新图片默认 matrix: {new_image.matrix()}")
                                    print(f"[DEBUG] - 新图片默认 scaleMode: {new_image.scaleMode()}")
                                    
                                    # 🔑 关键：应用原始图层的变换信息到新图片
                                    # ⚠️ 重要：必须先设置 scaleMode，再设置 matrix！
                                    # 因为 setScaleMode 可能会重新计算 matrix
                                    
                                    # 步骤 1：设置 scaleMode
                                    if original_scale_mode is not None:
                                        try:
                                            print(f"[DEBUG] ✨ 应用原始 scaleMode: {original_scale_mode}")
                                            new_image.setScaleMode(original_scale_mode)
                                            print(f"[DEBUG] ✅ ScaleMode 应用成功")
                                        except Exception as e:
                                            print(f"[DEBUG] ⚠️ 应用 scaleMode 失败: {e}")
                                    else:
                                        # 如果没有原始 scaleMode，但有 matrix，就不设置 scaleMode
                                        # 让 matrix 完全控制变换
                                        if original_matrix is None:
                                            # 只有在没有 matrix 的情况下才使用默认 scaleMode
                                            if hasattr(libpag, 'PAGScaleMode') and hasattr(libpag.PAGScaleMode, 'LetterBox'):
                                                try:
                                                    print(f"[DEBUG] ℹ️ 使用默认 scaleMode: LetterBox（保持宽高比）")
                                                    new_image.setScaleMode(libpag.PAGScaleMode.LetterBox)
                                                except Exception as e:
                                                    print(f"[DEBUG] ⚠️ 设置默认 scaleMode 失败: {e}")
                                        else:
                                            print(f"[DEBUG] ℹ️ 跳过 scaleMode 设置（优先使用 matrix）")
                                    
                                    # 步骤 2：设置 matrix（必须在 scaleMode 之后）
                                    if original_matrix is not None:
                                        try:
                                            print(f"[DEBUG] ✨ 应用原始 matrix: {original_matrix}")
                                            new_image.setMatrix(original_matrix)
                                            print(f"[DEBUG] ✅ Matrix 应用成功，新 matrix: {new_image.matrix()}")
                                        except Exception as e:
                                            print(f"[DEBUG] ⚠️ 应用 matrix 失败: {e}")
                                    else:
                                        print(f"[DEBUG] ℹ️ 未获取到原始 matrix，新图片将使用默认变换")
                                    
                                    # 执行替换
                                    print(f"[DEBUG] 执行 replaceImage(editableImageIndex={editable_image_index}, ...)")
                                    result = pag.replaceImage(editable_image_index, new_image)
                                    print(f"[DEBUG] replaceImage 返回值: {result}")
                                    
                                    # 验证替换结果
                                    if original_layers and len(original_layers) > 0 and hasattr(original_layer, 'getReplacedImage'):
                                        try:
                                            # 重用前面已定义的 original_layer 变量，保持一致性
                                            replaced_img = original_layer.getReplacedImage()
                                            print(f"[DEBUG] 替换后 getReplacedImage 类型: {type(replaced_img)} 是否为 None: {replaced_img is None}")
                                        except Exception as e:
                                            print(f"[DEBUG] 替换后 getReplacedImage 调用异常: {e}")
                                    print(f"[DEBUG] 替换后图片层数量: {pag.numImages()}")
                                else:
                                    print(f"[ERROR] PAGImage.FromPath 返回 None - EditableIndex {editable_image_index}")
                            
                            except Exception as e:
                                print(f"[ERROR] 图片替换过程出错: {e}")
                                import traceback
                                traceback.print_exc()
                            
                            # 清理临时文件
                            try:
                                os.unlink(temp_img_path)
                            except:
                                pass
                                pass
                        
                        # 情况 2：base64 数据
                        elif value.startswith('data:image/'):
                            # 处理 base64 图片数据
                            # 格式: data:image/png;base64,iVBORw0KGgo...
                            base64_data = value.split(',', 1)[1] if ',' in value else value
                            image_bytes = base64.b64decode(base64_data)
                            
                            # 保存到临时文件
                            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_img:
                                temp_img.write(image_bytes)
                                temp_img_path = temp_img.name
                            
                            # 加载图片
                            image = libpag.PAGImage.FromPath(temp_img_path)
                            if image:
                                result = pag.replaceImage(layer_index, image)
                                print(f"[DEBUG] 替换图片 - 图层 {layer_index}: base64 数据 ({len(image_bytes)} 字节), 结果: {result}")
                            else:
                                print(f"[ERROR] 无法加载图片 - 图层 {layer_index}")
                            
                            # 清理临时文件
                            try:
                                os.unlink(temp_img_path)
                            except:
                                pass
                                
                        elif os.path.exists(value):
                            # 如果是文件路径
                            image = libpag.PAGImage.FromPath(value)
                            if image:
                                result = pag.replaceImage(layer_index, image)
                                print(f"[DEBUG] 替换图片 - 图层 {layer_index}: 文件 {value}, 结果: {result}")
                            else:
                                print(f"[ERROR] 无法加载图片文件 - {value}")
                        else:
                            print(f"[WARNING] 无效的图片数据 - 图层 {layer_index}: {value[:50]}...")
                            
                    except Exception as e:
                        print(f"[ERROR] 图片替换失败 - 图层 {layer_index}: {str(e)}")
                        import traceback
                        traceback.print_exc()
                
                elif mod_type == 'imageTransform':
                    # 🆕 应用图层变换（位置、锚点、缩放、旋转、不透明度）
                    # ⚠️ 注意：变换不会持久化到文件，需要在渲染时应用
                    transform = mod.get('transform', {})
                    print(f"[DEBUG] 记录图层变换 - 图层 {layer_index}: {transform}")
                    print(f"[DEBUG] ⚠️ 变换将在渲染时应用（不会保存到文件）")
                    
                    # 不在这里应用变换，因为它们不会持久化
                    # 变换会在渲染时由 apply_transforms_to_layers() 函数应用
            
            # 保存修改后的文件
            # 注意：新版本的 pypag 支持 save() 方法
            print(f"[DEBUG] ========================================")
            print(f"[DEBUG] 准备保存文件")
            print(f"[DEBUG] - 输出路径: {temp_output_path}")
            print(f"[DEBUG] - 当前图片层数: {pag.numImages()}")
            print(f"[DEBUG] ========================================")
            
            success = pag.save(temp_output_path)
            
            print(f"[DEBUG] save() 返回值: {success} (类型: {type(success)})")
            
            if not success:
                return jsonify({'error': 'PAG 文件保存失败，save() 返回 False'}), 500
            
            # 检查输出文件是否存在
            if not os.path.exists(temp_output_path):
                return jsonify({'error': '输出文件未生成'}), 500
            
            # 对比文件大小
            input_size = os.path.getsize(temp_input_path)
            output_size = os.path.getsize(temp_output_path)
            print(f"[DEBUG] 文件大小对比:")
            print(f"[DEBUG] - 输入文件: {input_size} 字节")
            print(f"[DEBUG] - 输出文件: {output_size} 字节")
            print(f"[DEBUG] - 差异: {output_size - input_size:+d} 字节")
            
            # 读取输出文件并返回
            with open(temp_output_path, 'rb') as f:
                output_data = f.read()
            
            print(f"[DEBUG] 读取输出数据: {len(output_data)} 字节")
            
            # 清理临时文件
            os.unlink(temp_input_path)
            os.unlink(temp_output_path)
            
            # 返回文件
            return send_file(
                io.BytesIO(output_data),
                mimetype='application/octet-stream',
                as_attachment=True,
                download_name=f'modified_{pag_file.filename}'
            )
            
        except Exception as e:
            # 清理临时文件
            if os.path.exists(temp_input_path):
                os.unlink(temp_input_path)
            if os.path.exists(temp_output_path):
                os.unlink(temp_output_path)
            raise e
        
    except Exception as e:
        import traceback
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


@app.route('/api/export-pag-simple', methods=['POST'])
def export_pag_simple():
    """
    简化版导出 - 使用 base64 编码的图片数据
    
    适用于前端直接发送图片数据的场景
    """
    try:
        if not PAG_AVAILABLE:
            return jsonify({
                'error': 'PAG SDK 未安装',
                'message': '请运行: pip install libpag'
            }), 500
        
        data = request.get_json()
        
        # 获取 base64 编码的 PAG 文件
        pag_base64 = data.get('pagFile')
        modifications = data.get('modifications', [])
        
        # 解码 PAG 文件
        pag_bytes = base64.b64decode(pag_base64)
        
        # 保存到临时文件
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pag') as temp_input:
            temp_input.write(pag_bytes)
            temp_input_path = temp_input.name
        
        temp_output = tempfile.NamedTemporaryFile(delete=False, suffix='.pag')
        temp_output_path = temp_output.name
        temp_output.close()
        
        try:
            # 加载并修改
            pag = libpag.PAGFile.Load(temp_input_path)
            
            for mod in modifications:
                layer_index = mod.get('layerIndex')
                mod_type = mod.get('type')
                value = mod.get('value')
                
                if mod_type == 'text':
                    text_data = pag.getTextData(layer_index)
                    if text_data:
                        text_data.text = value
                        pag.replaceText(layer_index, text_data)
                
                elif mod_type == 'image':
                    # value 是 base64 编码的图片
                    if value.startswith('data:image'):
                        # 提取 base64 数据
                        image_data = value.split(',')[1]
                        image_bytes = base64.b64decode(image_data)
                        
                        # 保存到临时文件
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_img:
                            temp_img.write(image_bytes)
                            image = libpag.PAGImage.FromPath(temp_img.name)
                            if image:
                                pag.replaceImage(layer_index, image)
                            os.unlink(temp_img.name)
            
            # 保存
            pag.save(temp_output_path)
            
            # 读取并编码为 base64
            with open(temp_output_path, 'rb') as f:
                output_bytes = f.read()
            
            output_base64 = base64.b64encode(output_bytes).decode('utf-8')
            
            # 清理
            os.unlink(temp_input_path)
            os.unlink(temp_output_path)
            
            return jsonify({
                'success': True,
                'pagFile': output_base64
            })
            
        except Exception as e:
            if os.path.exists(temp_input_path):
                os.unlink(temp_input_path)
            if os.path.exists(temp_output_path):
                os.unlink(temp_output_path)
            raise e
        
    except Exception as e:
        import traceback
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


if __name__ == '__main__':
    print("""
    ╔═══════════════════════════════════════╗
    ║   🚀 PAG 导出服务器                    ║
    ╚═══════════════════════════════════════╝
    
    服务地址: http://localhost:5000
    API 文档: http://localhost:5000/
    最大文件大小: 100 MB
    
    PAG SDK 状态: {status}
    {error_info}
    
    按 Ctrl+C 停止服务器
    """.format(
        status="✅ 已安装并可用" if PAG_AVAILABLE else "❌ 未安装",
        error_info="" if PAG_AVAILABLE else f"\n    错误信息: {IMPORT_ERROR_MSG}\n    解决方法: 设置 PYTHONPATH 或安装 libpag"
    ))
    
    # 运行服务器，配置允许大文件上传
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
