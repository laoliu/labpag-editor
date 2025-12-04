"""
PAG 模板批量编辑器 - Python 版本
使用 JSON 配置批量生成个性化 PAG 文件

依赖:
    需要安装 PAG Python SDK (如果有的话)
    或者使用 Node.js PAG SDK
    
当前实现:
    提供配置结构和使用示例
    实际编辑需要 PAG SDK 支持
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any


class PAGTemplateBatchEditor:
    """PAG 模板批量编辑器"""
    
    def __init__(self, template_path: str):
        """
        初始化编辑器
        
        Args:
            template_path: PAG 模板文件路径
        """
        self.template_path = template_path
        self.template_name = Path(template_path).stem
        
    def generate_batch(self, config_list: List[Dict[str, Any]], output_dir: str):
        """
        批量生成 PAG 文件
        
        Args:
            config_list: 配置列表，每个配置包含修改信息
            output_dir: 输出目录
            
        示例配置:
            [
                {
                    "name": "张三",
                    "modifications": [
                        {"type": "text", "layerIndex": 0, "value": "张三"},
                        {"type": "text", "layerIndex": 1, "value": "产品经理"}
                    ]
                },
                {
                    "name": "李四",
                    "modifications": [
                        {"type": "text", "layerIndex": 0, "value": "李四"},
                        {"type": "text", "layerIndex": 1, "value": "设计师"}
                    ]
                }
            ]
        """
        os.makedirs(output_dir, exist_ok=True)
        
        for i, config in enumerate(config_list):
            name = config.get('name', f'output_{i}')
            modifications = config.get('modifications', [])
            
            output_path = os.path.join(output_dir, f'{self.template_name}_{name}.pag')
            
            print(f"生成: {output_path}")
            self._apply_modifications(modifications, output_path)
            
    def _apply_modifications(self, modifications: List[Dict], output_path: str):
        """
        应用修改并保存
        
        注意: 这需要 PAG SDK 支持
        当前为示例代码
        """
        # TODO: 使用 PAG SDK 实际实现
        # 1. 加载模板
        # pag_file = PAG.load(self.template_path)
        
        # 2. 应用修改
        # for mod in modifications:
        #     if mod['type'] == 'text':
        #         pag_file.replace_text(mod['layerIndex'], mod['value'])
        #     elif mod['type'] == 'image':
        #         pag_file.replace_image(mod['layerIndex'], mod['imagePath'])
        
        # 3. 保存
        # pag_file.save(output_path)
        
        print(f"  - 应用了 {len(modifications)} 个修改")
        

class PAGBatchConfigGenerator:
    """PAG 批量配置生成器"""
    
    @staticmethod
    def from_csv(csv_path: str) -> List[Dict]:
        """
        从 CSV 文件生成配置
        
        CSV 格式:
            name,title,subtitle,phone
            张三,产品经理,创新部,138****1234
            李四,设计师,设计部,139****5678
            
        Returns:
            配置列表
        """
        import csv
        
        configs = []
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                config = {
                    'name': row['name'],
                    'modifications': []
                }
                
                # 根据 CSV 列生成修改配置
                # 假设: 列0=姓名, 列1=职位, 列2=部门, 列3=电话
                layer_index = 0
                for key, value in row.items():
                    if key != 'name':  # name 用作输出文件名
                        config['modifications'].append({
                            'type': 'text',
                            'layerIndex': layer_index,
                            'value': value
                        })
                        layer_index += 1
                
                configs.append(config)
                
        return configs
    
    @staticmethod
    def from_json(json_path: str) -> List[Dict]:
        """从 JSON 文件加载配置"""
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    @staticmethod
    def to_json(configs: List[Dict], output_path: str):
        """保存配置到 JSON"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(configs, f, ensure_ascii=False, indent=2)


# ============================================================
# 使用示例
# ============================================================

def example_batch_namecard():
    """示例: 批量生成个性化名片"""
    
    # 1. 准备配置
    configs = [
        {
            'name': '张三',
            'modifications': [
                {'type': 'text', 'layerIndex': 0, 'value': '张三'},
                {'type': 'text', 'layerIndex': 1, 'value': '产品经理'},
                {'type': 'text', 'layerIndex': 2, 'value': '创新部'},
                {'type': 'text', 'layerIndex': 3, 'value': '138****1234'},
            ]
        },
        {
            'name': '李四',
            'modifications': [
                {'type': 'text', 'layerIndex': 0, 'value': '李四'},
                {'type': 'text', 'layerIndex': 1, 'value': '设计师'},
                {'type': 'text', 'layerIndex': 2, 'value': '设计部'},
                {'type': 'text', 'layerIndex': 3, 'value': '139****5678'},
            ]
        },
    ]
    
    # 2. 批量生成
    editor = PAGTemplateBatchEditor('templates/namecard.pag')
    editor.generate_batch(configs, 'output/namecards')
    

def example_from_csv():
    """示例: 从 CSV 批量生成"""
    
    # 1. 从 CSV 加载配置
    configs = PAGBatchConfigGenerator.from_csv('data/employees.csv')
    
    # 2. 批量生成
    editor = PAGTemplateBatchEditor('templates/employee_card.pag')
    editor.generate_batch(configs, 'output/employee_cards')
    

def example_save_config():
    """示例: 生成并保存配置"""
    
    configs = [
        {
            'name': '活动1',
            'modifications': [
                {'type': 'text', 'layerIndex': 0, 'value': '双十一狂欢'},
                {'type': 'image', 'layerIndex': 0, 'imagePath': 'images/bg1.jpg'},
            ]
        },
        {
            'name': '活动2',
            'modifications': [
                {'type': 'text', 'layerIndex': 0, 'value': '618大促'},
                {'type': 'image', 'layerIndex': 0, 'imagePath': 'images/bg2.jpg'},
            ]
        },
    ]
    
    # 保存配置
    PAGBatchConfigGenerator.to_json(configs, 'configs/activity_posters.json')
    

# ============================================================
# Node.js 调用方案（推荐）
# ============================================================

def generate_nodejs_script(config_path: str, template_path: str, output_dir: str):
    """
    生成 Node.js 脚本用于批量编辑
    
    因为 PAG SDK 在 Node.js 环境下更成熟
    """
    script = f"""
const PAG = require('libpag');
const fs = require('fs');
const path = require('path');

async function batchGenerate() {{
    // 加载配置
    const configs = JSON.parse(fs.readFileSync('{config_path}', 'utf-8'));
    
    // 加载模板
    const templateBuffer = fs.readFileSync('{template_path}');
    const templateFile = await PAG.PAGFile.load(templateBuffer);
    
    // 批量生成
    for (const config of configs) {{
        console.log(`生成: ${{config.name}}`);
        
        // 克隆模板
        const pagFile = templateFile.copyOriginal();
        
        // 应用修改
        for (const mod of config.modifications) {{
            if (mod.type === 'text') {{
                const textData = await pagFile.getTextData(mod.layerIndex);
                textData.text = mod.value;
                await pagFile.replaceText(mod.layerIndex, textData);
            }} else if (mod.type === 'image') {{
                const imageBuffer = fs.readFileSync(mod.imagePath);
                await pagFile.replaceImage(mod.layerIndex, imageBuffer);
            }}
        }}
        
        // 保存
        const outputPath = path.join('{output_dir}', `${{config.name}}.pag`);
        const outputBuffer = await pagFile.save();
        fs.writeFileSync(outputPath, outputBuffer);
        
        console.log(`  ✅ 已保存: ${{outputPath}}`);
    }}
    
    console.log('\\n✨ 批量生成完成！');
}}

batchGenerate().catch(console.error);
"""
    
    output_path = 'batch_generate.js'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(script)
    
    print(f"✅ 已生成 Node.js 脚本: {output_path}")
    print(f"运行: node {output_path}")


# ============================================================
# 主函数
# ============================================================

if __name__ == '__main__':
    import sys
    
    print("=" * 60)
    print("PAG 模板批量编辑器")
    print("=" * 60)
    print()
    
    print("功能:")
    print("1. 批量生成配置文件")
    print("2. 从 CSV 批量生成")
    print("3. 生成 Node.js 批量脚本（推荐）")
    print()
    
    print("注意:")
    print("- Python SDK 支持有限，推荐使用 Node.js 方案")
    print("- 或使用 Web 版模板编辑器: http://localhost:8000/pag_template_editor.html")
    print()
    
    # 示例: 生成 Node.js 脚本
    print("生成 Node.js 批量脚本示例...")
    
    # 创建示例配置
    example_configs = [
        {
            'name': '张三_名片',
            'modifications': [
                {'type': 'text', 'layerIndex': 0, 'value': '张三'},
                {'type': 'text', 'layerIndex': 1, 'value': '产品经理'},
            ]
        },
        {
            'name': '李四_名片',
            'modifications': [
                {'type': 'text', 'layerIndex': 0, 'value': '李四'},
                {'type': 'text', 'layerIndex': 1, 'value': '设计师'},
            ]
        },
    ]
    
    # 保存配置
    os.makedirs('configs', exist_ok=True)
    config_path = 'configs/batch_config.json'
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(example_configs, f, ensure_ascii=False, indent=2)
    print(f"✅ 已生成配置: {config_path}")
    
    # 生成 Node.js 脚本
    generate_nodejs_script(
        config_path='configs/batch_config.json',
        template_path='templates/namecard.pag',
        output_dir='output'
    )
    
    print()
    print("=" * 60)
    print("✨ 完成！")
    print("=" * 60)
