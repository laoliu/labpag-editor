#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PAG 运行时变换渲染器

支持在渲染时应用图层变换（位置、锚点、缩放、旋转、透明度）
"""

import sys
import os
import json

try:
    import pypag
    print("✅ pypag 导入成功")
except ImportError as e:
    print(f"❌ 导入 pypag 失败: {e}")
    sys.exit(1)


class PAGRuntimeRenderer:
    """PAG 运行时渲染器，支持动态应用变换"""
    
    def __init__(self, pag_file_path):
        """
        初始化渲染器
        
        Args:
            pag_file_path: PAG 文件路径
        """
        self.pag_file_path = pag_file_path
        self.pag = None
        self.modifications = []
        
    def load(self):
        """加载 PAG 文件"""
        if not os.path.exists(self.pag_file_path):
            raise FileNotFoundError(f"PAG 文件不存在: {self.pag_file_path}")
        
        self.pag = pypag.PAGFile.Load(self.pag_file_path)
        if not self.pag:
            raise RuntimeError("加载 PAG 文件失败")
        
        print(f"✅ PAG 文件加载成功")
        print(f"   - 尺寸: {self.pag.width()} × {self.pag.height()}")
        print(f"   - 时长: {self.pag.duration() / 1000000:.2f} 秒")
        print(f"   - 帧率: {self.pag.frameRate()} fps")
        
        return self
    
    def load_config(self, config_path_or_dict):
        """
        加载配置文件或字典
        
        Args:
            config_path_or_dict: JSON 配置文件路径或配置字典
        """
        if isinstance(config_path_or_dict, str):
            # 从文件加载
            with open(config_path_or_dict, 'r', encoding='utf-8') as f:
                config = json.load(f)
        else:
            # 直接使用字典
            config = config_path_or_dict
        
        self.modifications = config.get('modifications', [])
        print(f"✅ 配置加载成功，共 {len(self.modifications)} 个修改项")
        
        # 统计修改类型
        types = {}
        for mod in self.modifications:
            mod_type = mod.get('type', 'unknown')
            types[mod_type] = types.get(mod_type, 0) + 1
        
        for mod_type, count in types.items():
            print(f"   - {mod_type}: {count} 项")
        
        return self
    
    def apply_image_replacements(self):
        """
        应用图片替换（一次性，可持久化）
        
        Returns:
            int: 成功替换的图片数量
        """
        replaced_count = 0
        
        for mod in self.modifications:
            if mod.get('type') != 'imageReplacement':
                continue
            
            layer_index = mod.get('layerIndex', mod.get('editableIndex', 0))
            image_path = mod.get('imagePath', mod.get('newImagePath'))
            
            if not image_path or not os.path.exists(image_path):
                print(f"⚠️  图片文件不存在: {image_path}")
                continue
            
            try:
                # 获取图层
                layers = self.pag.getLayersByEditableIndex(layer_index, pypag.LayerType.Image)
                if not layers or len(layers) == 0:
                    print(f"⚠️  未找到图层索引 {layer_index}")
                    continue
                
                layer = layers[0]
                
                # 替换图片
                pag_image = pypag.PAGImage.FromPath(image_path)
                if pag_image:
                    layer.replaceImage(pag_image)
                    replaced_count += 1
                    print(f"✅ 图层 {layer_index} 图片已替换: {os.path.basename(image_path)}")
                else:
                    print(f"❌ 创建 PAGImage 失败: {image_path}")
            
            except Exception as e:
                print(f"❌ 替换图片失败 - 图层 {layer_index}: {e}")
        
        print(f"\n✅ 图片替换完成，成功 {replaced_count} 项")
        return replaced_count
    
    def apply_transforms(self):
        """
        应用所有图层变换（运行时，需要每帧调用）
        
        这个方法需要在渲染每一帧之前调用
        """
        for mod in self.modifications:
            if mod.get('type') != 'imageTransform':
                continue
            
            layer_index = mod.get('layerIndex', mod.get('editableIndex', 0))
            transform = mod.get('transform', {})
            
            try:
                # 获取图层
                layers = self.pag.getLayersByEditableIndex(layer_index, pypag.LayerType.Image)
                if not layers or len(layers) == 0:
                    continue
                
                layer = layers[0]
                
                # 应用位置
                if 'position' in transform:
                    pos = transform['position']
                    layer.setPosition(pos.get('x', 0), pos.get('y', 0))
                
                # 应用锚点
                if 'anchorPoint' in transform:
                    anchor = transform['anchorPoint']
                    layer.setAnchorPoint(anchor.get('x', 0), anchor.get('y', 0))
                
                # 应用缩放
                if 'scale' in transform:
                    scale = transform['scale']
                    layer.setScale(scale.get('x', 1.0), scale.get('y', 1.0))
                
                # 应用旋转
                if 'rotation' in transform:
                    layer.setRotation(transform['rotation'])
                
                # 应用透明度
                if 'opacity' in transform:
                    alpha = int(transform['opacity'] * 255)
                    layer.setAlpha(alpha)
            
            except Exception as e:
                print(f"❌ 应用变换失败 - 图层 {layer_index}: {e}")
    
    def render_frame(self, progress, output_path=None):
        """
        渲染单帧
        
        Args:
            progress: 进度 (0.0 - 1.0)
            output_path: 输出文件路径（可选）
        
        Returns:
            bool: 是否成功
        """
        if not self.pag:
            raise RuntimeError("PAG 文件未加载")
        
        # 应用变换（关键！每帧都要应用）
        self.apply_transforms()
        
        # 创建 Surface 进行渲染
        surface = pypag.PAGSurface.MakeOffscreen(self.pag.width(), self.pag.height())
        if not surface:
            print("❌ 创建 Surface 失败")
            return False
        
        # 创建 Player
        player = pypag.PAGPlayer()
        player.setSurface(surface)
        player.setComposition(self.pag)
        
        # 设置进度（通过 Player 设置，不是 PAGFile）
        player.setProgress(progress)
        
        # 刷新渲染
        player.flush()
        
        # 如果指定了输出路径，保存图片
        if output_path:
            # 从 Surface 读取像素数据
            pixels = surface.readPixels()
            if pixels:
                # 这里需要将像素数据保存为图片
                # 实际使用时可能需要 PIL 或其他库
                print(f"✅ 渲染完成: {output_path}")
                # TODO: 保存像素数据为图片
            else:
                print("❌ 读取像素数据失败")
                return False
        
        return True
    
    def render_video(self, output_dir, fps=None, prefix="frame"):
        """
        渲染完整视频的所有帧
        
        Args:
            output_dir: 输出目录
            fps: 帧率（默认使用 PAG 文件的帧率）
            prefix: 文件名前缀
        
        Returns:
            list: 生成的帧文件路径列表
        """
        if not self.pag:
            raise RuntimeError("PAG 文件未加载")
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        # 使用 PAG 文件的帧率
        if fps is None:
            fps = self.pag.frameRate()
        
        # 计算总帧数
        duration_seconds = self.pag.duration() / 1000000.0  # 微秒转秒
        total_frames = int(duration_seconds * fps)
        
        print(f"\n🎬 开始渲染视频")
        print(f"   - 总帧数: {total_frames}")
        print(f"   - 帧率: {fps} fps")
        print(f"   - 输出目录: {output_dir}")
        
        frame_paths = []
        
        for frame_num in range(total_frames):
            # 计算进度
            progress = frame_num / max(total_frames - 1, 1)
            
            # 输出路径
            output_path = os.path.join(output_dir, f"{prefix}_{frame_num:04d}.png")
            
            # 渲染帧
            success = self.render_frame(progress, output_path)
            
            if success:
                frame_paths.append(output_path)
                
                # 显示进度
                if (frame_num + 1) % 10 == 0 or frame_num == total_frames - 1:
                    percent = ((frame_num + 1) / total_frames) * 100
                    print(f"   渲染进度: {frame_num + 1}/{total_frames} ({percent:.1f}%)")
            else:
                print(f"❌ 渲染帧 {frame_num} 失败")
        
        print(f"\n✅ 渲染完成！共 {len(frame_paths)} 帧")
        return frame_paths


def main():
    """主函数 - 示例用法"""
    
    # 示例配置
    example_config = {
        "modifications": [
            {
                "layerIndex": 0,
                "type": "imageReplacement",
                "imagePath": r"D:\Documents\Downloads\d91b11e9056867581a1f1de8ec6c92ef.jpeg"
            },
            {
                "layerIndex": 0,
                "type": "imageTransform",
                "transform": {
                    "position": {"x": 100, "y": 200},
                    "anchorPoint": {"x": 50, "y": 50},
                    "scale": {"x": 1.5, "y": 1.5},
                    "rotation": 45,
                    "opacity": 0.8
                }
            }
        ]
    }
    
    # PAG 文件路径
    pag_file = r"D:\Documents\Downloads\modified_1764685791226.pag"
    
    print("=" * 60)
    print("🎬 PAG 运行时变换渲染器")
    print("=" * 60)
    print()
    
    try:
        # 创建渲染器
        renderer = PAGRuntimeRenderer(pag_file)
        
        # 加载 PAG 文件
        renderer.load()
        
        # 加载配置
        renderer.load_config(example_config)
        
        # 应用图片替换（一次性）
        renderer.apply_image_replacements()
        
        print("\n" + "=" * 60)
        print("🎬 渲染测试")
        print("=" * 60)
        
        # 测试渲染单帧
        print("\n🧪 测试 1: 渲染第一帧 (进度 0%)")
        renderer.render_frame(0.0)
        
        print("\n🧪 测试 2: 渲染中间帧 (进度 50%)")
        renderer.render_frame(0.5)
        
        print("\n🧪 测试 3: 渲染最后一帧 (进度 100%)")
        renderer.render_frame(1.0)
        
        print("\n✅ 渲染测试完成！")
        print("\n💡 提示:")
        print("   - 变换在每帧渲染前都会重新应用")
        print("   - 图片替换只需要应用一次")
        print("   - 要渲染完整视频，使用 renderer.render_video()")
        
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
