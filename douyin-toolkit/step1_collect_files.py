# -*- coding: utf-8 -*-
"""
简单脚本：把所有 funasr_output/text.txt 收集到一个文件夹，并重命名
"""

import os
import shutil
import re

# 配置（根据你的实际情况修改）
SOURCE_ROOT = r"D:\迅雷下载\douyin-downloader-main\douyin-downloader-main\Downloaded"   # 根目录
OUTPUT_DIR = r"C:\Users\49713\.openclaw\workspace\douyin_transcripts_raw"                                  # 统一输出文件夹（改成你想要的路径）

# 创建输出目录
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("开始收集 text.txt 文件...")
print(f"源根目录: {SOURCE_ROOT}")
print(f"输出目录: {OUTPUT_DIR}")
print("-" * 60)

# 查找所有 text.txt
text_files = []
for root, dirs, files in os.walk(SOURCE_ROOT):
    if 'funasr_output' in root and 'text.txt' in files:
        text_files.append(os.path.join(root, 'text.txt'))

print(f"找到 {len(text_files)} 个 text.txt 文件")

if not text_files:
    print("没有找到任何 text.txt 文件！")
    exit(1)

# 复制并重命名
success = 0
failed = 0

for txt_path in text_files:
    try:
        # 从上级目录名提取有意义的部分作为文件名
        parent_dir = os.path.basename(os.path.dirname(os.path.dirname(txt_path)))  # funasr_output 的父目录（通常是视频文件夹名）
        
        # 清理非法字符，保留中文 + 字母数字 + _ -
        clean_name = re.sub(r'[<>:"/\\|?*]', '_', parent_dir)
        clean_name = clean_name.strip().replace(' ', '_')[:150]  # 长度限制
        
        # 如果名字太短或为空，用序号兜底
        if len(clean_name) < 5:
            clean_name = f"video_{success + failed + 1:04d}"
        
        new_filename = f"{clean_name}.txt"
        dest_path = os.path.join(OUTPUT_DIR, new_filename)
        
        # 如果同名已存在，加序号避免覆盖
        base, ext = os.path.splitext(new_filename)
        counter = 1
        while os.path.exists(dest_path):
            new_filename = f"{base}_{counter}{ext}"
            dest_path = os.path.join(OUTPUT_DIR, new_filename)
            counter += 1
        
        shutil.copy2(txt_path, dest_path)
        print(f"已复制并重命名: {new_filename}")
        success += 1
        
    except Exception as e:
        print(f"失败: {txt_path} → {e}")
        failed += 1

print("\n" + "=" * 60)
print(f"完成！")
print(f"成功复制并重命名: {success} 个文件")
print(f"失败: {failed} 个")
print(f"所有文件已统一保存到: {OUTPUT_DIR}")
print("=" * 60)