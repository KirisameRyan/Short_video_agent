# -*- coding: utf-8 -*-
"""
最终版：跳过 FunASR 输出中最长的开头大段文本
保留后面的短句对话，按原始顺序
每个原始 txt 生成一个 _clean.txt
"""

import os
import re

INPUT_DIR = r"C:\Users\49713\.openclaw\workspace\douyin_transcripts_raw"
OUTPUT_DIR = os.path.join(os.path.expanduser("~"), "Desktop", "douyin_clean_dialogues")
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("开始清洗（自动跳过最长开头大段）...")
print(f"输入: {INPUT_DIR}")
print(f"输出: {OUTPUT_DIR}")
print("-" * 60)

success = 0
failed = 0

for filename in os.listdir(INPUT_DIR):
    if not filename.lower().endswith('.txt'):
        continue
    
    input_path = os.path.join(INPUT_DIR, filename)
    print(f"处理: {filename}")
    
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 提取每个 text + spk
        pattern = r"\{[^}]*?'text':\s*'(.*?)'[^}]*?'spk':\s*(\d+)[^}]*?\}"
        matches = re.findall(pattern, content, re.DOTALL | re.MULTILINE)
        
        if not matches:
            print(f"  未匹配到对话，跳过")
            failed += 1
            continue
        
        # 收集所有段落（text, spk, length）
        segments = []
        for text, spk_str in matches:
            spk = int(spk_str)
            text = text.strip()
            text = re.sub(r'\\n|\\r|\[\[.*?\]\]|\[.*?\]|start|end|timestamp|sentence_info', '', text)
            text = re.sub(r'\s+', ' ', text).strip()
            if text:
                segments.append((text, spk, len(text)))
        
        if not segments:
            print(f"  无有效内容，跳过")
            failed += 1
            continue
        
        # 找到最长段落的索引（开头大段通常最长）
        max_length_idx = max(range(len(segments)), key=lambda i: segments[i][2])
        
        # 如果最长段落长度 > 200 字符，就跳过它（可调阈值）
        if segments[max_length_idx][2] > 200:
            print(f"  跳过最长段落（长度 {segments[max_length_idx][2]} 字符）")
            del segments[max_length_idx]
        
        # 按原始顺序输出剩余段落
        clean_lines = []
        for text, spk, _ in segments:
            clean_lines.append(f"spk {spk}: {text}")
        
        if clean_lines:
            base_name = os.path.splitext(filename)[0]
            new_filename = f"{base_name}_clean.txt"
            output_path = os.path.join(OUTPUT_DIR, new_filename)
            
            with open(output_path, 'w', encoding='utf-8') as out:
                out.write('\n'.join(clean_lines))
            
            print(f"  成功生成: {new_filename} ({len(clean_lines)} 行)")
            success += 1
        else:
            print(f"  提取后无短句，跳过")
            failed += 1
    
    except Exception as e:
        print(f"  失败 {filename}: {e}")
        failed += 1

print("\n" + "=" * 60)
print(f"处理完成！")
print(f"成功生成纯台词文件: {success} 个")
print(f"失败/无内容: {failed} 个")
print(f"所有结果在: {OUTPUT_DIR}")
print("每个文件已跳过最长开头大段，只保留短句对话")
print("=" * 60)