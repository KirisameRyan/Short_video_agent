#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
格式化 JSON 文件，文档之间增加换行
"""

import json
from pathlib import Path

input_file = Path("dify_knowledge/文档结构化数据.json")
output_file = Path("dify_knowledge/文档结构化数据_格式化.json")

print("正在格式化 JSON 文件...")

with open(input_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

# 提取文档列表
docs = data.get("文档列表", [])
metadata = {k: v for k, v in data.items() if k != "文档列表"}

print(f"文档数量: {len(docs)}")

# 手动格式化输出
with open(output_file, 'w', encoding='utf-8') as f:
    f.write("{\n")
    
    # 写入元数据
    for idx, (key, value) in enumerate(metadata.items()):
        f.write(f'  "{key}": ')
        if isinstance(value, str):
            f.write(f'"{value}"')
        else:
            f.write(str(value))
        f.write(",\n")
    
    # 写入文档列表
    f.write('  "文档列表": [\n')
    
    for idx, doc in enumerate(docs):
        # 每个文档前后加空行
        if idx > 0:
            f.write("\n")
        
        f.write("    ")
        f.write(json.dumps(doc, ensure_ascii=False, indent=6).replace("\n", "\n    "))
        
        if idx < len(docs) - 1:
            f.write(",\n")
        else:
            f.write("\n")
    
    f.write("  ]\n")
    f.write("}\n")

print(f"✓ 已保存到: {output_file}")
print(f"原文件保留: {input_file}")
