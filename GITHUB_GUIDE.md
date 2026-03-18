# 🚀 GitHub 自动打包三个平台版本

## 📋 操作步骤（5 分钟）

### 第 1 步：创建 GitHub 仓库

1. 访问 https://github.com/new
2. 仓库名称：`openclaw-deploy-tool`
3. 设为私有（推荐）或公开
4. 不要初始化 README
5. 点击"Create repository"

---

### 第 2 步：准备本地代码

```bash
# 进入项目目录
cd /home/long/.openclaw/workspace/openclaw-deploy-service

# 初始化 Git
git init

# 添加所有文件
git add .

# 提交
git commit -m "Initial commit"
```

---

### 第 3 步：连接到 GitHub

```bash
# 添加远程仓库（替换为你的用户名）
git remote add origin https://github.com/你的用户名/openclaw-deploy-tool.git

# 推送代码
git branch -M main
git push -u origin main
```

---

### 第 4 步：触发自动打包

#### 方法 A：推送标签（推荐）

```bash
# 打标签
git tag v1.0.0

# 推送标签
git push origin v1.0.0
```

#### 方法 B：手动触发

1. 打开 GitHub 仓库
2. 点击 "Actions" 标签
3. 选择 "Build OpenClaw Deploy Tool"
4. 点击 "Run workflow"
5. 选择分支（main）
6. 点击 "Run workflow"

---

### 第 5 步：下载打包好的文件

等待 3-5 分钟后：

1. 打开 GitHub 仓库
2. 点击 "Actions" 标签
3. 点击最新的 "Build OpenClaw Deploy Tool" 运行
4. 滚动到底部的 "Artifacts" 部分
5. 下载三个文件：
   - `OpenClaw-部署工具-linux` (Linux 版本)
   - `OpenClaw-部署工具.exe` (Windows 版本)
   - `OpenClaw-部署工具-mac` (Mac 版本)

---

## 🎉 完成！

现在你有三个平台的打包文件了：
- `OpenClaw-部署工具.exe` - Windows（99% 客户用）
- `OpenClaw-部署工具-linux` - Linux（服务器部署）
- `OpenClaw-部署工具-mac` - Mac（少数用户）

上传到网盘，发给客户就行了！

---

## 🔄 以后更新版本

只需要：

```bash
# 修改代码
# ...

# 提交
git add .
git commit -m "Update version"

# 打新标签
git tag v1.1.0
git push origin v1.1.0
```

GitHub 会自动打包三个新版本！

---

## ⚠️ 注意事项

1. **首次推送需要登录**
   - 如果没有 SSH key，用 HTTPS：
   ```bash
   git remote add origin https://github.com/你的用户名/openclaw-deploy-tool.git
   ```

2. **推送时需要 GitHub 账号密码**
   - 用户名：你的 GitHub 用户名
   - 密码：使用 Personal Access Token（不是登录密码）
   - 获取 Token：https://github.com/settings/tokens

3. **打包需要 3-5 分钟**
   - Windows 版本最慢
   - 看 Actions 页面的进度条

---

## 🆘 遇到问题？

### 问题：推送失败，提示认证
**解决：** 使用 Personal Access Token
1. Settings → Developer settings → Personal access tokens
2. Generate new token → 勾选 repo 权限
3. 复制 token，推送时作为密码使用

### 问题：Actions 失败
**解决：**
1. 查看 Actions 日志
2. 检查代码是否正确
3. 重新触发工作流

---

## 📦 打包后的文件使用

| 平台 | 文件名 | 运行方式 |
|------|--------|----------|
| Windows | `OpenClaw-部署工具.exe` | 双击运行 |
| Linux | `OpenClaw-部署工具-linux` | `./OpenClaw-部署工具-linux` |
| Mac | `OpenClaw-部署工具-mac` | `./OpenClaw-部署工具-mac` |

---

**开始操作吧！有问题随时问我～** 🚀