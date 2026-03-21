#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量处理短剧文档，提取结构化信息并生成方法论
支持断点续传
"""

from pathlib import Path
import requests
import json
import time
from datetime import datetime

# API 配置
API_BASE_URL = "https://api.siliconflow.cn/v1"
MODEL_NAME = "deepseek-ai/DeepSeek-V3"

TIER_DIRS = {
    "S": "enhanced_dialogues/S_tier_enhanced",
    "A": "enhanced_dialogues/A_tier_enhanced",
    "B": "enhanced_dialogues/B_tier_enhanced"
}

# 断点续传文件
CHECKPOINT_FILE = "processing_checkpoint.json"
OUTPUT_DIR = Path("dify_knowledge")

def load_checkpoint():
    """加载断点数据"""
    checkpoint_path = OUTPUT_DIR / CHECKPOINT_FILE
    if checkpoint_path.exists():
        with open(checkpoint_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"processed_files": [], "all_docs": []}

def save_checkpoint(processed_files: list, all_docs: list):
    """保存断点数据"""
    OUTPUT_DIR.mkdir(exist_ok=True)
    checkpoint_path = OUTPUT_DIR / CHECKPOINT_FILE
    with open(checkpoint_path, 'w', encoding='utf-8') as f:
        json.dump({
            "processed_files": processed_files,
            "all_docs": all_docs,
            "last_update": datetime.now().isoformat()
        }, f, ensure_ascii=False, indent=2)

def call_deepseek(prompt: str, api_key: str, max_tokens: int = 2000) -> str:
    """调用 DeepSeek API"""
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3,
        "max_tokens": max_tokens
    }
    
    for attempt in range(3):
        try:
            response = requests.post(
                f"{API_BASE_URL}/chat/completions",
                headers=headers,
                json=payload,
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"].strip()
            elif response.status_code == 429:
                wait_time = 2 * (attempt + 1)
                print(f"      [速率限制] 等待 {wait_time} 秒...")
                time.sleep(wait_time)
            else:
                print(f"      [WARN] API {response.status_code}")
                if attempt < 2:
                    time.sleep(2)
        
        except Exception as e:
            print(f"      [WARN] {e}")
            if attempt < 2:
                time.sleep(2)
    
    return ""

def extract_document_info(content: str, filename: str, api_key: str) -> dict:
    """提取单个文档的结构化信息"""
    
    prompt = f"""分析以下抖音短剧对话文档，提取结构化信息。

文档内容：
```
{content[:1500]}
```

请以 JSON 格式输出（只输出JSON，不要其他文字）：
{{
  "title": "文档的核心主题（5-10字）",
  "outline": ["大纲要点1", "大纲要点2", "大纲要点3"],
  "keywords": ["关键词1", "关键词2", "关键词3", "关键词4", "关键词5"],
  "scene_types": ["场景类型1", "场景类型2"],
  "character_types": ["角色类型1", "角色类型2"],
  "conflict_type": "冲突类型（如：身份反转/情感虐心/复仇打脸）",
  "structure_pattern": "结构模式（如：三段式/悬念式）"
}}"""

    response = call_deepseek(prompt, api_key, max_tokens=800)
    
    try:
        # 提取 JSON
        if "```json" in response:
            json_str = response.split("```json")[1].split("```")[0].strip()
        elif "```" in response:
            json_str = response.split("```")[1].split("```")[0].strip()
        else:
            json_str = response.strip()
        
        data = json.loads(json_str)
        data["filename"] = filename
        return data
    
    except Exception as e:
        print(f"      [ERROR] 解析失败: {e}")
        return {
            "filename": filename,
            "title": "解析失败",
            "outline": [],
            "keywords": [],
            "scene_types": [],
            "character_types": [],
            "conflict_type": "未知",
            "structure_pattern": "未知"
        }

def process_tier(tier_name: str, tier_dir: str, api_key: str, checkpoint_data: dict):
    """处理某个等级的所有文档（支持断点续传）"""
    
    input_dir = Path(tier_dir)
    if not input_dir.exists():
        print(f"[SKIP] 目录不存在: {tier_dir}")
        return []
    
    files = sorted(input_dir.glob("*.txt"))
    total = len(files)
    
    processed_files = checkpoint_data.get("processed_files", [])
    
    print(f"\n{'='*60}")
    print(f"处理 {tier_name} 级文档")
    print(f"总文件数: {total}")
    print(f"已处理: {len([f for f in processed_files if tier_name in f])}")
    print(f"{'='*60}\n")
    
    results = []
    processed_count = 0
    skipped_count = 0
    
    for idx, file_path in enumerate(files, 1):
        file_key = f"{tier_name}:{file_path.name}"
        
        # 检查是否已处理
        if file_key in processed_files:
            skipped_count += 1
            if idx % 20 == 0:
                print(f"[{idx}/{total}] 已跳过 {skipped_count} 个文件...")
            continue
        
        print(f"[{idx}/{total}] 处理: {file_path.name[:40]}...")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            
            if not content:
                print("      [SKIP] 空文件")
                processed_files.append(file_key)
                continue
            
            doc_info = extract_document_info(content, file_path.name, api_key)
            doc_info["tier"] = tier_name
            doc_info["content_length"] = len(content)
            
            results.append(doc_info)
            processed_files.append(file_key)
            processed_count += 1
            
            print(f"      [OK] {doc_info.get('title', '未知')}")
            
            # 每处理5个文件保存一次断点
            if processed_count % 5 == 0:
                all_existing_docs = checkpoint_data.get("all_docs", [])
                all_existing_docs.extend(results)
                save_checkpoint(processed_files, all_existing_docs)
                results = []  # 清空临时列表
                print(f"      [保存] 断点已更新（已处理 {processed_count} 个新文件）")
            
            # 避免频繁请求
            time.sleep(0.8)
        
        except Exception as e:
            print(f"      [ERROR] {e}")
    
    # 保存剩余的结果
    if results:
        all_existing_docs = checkpoint_data.get("all_docs", [])
        all_existing_docs.extend(results)
        save_checkpoint(processed_files, all_existing_docs)
    
    print(f"\n[统计] {tier_name}级: 新处理 {processed_count} 个，跳过 {skipped_count} 个")
    
    return checkpoint_data.get("all_docs", [])

def generate_methodology(all_docs: list, tier_filter: str, api_key: str) -> str:
    """生成方法论"""
    
    filtered_docs = [d for d in all_docs if d.get("tier") in tier_filter.split("+")]
    
    print(f"\n生成 {tier_filter} 方法论...")
    print(f"基于 {len(filtered_docs)} 个文档")
    
    # 统计分析
    all_keywords = []
    all_conflicts = []
    all_scenes = []
    all_characters = []
    
    for doc in filtered_docs:
        all_keywords.extend(doc.get("keywords", []))
        all_conflicts.append(doc.get("conflict_type", ""))
        all_scenes.extend(doc.get("scene_types", []))
        all_characters.extend(doc.get("character_types", []))
    
    from collections import Counter
    top_keywords = Counter(all_keywords).most_common(20)
    top_conflicts = Counter(all_conflicts).most_common(10)
    top_scenes = Counter(all_scenes).most_common(15)
    top_characters = Counter(all_characters).most_common(15)
    
    # 生成方法论
    summary_data = {
        "文档数量": len(filtered_docs),
        "高频关键词": [{"词": k, "频次": v} for k, v in top_keywords],
        "高频冲突类型": [{"类型": k, "频次": v} for k, v in top_conflicts if k],
        "高频场景": [{"场景": k, "频次": v} for k, v in top_scenes if k],
        "高频角色": [{"角色": k, "频次": v} for k, v in top_characters if k]
    }
    
    methodology_prompt = f"""你是短剧创作专家。基于以下数据分析，生成一套系统化的**抖音短剧创作方法论**（Markdown格式）。

数据统计：
{json.dumps(summary_data, ensure_ascii=False, indent=2)}

样本文档大纲（前10个）：
{json.dumps([{{"标题": d.get("title"), "大纲": d.get("outline"), "冲突类型": d.get("conflict_type")}} for d in filtered_docs[:10]], ensure_ascii=False, indent=2)}

要求输出：
1. **核心方法论**（3-5条最重要的创作原则）
2. **场景设计指南**（基于高频场景数据）
3. **角色塑造技巧**（基于高频角色数据）
4. **冲突类型模板**（基于高频冲突类型）
5. **关键词库**（高频关键词的使用场景）
6. **创作检查清单**

输出格式：Markdown，简洁实用，便于 AI 学习。"""

    methodology_content = call_deepseek(methodology_prompt, api_key, max_tokens=6000)
    
    return methodology_content

def main():
    """主函数"""
    
    print("\n" + "="*60)
    print("抖音短剧文档批量处理 & 方法论生成 v2.0")
    print("支持断点续传")
    print("="*60 + "\n")
    
    # 加载断点数据
    checkpoint_data = load_checkpoint()
    
    if checkpoint_data.get("all_docs"):
        print(f"[发现断点] 已有 {len(checkpoint_data['all_docs'])} 个文档数据")
        print(f"[上次更新] {checkpoint_data.get('last_update', '未知')}")
        resume = input("\n是否继续上次的进度？(y/n): ").strip().lower()
        if resume != 'y':
            print("[重新开始] 清除断点数据")
            checkpoint_data = {"processed_files": [], "all_docs": []}
    
    api_key = input("\n请输入硅基流动 API Key: ").strip()
    if not api_key:
        print("[ERROR] API Key 不能为空")
        return
    
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    # 第一步：处理所有文档
    print("\n" + "="*60)
    print("[阶段 1] 提取文档结构信息")
    print("="*60)
    
    try:
        # 处理 S 级
        all_docs = process_tier("S", TIER_DIRS["S"], api_key, checkpoint_data)
        checkpoint_data["all_docs"] = all_docs
        
        # 处理 A 级
        all_docs = process_tier("A", TIER_DIRS["A"], api_key, checkpoint_data)
        checkpoint_data["all_docs"] = all_docs
        
        # 处理 B 级（如果存在）
        all_docs = process_tier("B", TIER_DIRS["B"], api_key, checkpoint_data)
        checkpoint_data["all_docs"] = all_docs
        
    except KeyboardInterrupt:
        print("\n\n[中断] 已保存进度，下次运行可继续")
        return
    except Exception as e:
        print(f"\n[ERROR] 处理失败: {e}")
        print("[提示] 进度已保存，可重新运行继续")
        return
    
    # 统计
    s_count = len([d for d in all_docs if d.get("tier") == "S"])
    a_count = len([d for d in all_docs if d.get("tier") == "A"])
    b_count = len([d for d in all_docs if d.get("tier") == "B"])
    
    # 保存结构化数据
    json_file = OUTPUT_DIR / "文档结构化数据.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump({
            "生成时间": datetime.now().isoformat(),
            "总文档数": len(all_docs),
            "S级": s_count,
            "A级": a_count,
            "B级": b_count,
            "文档列表": all_docs
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n[完成] 结构化数据已保存: {json_file}")
    
    # 第二步：生成方法论
    print("\n" + "="*60)
    print("[阶段 2] 生成创作方法论")
    print("="*60)
    
    # S+A 方法论
    print("\n[1/2] 生成 S+A 级方法论...")
    sa_methodology = generate_methodology(all_docs, "S+A", api_key)
    
    sa_file = OUTPUT_DIR / "抖音短剧创作方法论_SA级.md"
    with open(sa_file, 'w', encoding='utf-8') as f:
        f.write(f"# 抖音短剧创作方法论（S+A级）\n\n")
        f.write(f"> 基于 {s_count + a_count} 个高质量案例\n")
        f.write(f"> 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
        f.write("---\n\n")
        f.write(sa_methodology)
    
    print(f"[完成] {sa_file}")
    
    # S+A+B 方法论
    if b_count > 0:
        print("\n[2/2] 生成 S+A+B 级方法论...")
        sab_methodology = generate_methodology(all_docs, "S+A+B", api_key)
        
        sab_file = OUTPUT_DIR / "抖音短剧创作方法论_全量.md"
        with open(sab_file, 'w', encoding='utf-8') as f:
            f.write(f"# 抖音短剧创作方法论（全量）\n\n")
            f.write(f"> 基于 {len(all_docs)} 个案例（S:{s_count} A:{a_count} B:{b_count}）\n")
            f.write(f"> 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
            f.write("---\n\n")
            f.write(sab_methodology)
        
        print(f"[完成] {sab_file}")
    
    # 清除断点文件
    checkpoint_path = OUTPUT_DIR / CHECKPOINT_FILE
    if checkpoint_path.exists():
        checkpoint_path.unlink()
        print(f"\n[清理] 已删除断点文件")
    
    # 总结
    print("\n" + "="*60)
    print("全部完成！")
    print("\n生成的文件：")
    print(f"  1. {json_file.name} - 结构化数据（{len(all_docs)} 个文档）")
    print(f"  2. {sa_file.name} - S+A级方法论（{s_count + a_count} 个案例）")
    if b_count > 0:
        print(f"  3. {sab_file.name} - 全量方法论（{len(all_docs)} 个案例）")
    print("\nDify 上传建议：")
    print("  - 上传方法论 MD 文件到「创作指南」知识库")
    print("  - JSON 文件可用于结构化检索")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
