# 抖音短剧工具套件

一套完整的抖音短剧下载、转录、分析和优化工具链。

## 📦 项目结构

```
douyin-toolkit/
├── douyin-downloader/          # 抖音视频下载器（来自 GitHub）
│   ├── new.py                  # 批量下载脚本（从 urls.txt 读取）
│   └── ...                     # 其他下载器文件
├── extract_douyin_transcripts.py   # 使用 Whisper 提取视频转录文本
├── step1_collect_files.py      # 收集 FunASR 生成的文件
├── check_format.py             # 检查转录文件格式
├── collect_transcripts.py      # 将 FunASR 输出转换为可读台词本
├── score_dialogues_deepseek.py # 使用 DeepSeek 给台词本打分
├── dialogue_enhancer.py        # 优化台词本文档
├── format_json.py              # JSON 格式化工具
├── upload.py                   # 上传到 Dify 知识库（支持断点续传）
└── batch_process_docs.py       # 批量处理文档，生成创作方法论
```

## 🔄 完整工作流

### 1️⃣ 下载抖音视频

```bash
cd douyin-downloader
python new.py
```

- 从 `urls.txt` 读取抖音链接
- 批量下载视频到本地

### 2️⃣ 提取转录文本

#### 方法 A：使用 Whisper

```bash
python extract_douyin_transcripts.py
```

- 使用 OpenAI Whisper 模型
- 生成带时间戳的字幕文件

#### 方法 B：使用 FunASR（阿里达摩院）

如果使用 FunASR 生成转录，则运行：

```bash
python step1_collect_files.py  # 收集 FunASR 输出文件
python check_format.py         # 检查格式
python collect_transcripts.py  # 转换为台词本
```

### 3️⃣ 评分和优化

```bash
python score_dialogues_deepseek.py  # 给台词本打分（S/A/B/C 级）
python dialogue_enhancer.py         # 优化高分台词本
```

### 4️⃣ 上传到 Dify

```bash
python upload.py
```

- 支持断点续传
- 慢速上传模式（避免速率限制）
- 自动保存进度

### 5️⃣ 生成创作方法论

```bash
python batch_process_docs.py
```

- 分析所有台词本
- 提取高频关键词、冲突类型、场景模式
- 生成结构化的创作指南

## 🛠️ 依赖安装

```bash
pip install requests openai-whisper funasr python-dotenv
```

## 📝 配置说明

### API 配置

脚本中使用的 API：

- **DeepSeek API**（评分和分析）：`https://api.siliconflow.cn/v1`
- **Dify API**（知识库上传）：`http://www.azureflame.cloud/v1`

运行时需要输入对应的 API Key。

### URLs 文件格式

`douyin-downloader/urls.txt`：

```
https://www.douyin.com/video/1234567890
https://www.douyin.com/video/0987654321
...
```

## 📊 输出文件

- **转录文本**：`transcripts/` 或 FunASR 输出目录
- **评分结果**：各级台词本（S/A/B/C tier）
- **优化后文档**：`enhanced_dialogues/`
- **方法论**：`dify_knowledge/抖音短剧创作方法论_SA级.md`

## ⚠️ 注意事项

1. **磁盘空间**：视频下载需要较大空间
2. **API 配额**：注意 DeepSeek 和 Dify 的速率限制
3. **断点续传**：长时间任务可随时中断，下次继续

## 🤝 贡献

- `douyin-downloader`：基于 GitHub 开源项目
- 处理脚本：自定义工作流

## 📄 License

MIT License（自定义脚本部分）

---

**最后更新**: 2026-03-21
