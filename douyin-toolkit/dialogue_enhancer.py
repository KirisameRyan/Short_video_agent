#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
对话增强脚本 v1.1 - 交互式配置版本
"""

import os
import json
import time
from pathlib import Path
import requests

# ========== 配置区 ==========
API_BASE_URL = "https://api.siliconflow.cn/v1"
MODEL_NAME = "deepseek-ai/DeepSeek-V3"

INPUT_DIRS = [
    "douyin_dialogues_S_tier",
    "douyin_dialogues_A_tier", 
    "douyin_dialogues_B_tier"
]
OUTPUT_DIR = "enhanced_dialogues"

# API 请求配置
MAX_RETRIES = 3
RETRY_DELAY = 2
REQUEST_TIMEOUT = 120

# ========== 提示词模板 ==========
SYSTEM_PROMPT = """你是一个专业的短剧编剧和对话优化专家。你的任务是：

1. **场景识别**：分析对话内容，识别明显的场景切换点（如地点变化、时间跳跃、话题转折）
2. **说话人优化**：
   - 如果整段对话只有一个说话人（spk 0），根据内容合理推断并分配多个角色
   - 为每个角色起一个简短的名字或称呼（如"男主"、"女主"、"路人甲"、"老板"等）
3. **连贯性增强**：在场景切换处添加简短的场景描述（1-2句话）
4. **格式规范**：
   - 场景标记：[场景：xxx]（如 [场景：街头夜晚]）
   - 说话人格式：角色名：对话内容
   - 每个场景之间空一行

**要求**：
- 保持原对话内容不变，只添加场景标记和优化说话人
- 场景描述要简洁、具象，突出环境和氛围
- 说话人名字要符合角色特点和剧情逻辑
- 如果原文本质量差（逻辑混乱、无法理解），可以适当润色补充过渡句，但不要改变核心情节

输出纯文本格式，不要markdown代码块。"""

USER_PROMPT_TEMPLATE = """请优化以下短剧对话：

原始对话：
```
{dialogue_text}
```

请按要求重写，添加场景标记和优化说话人。"""

# ========== 核心函数 ==========

def call_deepseek_api(dialogue_text: str, api_key: str) -> str:
    """调用硅基流动 DeepSeek API"""
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": USER_PROMPT_TEMPLATE.format(dialogue_text=dialogue_text)}
        ],
        "temperature": 0.7,
        "max_tokens": 4096,
        "stream": False
    }
    
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.post(
                f"{API_BASE_URL}/chat/completions",
                headers=headers,
                json=payload,
                timeout=REQUEST_TIMEOUT
            )
            
            if response.status_code == 200:
                result = response.json()
                enhanced_text = result["choices"][0]["message"]["content"].strip()
                
                # 移除可能的 markdown 代码块标记
                if enhanced_text.startswith("```"):
                    lines = enhanced_text.split("\n")
                    enhanced_text = "\n".join(lines[1:-1]) if len(lines) > 2 else enhanced_text
                
                return enhanced_text
            
            elif response.status_code == 429:  # Rate limit
                wait_time = RETRY_DELAY * (attempt + 1)
                print(f"[WARN] 触发速率限制，等待 {wait_time} 秒...")
                time.sleep(wait_time)
            
            else:
                error_msg = f"API 错误 {response.status_code}: {response.text[:200]}"
                print(f"[ERROR] {error_msg}")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY)
                else:
                    raise Exception(error_msg)
        
        except requests.exceptions.Timeout:
            print(f"[WARN] 请求超时 (尝试 {attempt + 1}/{MAX_RETRIES})")
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
        
        except Exception as e:
            print(f"[ERROR] 请求异常: {e}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
    
    raise Exception(f"API 调用失败，已重试 {MAX_RETRIES} 次")

def process_file(input_path: Path, output_path: Path, api_key: str) -> bool:
    """处理单个对话文件"""
    
    try:
        # 读取原始对话
        with open(input_path, 'r', encoding='utf-8', errors='ignore') as f:
            original_text = f.read().strip()
        
        if not original_text:
            print(f"[SKIP] 空文件: {input_path.name}")
            return False
        
        # 调用 API 增强
        print(f"[PROCESSING] {input_path.name}")
        enhanced_text = call_deepseek_api(original_text, api_key)
        
        # 保存结果
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(enhanced_text)
        
        print(f"[SUCCESS] {output_path.name}")
        return True
    
    except Exception as e:
        print(f"[FAILED] {input_path.name}: {str(e)[:100]}")
        return False

def process_tier_directory(tier_dir: str, output_subdir: str, api_key: str):
    """处理某个等级目录下的所有文件"""
    
    input_dir = Path(tier_dir)
    output_dir = Path(OUTPUT_DIR) / output_subdir
    
    if not input_dir.exists():
        print(f"[SKIP] 目录不存在: {tier_dir}")
        return
    
    txt_files = list(input_dir.glob("*.txt"))
    total = len(txt_files)
    success = 0
    
    print(f"\n{'='*60}")
    print(f"处理目录: {tier_dir}")
    print(f"文件数量: {total}")
    print(f"{'='*60}\n")
    
    for idx, file_path in enumerate(txt_files, 1):
        print(f"\n[{idx}/{total}] ", end="")
        output_path = output_dir / file_path.name
        
        if output_path.exists():
            print(f"[EXISTS] 跳过: {file_path.name}")
            success += 1  # 算作成功
            continue
        
        if process_file(file_path, output_path, api_key):
            success += 1
        
        # 避免过快请求
        if idx < total:
            time.sleep(1.5)
    
    print(f"\n[DONE] {tier_dir} 完成: {success}/{total} 个文件成功处理\n")

def main():
    """主函数"""
    
    print("\n" + "="*60)
    print("短剧对话增强脚本 v1.1")
    print("="*60)
    
    # 获取 API Key
    api_key = input("\n请输入硅基流动 API Key: ").strip()
    
    if not api_key:
        print("[ERROR] API Key 不能为空")
        return
    
    # 创建输出目录
    Path(OUTPUT_DIR).mkdir(exist_ok=True)
    
    # 处理每个等级目录
    tier_mapping = {
        "douyin_dialogues_S_tier": "S_tier_enhanced",
        "douyin_dialogues_A_tier": "A_tier_enhanced",
        "douyin_dialogues_B_tier": "B_tier_enhanced"
    }
    
    for input_dir, output_subdir in tier_mapping.items():
        if input_dir in INPUT_DIRS:
            process_tier_directory(input_dir, output_subdir, api_key)
    
    print("\n" + "="*60)
    print("全部处理完成！")
    print(f"结果保存在: {OUTPUT_DIR}/")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
