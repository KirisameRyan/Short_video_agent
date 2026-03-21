# 快速开始指南

## 📦 安装

### 1. 克隆项目

```bash
git clone https://github.com/你的用户名/douyin-toolkit.git
cd douyin-toolkit
```

### 2. 安装 Python 依赖

```bash
pip install -r requirements.txt
```

### 3. 配置 douyin-downloader

```bash
cd douyin-downloader
# 首次运行会生成配置文件
python run.py
```

## 🚀 使用示例

### 场景 1：批量下载抖音视频

1. 准备链接列表 `douyin-downloader/urls.txt`：
```
https://www.douyin.com/video/7123456789
https://www.douyin.com/video/7987654321
```

2. 运行批量下载脚本：
```bash
cd douyin-downloader
python new.py
```

视频会保存到 `Downloaded/` 目录。

---

### 场景 2：提取视频字幕

#### 使用 Whisper（推荐用于英文/混合语言）

```bash
python extract_douyin_transcripts.py
```

程序会扫描视频目录，逐个提取字幕。

#### 使用 FunASR（推荐用于中文）

假设你已经用 FunASR 处理过视频，现在要整理输出：

```bash
# 第一步：收集 FunASR 输出文件
python step1_collect_files.py

# 第二步：检查文件格式
python check_format.py

# 第三步：转换为台词本
python collect_transcripts.py
```

---

### 场景 3：评估台词质量

```bash
python score_dialogues_deepseek.py
```

**需要准备**：
- 硅基流动 API Key
- 台词本文件（放在 `transcripts/` 目录）

**输出**：
- S 级（优秀）
- A 级（良好）
- B 级（一般）
- C 级（较差）

各级文档会分类存放。

---

### 场景 4：优化高质量台词本

```bash
python dialogue_enhancer.py
```

自动优化 S 级和 A 级台词本，输出到 `enhanced_dialogues/`。

---

### 场景 5：上传到 Dify 知识库

```bash
python upload.py
```

**需要准备**：
- Dify API Key
- Dataset ID

**特性**：
- 支持断点续传
- 慢速模式避免速率限制
- 自动保存进度

---

### 场景 6：生成创作方法论

```bash
python batch_process_docs.py
```

**输入**：优化后的台词本（`enhanced_dialogues/`）

**输出**：
- `文档结构化数据.json` - 结构化分析结果
- `抖音短剧创作方法论_SA级.md` - S+A 级方法论
- `抖音短剧创作方法论_全量.md` - 全量方法论

可直接上传到 Dify 作为创作指南。

---

## 🔧 常见问题

### Q1: Whisper 提取很慢怎么办？

使用更小的模型：

```python
# 在 extract_douyin_transcripts.py 中修改
model = whisper.load_model("base")  # 默认 "large"
```

可选模型（越小越快，准确度越低）：
- `tiny`
- `base`
- `small`
- `medium`
- `large`

### Q2: API 调用频繁报错？

降低请求频率：

```python
# 在脚本中增加 sleep 时间
time.sleep(2)  # 增加到 2 秒
```

### Q3: 如何恢复中断的任务？

大部分脚本支持断点续传：
- `upload.py` - 自动检测已上传文件
- `batch_process_docs.py` - 保存进度到 checkpoint

直接重新运行即可。

### Q4: 如何自定义评分标准？

编辑 `score_dialogues_deepseek.py` 中的 prompt：

```python
prompt = f"""你是短剧编剧专家，评估以下对话质量...
[自定义你的评分标准]
"""
```

---

## 📂 目录结构说明

```
douyin-toolkit/
├── douyin-downloader/          # 下载器（带大量子模块）
│   ├── new.py                  # ⭐ 你的批量下载脚本
│   ├── urls.txt                # 链接列表
│   └── Downloaded/             # 下载的视频
├── transcripts/                # 原始转录文本
├── enhanced_dialogues/         # 优化后的台词本
│   ├── S_tier_enhanced/
│   ├── A_tier_enhanced/
│   └── B_tier_enhanced/
├── dify_knowledge/             # 上传到 Dify 的文档
└── *.py                        # 处理脚本
```

---

## 🎯 完整工作流示例

假设你要从零开始处理 100 个抖音短剧：

```bash
# 1. 下载视频
cd douyin-downloader
echo "https://www.douyin.com/video/..." > urls.txt
python new.py

# 2. 提取字幕
cd ..
python extract_douyin_transcripts.py

# 3. 评分
python score_dialogues_deepseek.py
# 输入 API Key

# 4. 优化高分内容
python dialogue_enhancer.py

# 5. 生成方法论
python batch_process_docs.py

# 6. 上传到 Dify
python upload.py
# 输入 Dify API Key 和 Dataset ID
```

**预计时间**（100 个视频）：
- 下载：1-3 小时（取决于网速）
- 转录：2-5 小时（Whisper large 模型）
- 评分：30 分钟
- 优化：20 分钟
- 生成方法论：10 分钟
- 上传：30 分钟

---

## 🤝 贡献

欢迎提交 Issue 和 PR！

## 📧 联系

有问题？提交 GitHub Issue 或发邮件。

---

**Happy scripting! 🎬**
