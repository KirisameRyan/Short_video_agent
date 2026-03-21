# -*- coding: utf-8 -*-
"""
抖音视频批量语音转文字脚本
使用 Whisper 提取所有视频的台词
"""

import os
import json
import whisper
from pathlib import Path
from datetime import datetime

# 配置
BASE_DIR = r"D:\迅雷下载\douyin-downloader-main\douyin-downloader-main\Downloaded"
MANIFEST_FILE = os.path.join(BASE_DIR, "download_manifest.jsonl")
OUTPUT_DIR = r"C:\Users\49713\.openclaw\workspace\douyin_transcripts"
PROGRESS_FILE = os.path.join(OUTPUT_DIR, "progress.json")

# 创建输出目录
os.makedirs(OUTPUT_DIR, exist_ok=True)

def load_progress():
    """加载处理进度"""
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"processed": [], "failed": [], "last_index": 0}

def save_progress(progress):
    """保存处理进度"""
    with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)

def main():
    print("=" * 80)
    print("抖音视频批量语音转文字工具")
    print("=" * 80)
    
    # 加载进度
    progress = load_progress()
    processed_ids = set(progress["processed"])
    
    # 加载 Whisper 模型
    print("\n正在加载 Whisper 模型（首次运行会下载模型，约 1.5GB）...")
    print("建议使用 'base' 或 'small' 模型（速度快）")
    print("如需更高准确度，可选 'medium' 或 'large'")
    
    model_size = input("\n请选择模型大小 (tiny/base/small/medium/large) [默认: base]: ").strip().lower()
    if not model_size:
        model_size = "base"
    
    try:
        model = whisper.load_model(model_size)
        print(f"✅ 模型 '{model_size}' 加载成功！")
    except Exception as e:
        print(f"❌ 模型加载失败: {e}")
        return
    
    # 读取视频清单
    print(f"\n正在读取视频清单: {MANIFEST_FILE}")
    videos = []
    with open(MANIFEST_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            video = json.loads(line)
            if video["aweme_id"] not in processed_ids:
                videos.append(video)
    
    total = len(videos)
    print(f"✅ 共有 {total} 个视频待处理")
    
    if total == 0:
        print("所有视频都已处理完成！")
        return
    
    # 询问是否继续
    confirm = input(f"\n是否开始处理 {total} 个视频？(y/n): ").strip().lower()
    if confirm != 'y':
        print("已取消")
        return
    
    # 批量处理
    print("\n" + "=" * 80)
    print("开始处理...")
    print("=" * 80)
    
    for i, video in enumerate(videos, 1):
        aweme_id = video["aweme_id"]
        author = video["author_name"]
        desc = video["desc"]
        date = video["date"]
        
        # 构建视频文件路径
        video_path = os.path.join(BASE_DIR, video["file_paths"][0])
        
        print(f"\n[{i}/{total}] 处理中...")
        print(f"  作者: {author}")
        print(f"  描述: {desc[:50]}...")
        print(f"  文件: {os.path.basename(video_path)}")
        
        if not os.path.exists(video_path):
            print(f"  ⚠️ 文件不存在，跳过")
            progress["failed"].append({
                "aweme_id": aweme_id,
                "reason": "文件不存在",
                "path": video_path
            })
            save_progress(progress)
            continue
        
        try:
            # 使用 Whisper 转录
            print(f"  🎤 正在识别语音...")
            result = model.transcribe(
                video_path,
                language="zh",  # 中文
                verbose=False
            )
            
            transcript = result["text"].strip()
            
            if not transcript:
                print(f"  ⚠️ 未识别到语音内容")
                progress["failed"].append({
                    "aweme_id": aweme_id,
                    "reason": "无语音内容"
                })
            else:
                print(f"  ✅ 识别成功！")
                print(f"  📝 内容: {transcript[:80]}...")
                
                # 保存转录结果
                output_data = {
                    "aweme_id": aweme_id,
                    "author": author,
                    "date": date,
                    "description": desc,
                    "transcript": transcript,
                    "segments": result.get("segments", []),
                    "video_file": video["file_names"][0],
                    "processed_at": datetime.now().isoformat()
                }
                
                output_file = os.path.join(OUTPUT_DIR, f"{aweme_id}.json")
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(output_data, f, ensure_ascii=False, indent=2)
                
                progress["processed"].append(aweme_id)
            
            progress["last_index"] = i
            save_progress(progress)
            
        except Exception as e:
            print(f"  ❌ 处理失败: {e}")
            progress["failed"].append({
                "aweme_id": aweme_id,
                "reason": str(e)
            })
            save_progress(progress)
    
    # 生成汇总报告
    print("\n" + "=" * 80)
    print("处理完成！生成汇总报告...")
    print("=" * 80)
    
    generate_summary_report()

def generate_summary_report():
    """生成汇总报告"""
    progress = load_progress()
    
    # 读取所有转录结果
    transcripts = []
    for aweme_id in progress["processed"]:
        json_file = os.path.join(OUTPUT_DIR, f"{aweme_id}.json")
        if os.path.exists(json_file):
            with open(json_file, 'r', encoding='utf-8') as f:
                transcripts.append(json.load(f))
    
    # 生成 Markdown 汇总
    report_lines = []
    report_lines.append("# 抖音视频语音转文字汇总")
    report_lines.append(f"\n生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append(f"\n- 成功处理: **{len(progress['processed'])}** 个视频")
    report_lines.append(f"- 处理失败: **{len(progress['failed'])}** 个视频")
    report_lines.append("\n" + "=" * 80 + "\n")
    
    for i, t in enumerate(transcripts, 1):
        report_lines.append(f"## 视频 {i}: {t['description'][:50]}")
        report_lines.append(f"\n- **作者**: {t['author']}")
        report_lines.append(f"- **日期**: {t['date']}")
        report_lines.append(f"- **抖音ID**: {t['aweme_id']}")
        report_lines.append(f"\n### 📝 台词内容：")
        report_lines.append(f"\n{t['transcript']}")
        report_lines.append("\n" + "-" * 80 + "\n")
    
    # 保存报告
    report_file = os.path.join(OUTPUT_DIR, "transcripts_summary.md")
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_lines))
    
    print(f"\n✅ 汇总报告已保存: {report_file}")
    print(f"✅ 转录结果JSON文件保存在: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
