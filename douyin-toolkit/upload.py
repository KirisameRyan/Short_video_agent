#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
上传到 Dify - 支持断点续传和慢速上传
"""

import requests
import json
from pathlib import Path
import time

DIFY_API_BASE = "http://www.azureflame.cloud/v1"
PROGRESS_FILE = "upload_progress.json"

def load_progress():
    """加载上传进度"""
    if Path(PROGRESS_FILE).exists():
        with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"uploaded": []}

def save_progress(uploaded_files):
    """保存上传进度"""
    with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
        json.dump({"uploaded": uploaded_files}, f, ensure_ascii=False, indent=2)

def upload_document(api_key: str, dataset_id: str, file_path: Path) -> bool:
    """上传文档（增加超时重试）"""
    
    url = f"{DIFY_API_BASE}/datasets/{dataset_id}/document/create_by_file"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    if not file_path.exists():
        print(f"✗ 文件不存在")
        return False
    
    print(f"[{file_path.name[:35]}...] ", end="", flush=True)
    
    # 重试3次
    for attempt in range(3):
        try:
            with open(file_path, 'rb') as f:
                files = {'file': (file_path.name, f, 'text/plain')}
                data = {
                    'data': json.dumps({
                        'indexing_technique': 'high_quality',
                        'process_rule': {'mode': 'automatic'}
                    })
                }
                
                response = requests.post(url, headers=headers, files=files, data=data, timeout=90)
            
            if response.status_code == 200:
                print("✓")
                return True
            else:
                error = response.json() if response.text else {}
                print(f"✗ {error.get('message', response.status_code)}")
                return False
        
        except requests.exceptions.Timeout:
            if attempt < 2:
                wait = (attempt + 1) * 5
                print(f"⏱ 超时，等待{wait}秒重试...", end="", flush=True)
                time.sleep(wait)
            else:
                print("✗ 超时")
                return False
        
        except Exception as e:
            print(f"✗ {e}")
            return False
    
    return False

def scan_dialogues():
    """扫描对话文件"""
    files = []
    base = Path("enhanced_dialogues")
    for tier in ["S_tier_enhanced", "A_tier_enhanced", "B_tier_enhanced"]:
        if (base / tier).exists():
            files.extend(sorted((base / tier).glob("*.txt")))
    return files

def main():
    print("\n" + "="*60)
    print("上传到 Dify（支持断点续传 + 慢速模式）")
    print("="*60 + "\n")
    
    # 加载进度
    progress = load_progress()
    uploaded = set(progress.get("uploaded", []))
    
    if uploaded:
        print(f"[发现进度] 已上传 {len(uploaded)} 个文件")
        if input("是否继续？(y/n): ").lower() != 'y':
            return
    
    api_key = input("\nDify API Key: ").strip()
    if not api_key:
        return
    
    print("\n请输入知识库 ID：")
    kb_id = input("实战案例库 ID: ").strip()
    
    if not kb_id:
        return
    
    # 扫描文件
    all_files = scan_dialogues()
    remaining_files = [f for f in all_files if f.name not in uploaded]
    
    print(f"\n文件统计：")
    print(f"  总文件: {len(all_files)}")
    print(f"  已上传: {len(uploaded)}")
    print(f"  待上传: {len(remaining_files)}")
    
    if not remaining_files:
        print("\n✓ 所有文件已上传完成！")
        return
    
    if input("\n开始上传？(y/n): ").lower() != 'y':
        return
    
    print("\n" + "="*60)
    print(f"开始上传（快速模式：2秒/文件）")
    print("="*60 + "\n")
    
    success = 0
    total = len(remaining_files)
    
    try:
        for i, file_path in enumerate(remaining_files, 1):
            current_total = len(uploaded) + success
            print(f"[{current_total+1}/{len(all_files)}] ", end="")
            
            if upload_document(api_key, kb_id, file_path):
                success += 1
                uploaded.add(file_path.name)
                
                # 每5个文件保存一次进度
                if success % 5 == 0:
                    save_progress(list(uploaded))
            
            # 快速上传：每个文件间隔2秒
            if i < total:
                if success % 30 == 0:
                    print(f"\n[进度] 已上传 {current_total+1}/{len(all_files)}, 暂停5秒...\n")
                    save_progress(list(uploaded))
                    time.sleep(1)
                else:
                    time.sleep(1)
    
    except KeyboardInterrupt:
        print("\n\n[中断] 进度已保存")
        save_progress(list(uploaded))
        print(f"已上传: {len(uploaded)}/{len(all_files)}")
        return
    
    # 保存最终进度
    save_progress(list(uploaded))
    
    print(f"\n完成: {len(uploaded)}/{len(all_files)} ({success}个新上传)")
    print("\n" + "="*60)
    print("上传完成！")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
