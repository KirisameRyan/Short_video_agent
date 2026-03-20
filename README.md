# 🎬 短剧智能体 - AI剧本创作系统

> 华中科技大学首届 AI 智能体开发大赛 - 短剧智能体赛道参赛作品

## 📌 项目简介

本项目旨在通过 AI 智能体技术，让用户通过**自然语言交流**即可完成专业短剧和个人短视频的**故事创作**和**拍摄脚本编写**。系统结合了大语言模型、知识库检索、文生图技术，实现了从创意到成品剧本的全流程自动化。

**在线体验:** [点击体验短剧智能体](http://www.azureflame.cloud/chat/3x4mmLXbxsAQjDuc)

---

## ✨ 核心功能

### 🎯 智能剧本创作 (核心 ChatFlow)

通过五步对话流程，逐步完善剧本创作：

1. **需求理解** - 理解用户创作意图和题材方向
2. **故事构思** - 生成故事大纲和人物设定
3. **剧情细化** - 扩展场景描述和对话内容
4. **视觉设计** - 生成场景配图建议
5. **成品输出** - 生成带插图的 DOCX 格式剧本

**特色:**
- 🗣️ 自然语言交互，无需专业编剧知识
- 📊 结合 6 大专业知识库(剧本写作理论、视听语言、短视频爆款分析等)
- 🖼️ 自动生成场景配图，可视化剧本内容
- 📄 一键导出专业格式剧本文档

### 🔥 热点知识库自动更新

- **定时 Workflow** - 每日抓取热门话题、短视频趋势
- **自动入库** - 新鲜素材实时补充到知识库
- **灵感源泉** - 为剧本创作提供时下热点参考

### 🎨 文生图插件

- **自研插件** - 基于 Stable Diffusion / DALL-E 的文生图能力
- **场景可视化** - 根据剧本描述自动生成场景概念图
- **独立 Workflow** - 可单独调用进行图片生成

---

## 🏗️ 技术架构

### 基础平台
- **Dify** - AI 应用开发平台 ([Apache 2.0 License](https://github.com/langgenius/dify))
- **Docker** - 容器化部署
- **PostgreSQL** - 关系数据库（存储聊天历史）
- **Redis** - 缓存层
- **Weaviate** - 向量数据库（知识库检索）

### AI 能力
- **LLM** - 大语言模型（OpenAI / Claude / 通义千问等）
- **Embedding** - 文本向量化（知识库召回）
- **Text-to-Image** - 文生图模型（场景配图）

### 知识库体系

| 知识库 | 内容 | 用途 |
|--------|------|------|
| 剧本写作理论 | 三幕式结构、人物弧光等 | 指导故事结构 |
| 视听语言 | 镜头语言、蒙太奇手法 | 优化场景描述 |
| 短视频爆款分析 | 抖音快手热门内容规律 | 提升传播力 |
| 对话写作技巧 | 经典台词、情感表达 | 优化角色对话 |
| 热点话题库 | 实时更新的社会热点 | 灵感来源 |
| 历史剧本库 | 过往生成的优秀剧本 | 风格参考 |

---

## 🚀 快速开始

### 环境要求
- Docker 20.10+
- Docker Compose 2.0+
- 8GB+ 内存
- 50GB+ 磁盘空间

### 部署步骤

```bash
# 1. 克隆项目
git clone https://github.com/KirisameRyan/Short_video_agent.git
cd Short_video_agent

# 2. 配置环境变量
cp docker/.env.example docker/.env
# 编辑 docker/.env，填入你的 API Keys

# 3. 启动服务
cd docker
docker-compose up -d

# 4. 访问服务
# Web UI: http://localhost:80
# API: http://localhost:80/api
```

### 配置说明

关键环境变量：

```bash
# LLM 配置
OPENAI_API_KEY=your_openai_api_key
OPENAI_API_BASE=https://api.openai.com/v1

# 文生图配置
STABLE_DIFFUSION_API_KEY=your_sd_key
IMAGE_MODEL=dall-e-3

# 数据库
POSTGRES_PASSWORD=your_secure_password
```

---

## 📂 项目结构

```
Short_video_agent/
├── api/                    # 后端 API
│   ├── core/              # 核心业务逻辑
│   ├── extensions/        # 扩展插件（包含文生图插件）
│   └── workflows/         # Workflow 定义
├── web/                   # 前端界面
├── docker/                # Docker 配置
│   ├── docker-compose.yaml
│   └── .env.example
├── scripts/               # 数据处理脚本
│   ├── douyin_downloader.py      # 抖音视频下载
│   ├── transcript_extractor.py   # 台词提取
│   ├── content_scorer.py          # 内容评分
│   └── data_formatter.py          # 数据格式化
├── knowledge_base/        # 知识库原始数据
└── docs/                  # 项目文档
```

---

## 🎨 核心 Workflow 说明

### 1. 剧本创作 ChatFlow

**流程图:**

```
用户输入 → 需求分析 → 故事大纲生成 → 剧情扩展 → 场景配图 → 格式化输出 → DOCX 剧本
           ↓           ↓             ↓          ↓          ↓
        知识库召回   知识库召回    知识库召回  文生图插件  文档生成器
```

**关键节点:**
- **条件分支** - 根据用户反馈决定修改方向
- **循环节点** - 支持多轮优化剧本内容
- **并行处理** - 同时生成多个场景的配图
- **LLM 调用** - 使用 GPT-4 级别模型保证创作质量

### 2. 热点更新 Workflow

**触发方式:** Cron 定时任务（每日凌晨 2:00）

**流程:**
1. 爬取抖音/快手/微博热搜
2. 内容清洗和去重
3. 提取关键信息和情感标签
4. 向量化并存入 Weaviate
5. 发送更新报告（Webhook）

### 3. 文生图 Workflow

**输入:** 场景描述文本  
**输出:** 场景概念图（PNG/JPG）

**优化点:**
- Prompt 工程 - 自动优化用户输入为高质量提示词
- 风格一致性 - 维护项目整体视觉风格
- 快速生成 - 平均 8-10 秒出图

---

## 💡 创新亮点

### 1. 五步对话式创作法
不同于传统"一键生成"，采用渐进式引导，让 AI 更好理解创作意图。

### 2. 动态知识库
热点自动更新机制确保创作内容紧跟时代潮流，避免 AI 幻觉和过时信息。

### 3. 文生图深度集成
不仅是工具调用，而是将图像生成融入创作流程，提升剧本的可视化程度。

### 4. 历史数据学习
数据库记录所有对话历史，为未来的自我学习和风格适应打下基础。

### 5. 数据驱动的内容优化
基于真实抖音数据分析（scripts/ 目录），提取优质剧本特征反哺创作。

---

## 📊 数据处理流程

项目包含完整的数据采集和处理管道：

```
抖音视频 → 下载 → 提取台词 → 情感分析 → 质量评分 → 格式化存储 → 知识库
(scripts/douyin_downloader.py)  (transcript_extractor.py)  (content_scorer.py)  (data_formatter.py)
```

### 数据处理脚本

- **douyin_downloader.py** - 批量下载抖音热门短剧视频
- **transcript_extractor.py** - 使用 Whisper 提取视频台词
- **content_scorer.py** - 基于多维度（情节、对话、节奏）打分
- **data_formatter.py** - 统一格式化为知识库可用的 JSON/CSV

---

## 🎥 演示

**在线体验:** [http://www.azureflame.cloud/chat/3x4mmLXbxsAQjDuc](http://www.azureflame.cloud/chat/3x4mmLXbxsAQjDuc)

**功能展示:**
- 通过自然对话创作短剧剧本
- 实时查看知识库检索结果
- 文生图插件生成场景配图
- 一键导出带插图的 DOCX 剧本

---

## 🛠️ 开发计划

- [ ] 自我学习模块 - 基于用户反馈优化创作风格
- [ ] 多模态输入 - 支持上传图片/视频作为灵感素材
- [ ] 语音交互 - 语音输入剧本需求
- [ ] 协作模式 - 多人共同编辑剧本
- [ ] 导演模式 - 生成分镜头脚本和拍摄指南
- [ ] 视频预览 - 基于剧本生成视频预览动画

---

## 📄 开源协议

本项目基于 [Dify](https://github.com/langgenius/dify) 开发，遵循 **Apache 2.0 License**。

- 原项目: https://github.com/langgenius/dify
- 二次开发: 华中科技大学 AI 智能体开发大赛参赛团队

---

## 👥 团队成员

**[你的名字/团队名称]**

- 项目负责人: [姓名]
- 技术架构: [姓名]
- 产品设计: [姓名]
- 数据工程: [姓名]

---

## 📞 联系方式

- **在线体验:** [http://www.azureflame.cloud/chat/3x4mmLXbxsAQjDuc](http://www.azureflame.cloud/chat/3x4mmLXbxsAQjDuc)
- **GitHub:** https://github.com/KirisameRyan/Short_video_agent
- **邮箱:** 2167145170@qq.com

---

## 🙏 致谢

- [Dify](https://github.com/langgenius/dify) - 提供强大的 AI 应用开发平台
- [OpenAI](https://openai.com) - GPT 系列模型支持
- 华中科技大学 - 提供比赛平台和技术支持
- 所有测试用户 - 提供宝贵的反馈意见

---

<p align="center">
  <b>🏆 华中科技大学首届 AI 智能体开发大赛 · 短剧智能体赛道</b>
</p>

<p align="center">
  <i>让 AI 成为每个人的专业编剧</i>
</p>
