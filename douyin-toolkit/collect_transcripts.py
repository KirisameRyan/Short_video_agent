# -*- coding: utf-8 -*-
"""
收集所有 funasr_output/text.txt 文件，并按照视频信息重命名
"""

import os
import json
import shutil
from pathlib import Path

# 配置
SOURCE_DIR = r"D:\迅雷下载\douyin-downloader-main\douyin-downloader-main\Downloaded"
OUTPUT_DIR = r"C:\Users\49713\.openclaw\workspace\douyin_transcripts_raw"
MANIFEST_FILE = os.path.join(SOURCE_DIR, "download_manifest.jsonl")

# 创建输出目录
os.makedirs(OUTPUT_DIR, exist_ok=True)

def load_video_metadata():
    """加载视频元数据"""
    metadata = {}
    with open(MANIFEST_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            video = json.loads(line)
            # 使用视频文件夹名作为 key
            folder_name = video['file_paths'][0].split('\\')[0] if '\\' in video['file_paths'][0] else video['file_paths'][0].split('/')[0]
            metadata[video['aweme_id']] = {
                'author': video['author_name'],
                'date': video['date'],
                'desc': video['desc'],
                'aweme_id': video['aweme_id']
            }
    return metadata

def main():
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    print("=" * 80)
    print("收集和重命名转录文件")
    print("=" * 80)
    
    # 加载视频元数据
    print("\n正在加载视频元数据...")
    metadata = load_video_metadata()
    print(f"OK 已加载 {len(metadata)} 个视频的元数据")
    
    # 查找所有 text.txt 文件
    print("\n正在搜索转录文件...")
    text_files = list(Path(SOURCE_DIR).rglob('funasr_output/text.txt'))
    print(f"✅ 找到 {len(text_files)} 个转录文件")
    
    if len(text_files) == 0:
        print("\n❌ 未找到任何转录文件！")
        return
    
    # 复制并重命名文件
    print("\n开始收集文件...")
    success_count = 0
    failed_count = 0
    
    for i, text_file in enumerate(text_files, 1):
        try:
            # 读取文件内容获取 key
            with open(text_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                key = data.get('key', '')
            
            # 从 key 中提取 aweme_id（最后一段数字）
            aweme_id = key.split('_')[-1] if '_' in key else ''
            
            if aweme_id and aweme_id in metadata:
                meta = metadata[aweme_id]
                # 生成新文件名：日期_作者_描述前30字_ID.txt
                desc_short = meta['desc'][:30].replace('/', '-').replace('\\', '-').replace(':', '-').replace('?', '').replace('*', '').replace('"', '').replace('<', '').replace('>', '').replace('|', '')
                author_clean = meta['author'].replace('/', '-').replace('\\', '-')
                new_filename = f"{meta['date']}_{author_clean}_{desc_short}_{aweme_id}.txt"
                
                # 复制文件
                dest_path = os.path.join(OUTPUT_DIR, new_filename)
                shutil.copy2(text_file, dest_path)
                
                print(f"[{i}/{len(text_files)}] ✅ {new_filename}")
                success_count += 1
            else:
                # 如果找不到元数据，使用原始 key
                new_filename = f"{key}.txt" if key else f"unknown_{i}.txt"
                dest_path = os.path.join(OUTPUT_DIR, new_filename)
                shutil.copy2(text_file, dest_path)
                
                print(f"[{i}/{len(text_files)}] ⚠️ {new_filename} (无元数据)")
                success_count += 1
                
        except Exception as e:
            print(f"[{i}/{len(text_files)}] ❌ 失败: {e}")
            failed_count += 1
    
    print("\n" + "=" * 80)
    print("收集完成！")
    print(f"✅ 成功: {success_count} 个")
    print(f"❌ 失败: {failed_count} 个")
    print(f"📁 输出目录: {OUTPUT_DIR}")
    print("=" * 80)

if __name__ == "__main__":
    main()
