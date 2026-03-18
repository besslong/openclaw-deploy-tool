# 🦞 OpenClaw 部署服务系统

全自动部署 + 激活码验证 + 售后支持

---

## 📋 系统组成

```
openclaw-deploy-service/
├── deploy_client.py      # 客户端部署脚本（编译成二进制分发）
├── license_server.py     # 激活码验证服务器
├── generate_license.py   # 激活码生成工具
├── faq_bot.py            # 钉钉群自动回复机器人
├── README.md             # 本文件
└── requirements.txt      # Python 依赖
```

---

## 🚀 快速开始

### 1. 部署验证服务器

```bash
# 安装依赖
pip install flask requests

# 启动验证服务器
python license_server.py
```

服务器会监听 `http://0.0.0.0:5000`

**API 端点：**
- `POST /api/verify` - 验证激活码
- `POST /api/report` - 上报部署结果
- `POST /api/generate` - 生成激活码
- `GET /api/list` - 查看激活码列表
- `POST /api/revoke/:key` - 吊销激活码

---

### 2. 生成激活码

```bash
# 交互模式
python generate_license.py

# 批量生成 10 个
python generate_license.py batch 10 365

# 生成单个
python generate_license.py single ORDER123 "买家信息" 365
```

生成的激活码格式：`OPENCLAW-XXXX-XXXX-XXXX`

---

### 3. 编译客户端脚本

```bash
# 安装 pyinstaller
pip install pyinstaller

# 修改 deploy_client.py 中的配置
# VERIFY_SERVER = "https://你的域名.com/api/verify"
# DEPLOY_SCRIPT_URL = "https://你的域名.com/deploy.sh"

# 编译成二进制
pyinstaller --onefile --name deploy_client deploy_client.py

# Windows 输出：dist/deploy_client.exe
# Mac/Linux 输出：dist/deploy_client
```

---

### 4. 上传到网盘

将编译好的文件上传到：
- 百度网盘
- 阿里云盘
- 腾讯微云
- 其他任意网盘

**获取分享链接**

---

### 5. 闲鱼上架

**商品标题：**
```
OpenClaw 自动部署服务 | 一键安装 | 包成功 | 送教程
```

**商品描述：**
```
🦞 OpenClaw 自动部署服务

✅ 支持系统：
- Linux (Ubuntu/Debian/CentOS)
- macOS
- Windows

✅ 部署方式：
1️⃣ 云服务器部署（推荐）
   - 提供 SSH 信息
   - 自动部署
   - 5-10 分钟完成

2️⃣ 本地电脑部署
   - 下载部署脚本
   - 一键执行
   - 包成功

✅ 服务包含：
- OpenClaw 安装
- 配置优化
- 使用教程
- 30 天技术支持

💰 价格：
- 云服务器部署：¥299
- 本地电脑部署：¥199
- 包年服务：¥999/年

📦 发货方式：
自动发送网盘链接 + 激活码

⚠️ 注意：
- 激活码仅限一台设备使用
- 请确认系统环境再购买
- 虚拟商品不支持退款

📚 文档：https://docs.openclaw.ai
```

**自动回复设置：**
```
感谢购买！

📦 部署脚本已放在网盘：
链接：https://pan.baidu.com/s/xxx
密码：xxxx

🔑 您的激活码：
OPENCLAW-XXXX-XXXX-XXXX

📋 使用说明：
1. 下载部署脚本
2. 运行脚本并输入激活码
3. 等待自动部署完成

💬 技术支持：
加入钉钉群：[群链接]
群内 @客服 获取帮助

📚 教程文档：https://你的域名.com/docs
```

---

## 🔧 配置说明

### deploy_client.py 配置

```python
# 修改这些配置
VERIFY_SERVER = "https://你的域名.com/api/verify"
DEPLOY_SCRIPT_URL = "https://你的域名.com/deploy.sh"
```

### license_server.py 配置

```python
# 数据库路径
DB_PATH = "licenses.db"

# 设备限制
MAX_DEVICES_PER_KEY = 1  # 一个激活码可用几台设备
```

### faq_bot.py 配置

```python
# 钉钉机器人 Webhook
DINGTALK_WEBHOOK = "https://oapi.dingtalk.com/robot/send?access_token=YOUR_TOKEN"
```

---

## 📊 激活码管理

### 查看所有激活码

```bash
curl http://localhost:5000/api/list
```

### 生成新激活码

```bash
curl -X POST http://localhost:5000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"order_id":"ORDER123","buyer_info":"买家名称","expires_days":365}'
```

### 吊销激活码

```bash
curl -X POST http://localhost:5000/api/revoke/OPENCLAW-XXXX-XXXX-XXXX
```

---

## 🤖 钉钉群设置

### 1. 创建钉钉群

- 打开钉钉
- 创建群聊
- 命名为"OpenClaw 技术支持群"

### 2. 添加机器人

- 群设置 → 智能群助手
- 添加自定义机器人
- 获取 Webhook 地址

### 3. 配置机器人

修改 `faq_bot.py` 中的 `DINGTALK_WEBHOOK`

### 4. 启动机器人

```bash
python faq_bot.py
```

### 5. 设置群公告

```
🤖 OpenClaw 技术支持群

常见问题自动回复：
- 安装失败 → 回复"安装"
- 激活码 → 回复"激活码"
- 端口占用 → 回复"端口"
- 无法访问 → 回复"访问"
- 完整帮助 → 回复"帮助"

人工客服：@客服
工作时间：9:00-22:00
```

---

## 📈 运营建议

### 定价策略

| 服务 | 价格 | 成本 | 利润 |
|------|------|------|------|
| 云服务器部署 | ¥299 | ¥0 | ¥299 |
| 本地电脑部署 | ¥199 | ¥0 | ¥199 |
| 包年服务 | ¥999/年 | ¥0 | ¥999 |

### 获客渠道

- 闲鱼（主要）
- 小红书（教程引流）
- B 站（视频教程）
- 知乎（技术文章）
- V2EX（开发者社区）

### 售后流程

```
客户问题 → 钉钉群提问
    ↓
自动回复（常见问题）
    ↓
人工处理（复杂问题）
    ↓
问题解决 → 邀请好评
```

---

## ⚠️ 注意事项

### 安全

1. 验证服务器建议用 HTTPS
2. 数据库定期备份
3. 激活码生成密钥保管好
4. 不要泄露管理员权限

### 法律

1. OpenClaw 是开源项目，可以商用
2. 你卖的是部署服务，不是软件本身
3. 明确标注服务内容和范围
4. 虚拟商品提前说明不退不换

### 运营

1. 及时回复客户问题
2. 收集常见问题更新 FAQ
3. 定期更新部署脚本
4. 维护好评价和信誉

---

## 🆘 常见问题

### Q: 激活码被破解怎么办？

A: 
- 核心逻辑在服务器，破解版无法使用
- 定期更新脚本，旧版本失效
- 在线验证可以吊销激活码

### Q: 客户不会用怎么办？

A:
- 准备详细教程文档
- 录制视频教程
- 钉钉群一对一指导

### Q: 服务器挂了怎么办？

A:
- 用云服务器（阿里云/腾讯云）
- 设置监控告警
- 定期备份数据库

### Q: 一天能处理多少订单？

A:
- 自动部署：无限（全自动）
- 售后支持：50-100 单/天（自动回复 + 人工）

---

## 📞 技术支持

钉钉群：[你的群链接]
文档：https://你的域名.com/docs

---

**祝生意兴隆！🦞**
