# -*- coding: utf-8 -*-
"""
使用 DeepSeek V3 API 对对话文档质量打分
硅基流动 API endpoint
"""

import os
import json
import time
import shutil
from pathlib import Path
import requests

# ==================== 配置区 ====================
# 硅基流动 API 配置
API_KEY = "sk-rwzbuuzfslwaissfaznnuxoohkyinagjdlprewvvbvzhllnb"  # 【需要填写】在这里填入你的硅基流动 API Key
API_BASE = "https://api.siliconflow.cn/v1"
MODEL = "deepseek-ai/DeepSeek-V3.2"

# 目录配置
INPUT_DIR = r"C:\Users\49713\.openclaw\workspace\douyin_clean_dialogues_filtered"
OUTPUT_DIR_S = r"C:\Users\49713\.openclaw\workspace\douyin_dialogues_S_tier"   # S级 (9-10分)
OUTPUT_DIR_A = r"C:\Users\49713\.openclaw\workspace\douyin_dialogues_A_tier"   # A级 (7-8分)
OUTPUT_DIR_B = r"C:\Users\49713\.openclaw\workspace\douyin_dialogues_B_tier"   # B级 (5-6分)
OUTPUT_DIR_C = r"C:\Users\49713\.openclaw\workspace\douyin_dialogues_C_tier"   # C级 (3-4分)
OUTPUT_DIR_D = r"C:\Users\49713\.openclaw\workspace\douyin_dialogues_D_tier"   # D级 (0-2分)

# 评分进度文件
PROGRESS_FILE = r"C:\Users\49713\.openclaw\workspace\scoring_progress.json"

# 评分标准
SCORING_PROMPT = """请作为一个专业的对话质量评估专家，对以下抖音视频对话内容进行评分。

评分标准（0-10分）：
1. **完整性** (0-3分)：对话是否完整，有开头、过程、结尾
2. **连贯性** (0-2分)：对话逻辑是否清晰，上下文是否连贯
3. **信息量** (0-2分)：是否包含有价值的信息或情节
4. **趣味性** (0-2分)：内容是否有趣、生动、吸引人
5. **实用性** (0-1分)：是否有学习、参考或娱乐价值

【对话内容】
{content}

请仔细阅读对话，然后返回一个JSON格式的评分结果：
{{
  "score": 7.5,
  "completeness": 2.5,
  "coherence": 2.0,
  "information": 1.5,
  "interest": 1.5,
  "utility": 0.0,
  "reason": "简短的评分理由（不超过50字）"
}}

只返回JSON，不要其他内容。"""

# ==================== 函数定义 ====================

def call_deepseek_api(content, max_retries=3):
    """调用 DeepSeek API 进行评分"""
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    prompt = SCORING_PROMPT.format(content=content[:2000])  # 限制长度避免超token
    
    data = {
        "model": MODEL,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 500
    }
    
    for attempt in range(max_retries):
        try:
            response = requests.post(
                f"{API_BASE}/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content'].strip()
                
                # 尝试解析 JSON
                # 有时 AI 会在前后加一些文字，需要提取 JSON 部分
                if '```json' in content:
                    content = content.split('```json')[1].split('```')[0].strip()
                elif '```' in content:
                    content = content.split('```')[1].split('```')[0].strip()
                
                # 移除可能的前后文字，只保留 {}
                start = content.find('{')
                end = content.rfind('}') + 1
                if start != -1 and end > start:
                    content = content[start:end]
                
                score_data = json.loads(content)
                return score_data
            
            elif response.status_code == 429:
                # 限流，等待后重试
                wait_time = (attempt + 1) * 5
                print(f"    限流，等待 {wait_time} 秒后重试...")
                time.sleep(wait_time)
            else:
                print(f"    API 错误 {response.status_code}: {response.text}")
                if attempt < max_retries - 1:
                    time.sleep(2)
        
        except json.JSONDecodeError as e:
            print(f"    JSON 解析失败: {e}")
            print(f"    原始响应: {content[:200]}")
            if attempt < max_retries - 1:
                time.sleep(2)
        
        except Exception as e:
            print(f"    请求失败: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(2)
    
    return None


def load_progress():
    """加载评分进度"""
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_progress(progress):
    """保存评分进度"""
    with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)


def main():
    print("=" * 80)
    print("使用 DeepSeek V3 API 对对话文档质量打分")
    print("=" * 80)
    
    # 检查 API Key
    if API_KEY == "YOUR_API_KEY_HERE":
        print("\n❌ 错误: 请先在脚本中填写你的硅基流动 API Key!")
        print("在脚本开头找到 API_KEY = \"YOUR_API_KEY_HERE\" 这一行")
        print("替换成你的真实 API Key")
        return
    
    # 创建输出目录
    os.makedirs(OUTPUT_DIR_S, exist_ok=True)
    os.makedirs(OUTPUT_DIR_A, exist_ok=True)
    os.makedirs(OUTPUT_DIR_B, exist_ok=True)
    os.makedirs(OUTPUT_DIR_C, exist_ok=True)
    os.makedirs(OUTPUT_DIR_D, exist_ok=True)
    
    # 加载进度
    progress = load_progress()
    print(f"\n已加载评分进度: {len(progress)} 个文档")
    
    # 获取所有文件
    files = sorted(Path(INPUT_DIR).glob('*.txt'))
    total = len(files)
    
    print(f"待处理文档: {total} 个")
    print(f"输入目录: {INPUT_DIR}")
    print(f"输出目录:")
    print(f"  S级 (9-10分): {OUTPUT_DIR_S}")
    print(f"  A级 (7-8分):  {OUTPUT_DIR_A}")
    print(f"  B级 (5-6分):  {OUTPUT_DIR_B}")
    print(f"  C级 (3-4分):  {OUTPUT_DIR_C}")
    print(f"  D级 (0-2分):  {OUTPUT_DIR_D}")
    print("\n" + "-" * 80)
    
    # 统计
    stats = {
        'S': 0,
        'A': 0,
        'B': 0,
        'C': 0,
        'D': 0,
        'failed': 0,
        'skipped': 0
    }
    
    for i, file in enumerate(files, 1):
        filename = file.name
        
        # 检查是否已评分
        if filename in progress:
            stats['skipped'] += 1
            score = progress[filename].get('score', 0)
            
            # 根据已有评分移动文件（如果还没移动）
            if file.exists():
                if score >= 9:
                    dest = os.path.join(OUTPUT_DIR_S, filename)
                    stats['S'] += 1
                elif score >= 7:
                    dest = os.path.join(OUTPUT_DIR_A, filename)
                    stats['A'] += 1
                elif score >= 5:
                    dest = os.path.join(OUTPUT_DIR_B, filename)
                    stats['B'] += 1
                elif score >= 3:
                    dest = os.path.join(OUTPUT_DIR_C, filename)
                    stats['C'] += 1
                else:
                    dest = os.path.join(OUTPUT_DIR_D, filename)
                    stats['D'] += 1
                
                if not os.path.exists(dest):
                    shutil.move(str(file), dest)
            
            if i % 50 == 0:
                print(f"[{i}/{total}] 跳过已评分文档...")
            continue
        
        # 读取文件内容
        try:
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"[{i}/{total}] ✗ 读取失败: {filename} - {e}")
            stats['failed'] += 1
            continue
        
        # 调用 API 评分
        print(f"[{i}/{total}] 评分中: {filename[:50]}...")
        score_data = call_deepseek_api(content)
        
        if score_data:
            score = score_data.get('score', 0)
            reason = score_data.get('reason', '')
            
            print(f"    ✓ 得分: {score:.1f}/10 - {reason}")
            
            # 保存进度
            progress[filename] = {
                'score': score,
                'details': score_data,
                'timestamp': time.time()
            }
            save_progress(progress)
            
            # 移动文件
            if score >= 9:
                dest = os.path.join(OUTPUT_DIR_S, filename)
                stats['S'] += 1
            elif score >= 7:
                dest = os.path.join(OUTPUT_DIR_A, filename)
                stats['A'] += 1
            elif score >= 5:
                dest = os.path.join(OUTPUT_DIR_B, filename)
                stats['B'] += 1
            elif score >= 3:
                dest = os.path.join(OUTPUT_DIR_C, filename)
                stats['C'] += 1
            else:
                dest = os.path.join(OUTPUT_DIR_D, filename)
                stats['D'] += 1
            
            shutil.move(str(file), dest)
            
            # 避免请求过快
            time.sleep(1)
        else:
            print(f"    ✗ 评分失败")
            stats['failed'] += 1
            # 失败的文档移到D级文件夹
            dest = os.path.join(OUTPUT_DIR_D, filename)
            shutil.move(str(file), dest)
    
    # 最终统计
    print("\n" + "=" * 80)
    print("评分完成！")
    print("=" * 80)
    print(f"S级 (9-10分): {stats['S']} 个 - 顶级优质内容")
    print(f"A级 (7-8分):  {stats['A']} 个 - 高质量内容")
    print(f"B级 (5-6分):  {stats['B']} 个 - 中等质量")
    print(f"C级 (3-4分):  {stats['C']} 个 - 较低质量")
    print(f"D级 (0-2分):  {stats['D']} 个 - 低质量")
    print(f"✗ 评分失败:   {stats['failed']} 个")
    print(f"→ 跳过(已评分): {stats['skipped']} 个")
    print("\n评分进度已保存到: " + PROGRESS_FILE)
    print("=" * 80)


if __name__ == "__main__":
    main()
