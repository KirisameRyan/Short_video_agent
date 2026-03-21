# GitHub 上传指南

## 📋 准备工作

### 1. 确保已安装 Git

打开 PowerShell/CMD，检查：

```bash
git --version
```

如果未安装，下载：https://git-scm.com/download/win

### 2. 配置 Git 用户信息（首次使用）

```bash
git config --global user.name "你的GitHub用户名"
git config --global user.email "你的邮箱@example.com"
```

## 🚀 上传到 GitHub

### 方法一：通过命令行（推荐）

#### Step 1: 进入项目目录

```bash
cd D:\douyin-toolkit
```

#### Step 2: 初始化 Git 仓库

```bash
git init
```

#### Step 3: 添加所有文件

```bash
git add .
```

#### Step 4: 查看即将提交的文件

```bash
git status
```

检查是否有不该提交的文件（`.gitignore` 应该已经排除了它们）。

#### Step 5: 创建首次提交

```bash
git commit -m "Initial commit: 抖音短剧工具套件"
```

#### Step 6: 在 GitHub 创建仓库

1. 访问：https://github.com/new
2. 仓库名：`douyin-toolkit`（或其他你喜欢的名字）
3. 描述：`抖音短剧下载、转录、分析和优化工具链`
4. 选择：**Public**（公开）或 **Private**（私有）
5. **不要**勾选 "Initialize with README"
6. 点击 **Create repository**

#### Step 7: 关联远程仓库

复制 GitHub 显示的 URL（类似 `https://github.com/你的用户名/douyin-toolkit.git`），然后：

```bash
git remote add origin https://github.com/你的用户名/douyin-toolkit.git
```

#### Step 8: 推送到 GitHub

```bash
git branch -M main
git push -u origin main
```

如果提示输入用户名和密码：
- **用户名**：你的 GitHub 用户名
- **密码**：GitHub Personal Access Token（不是登录密码！）

> 💡 **获取 Token**：GitHub 设置 → Developer settings → Personal access tokens → Generate new token

---

### 方法二：通过 GitHub Desktop（适合新手）

#### Step 1: 下载 GitHub Desktop

https://desktop.github.com/

#### Step 2: 登录 GitHub 账号

打开 GitHub Desktop，登录。

#### Step 3: 添加本地仓库

1. 点击 **File → Add local repository**
2. 选择路径：`D:\douyin-toolkit`
3. 如果提示未初始化，点击 **create a repository**

#### Step 4: 创建首次提交

1. 左下角填写 commit 信息：`Initial commit: 抖音短剧工具套件`
2. 点击 **Commit to main**

#### Step 5: 发布到 GitHub

1. 点击顶部 **Publish repository**
2. 填写仓库名和描述
3. 选择公开或私有
4. 点击 **Publish**

完成！

---

## 🔒 敏感信息检查

在推送前，务必确认以下文件**没有**被提交：

- ❌ `.cookies.json` - 登录凭证
- ❌ `config.yml` - 可能包含密钥
- ❌ `urls.txt` - 你的私人链接
- ❌ `*.db` - 数据库文件
- ❌ `Downloaded/` - 下载的视频

`.gitignore` 已经配置好了，但请再次确认：

```bash
git status
```

如果发现敏感文件，添加到 `.gitignore`：

```bash
echo "敏感文件.txt" >> .gitignore
git add .gitignore
git commit -m "更新 .gitignore"
```

---

## 📝 后续更新

当你修改代码后，推送更新：

```bash
# 1. 查看改动
git status

# 2. 添加改动的文件
git add .

# 3. 提交
git commit -m "描述你的改动"

# 4. 推送
git push
```

---

## 🎨 美化 GitHub 仓库

### 添加 Topics（标签）

在 GitHub 仓库页面，点击右侧 **About → Topics**，添加：

- `douyin`
- `short-drama`
- `video-downloader`
- `whisper`
- `ai-analysis`
- `content-creation`

### 设置仓库描述

在 **About** 中填写：

> 🎬 抖音短剧工具套件：下载、转录、评分、优化和创作辅助的完整工作流

### 添加 Logo

如果你有项目 Logo，可以上传到 `assets/logo.png`，然后在 README.md 顶部添加：

```markdown
<div align="center">
  <img src="assets/logo.png" alt="Logo" width="200">
  <h1>抖音短剧工具套件</h1>
</div>
```

---

## 🔗 分享你的项目

完成上传后，你的项目地址：

```
https://github.com/你的用户名/douyin-toolkit
```

可以分享给：
- 同行创作者
- 开发者社区
- 技术论坛

---

## ❓ 常见问题

### Q: 推送时提示 "Permission denied"

**解决**：使用 SSH 密钥或 Personal Access Token。

推荐用 Token：
1. GitHub → Settings → Developer settings → Tokens
2. Generate new token (classic)
3. 勾选 `repo` 权限
4. 复制 token
5. 推送时输入 token 作为密码

### Q: 不小心提交了敏感文件怎么办？

**解决**：

```bash
# 从 Git 历史中删除（保留本地文件）
git rm --cached 敏感文件.txt

# 提交删除操作
git commit -m "移除敏感文件"

# 强制推送（覆盖远程历史）
git push --force
```

⚠️ **注意**：强制推送会修改历史，谨慎操作！

### Q: 仓库太大无法推送？

GitHub 限制单个文件 100MB。

**解决**：

1. 排除大文件（如视频、数据库）
2. 使用 Git LFS（大文件存储）

```bash
git lfs install
git lfs track "*.mp4"
git add .gitattributes
```

---

**祝上传顺利！🎉**
