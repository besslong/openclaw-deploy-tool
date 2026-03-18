#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
钉钉群自动回复机器人
常见问题自动回答，复杂问题转人工
"""

from flask import Flask, request, jsonify
import requests
import json
from datetime import datetime

app = Flask(__name__)

# ============= 配置 =============
DINGTALK_WEBHOOK = "https://oapi.dingtalk.com/robot/send?access_token=YOUR_TOKEN"
SECRET = ""  # 钉钉机器人加签密钥（如有）
# =================================


# 常见问题库
FAQ_DATABASE = {
    # 关键词：回复
    "安装失败": """
📋 安装失败排查步骤：

1️⃣ 检查 Node.js 是否安装
   执行：node -v
   
2️⃣ 如果未安装，请执行：
   Linux: curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
   macOS: brew install node
   Windows: 前往 https://nodejs.org/ 下载安装

3️⃣ 重新运行部署脚本

如仍失败，请发送错误截图 @客服
""",

    "激活码无效": """
🔐 激活码问题排查：

1️⃣ 检查激活码格式
   正确格式：OPENCLAW-XXXX-XXXX-XXXX
   
2️⃣ 检查是否复制完整
   包含所有横杠和字母
   
3️⃣ 检查是否已使用
   一个激活码仅限一台设备
   
4️⃣ 检查网络
   需要联网验证激活码

如仍无法解决，请提供：
- 完整激活码
- 错误提示截图
@客服 处理
""",

    "端口占用": """
⚠️ 端口被占用解决：

1️⃣ 查看占用端口的进程
   Linux: lsof -i :18788
   macOS: lsof -i :18788
   
2️⃣ 杀死占用进程
   sudo kill -9 <PID>
   
3️⃣ 或修改 OpenClaw 端口
   openclaw config set gateway.port=18789

4️⃣ 重启服务
   openclaw gateway restart
""",

    "无法访问": """
🌐 无法访问控制面板：

1️⃣ 检查服务是否运行
   openclaw status
   
2️⃣ 检查防火墙
   sudo ufw allow 18788
   
3️⃣ 检查是否监听正确地址
   openclaw gateway info
   
4️⃣ 尝试本地访问
   http://localhost:18788

如仍无法访问，请提供：
- openclaw status 输出
- 系统类型
@客服 处理
""",

    "部署脚本": """
📥 部署脚本下载：

脚本已放在网盘，购买后自动发送

如未收到，请检查：
1️⃣ 闲鱼消息
2️⃣ 垃圾消息
3️⃣ 联系卖家重发

脚本说明：
- Windows: deploy_client.exe
- Mac/Linux: deploy_client
""",

    "视频教程": """
📺 视频教程：

B 站教程：https://space.bilibili.com/xxx
- OpenClaw 部署教程
- 功能使用讲解
- 常见问题解答

文档：https://docs.openclaw.ai
""",

    "退款": """
💰 退款政策：

✅ 支持退款情况：
- 部署失败且无法解决
- 产品与描述不符

❌ 不支持退款：
- 激活码已使用
- 超过 7 天
- 人为操作失误

申请退款请 @客服 并提供：
- 订单号
- 问题描述
- 相关截图
""",

    "帮助": """
🤖 OpenClaw 部署助手

常见问题：
- 安装失败 → 回复"安装"
- 激活码问题 → 回复"激活码"
- 端口占用 → 回复"端口"
- 无法访问 → 回复"访问"
- 部署脚本 → 回复"脚本"
- 视频教程 → 回复"视频"
- 退款政策 → 回复"退款"

人工客服：@客服
工作时间：9:00-22:00
""",

    "人工": """
👨‍💼 正在转接人工客服...

请稍候，客服会尽快回复您
工作时间：9:00-22:00

如问题紧急，请直接电话联系
""",

    "谢谢": """
😊 不客气！

如有其他问题，随时问我～

祝您使用愉快！🦞
"""
}


def send_dingtalk_message(content, at_user_ids=None):
    """发送钉钉消息"""
    headers = {'Content-Type': 'application/json'}
    
    data = {
        "msgtype": "text",
        "text": {
            "content": content
        },
        "at": {
            "atUserIds": at_user_ids or [],
            "isAtAll": False
        }
    }
    
    try:
        response = requests.post(DINGTALK_WEBHOOK, headers=headers, json=data)
        return response.json()
    except Exception as e:
        print(f"发送失败：{e}")
        return None


def match_keyword(message):
    """匹配关键词"""
    message = message.lower()
    
    for keyword, response in FAQ_DATABASE.items():
        if keyword.lower() in message:
            return response
    
    return None


@app.route('/webhook/dingtalk', methods=['POST'])
def dingtalk_webhook():
    """接收钉钉群消息"""
    data = request.json
    
    # 提取消息内容
    msg_content = data.get('text', {}).get('content', '')
    sender_id = data.get('senderId', '')
    conversation_id = data.get('conversationId', '')
    
    print(f"[{datetime.now()}] 收到消息 from {sender_id}: {msg_content}")
    
    # 忽略机器人消息
    if data.get('senderType') == 'robot':
        return jsonify({"status": "ignored"})
    
    # 匹配关键词自动回复
    response = match_keyword(msg_content)
    
    if response:
        send_dingtalk_message(response.strip(), at_user_ids=[sender_id])
        print(f"自动回复：{response[:50]}...")
    else:
        # 无匹配，提示转人工
        default_response = """
收到您的问题，请稍后～

常见问题可参考：
- 安装问题 → 回复"安装"
- 激活码 → 回复"激活码"
- 完整帮助 → 回复"帮助"

正在转接人工客服 @客服
"""
        send_dingtalk_message(default_response.strip(), at_user_ids=["manager"])
        print("转人工客服")
    
    return jsonify({"status": "ok"})


@app.route('/test', methods=['GET'])
def test():
    """测试端点"""
    return jsonify({
        "status": "ok",
        "time": datetime.now().isoformat(),
        "faq_count": len(FAQ_DATABASE)
    })


if __name__ == "__main__":
    print("="*60)
    print("🤖 钉钉群自动回复机器人")
    print("="*60)
    print(f"\n已加载 {len(FAQ_DATABASE)} 条常见问题")
    print("\n关键词列表：")
    for keyword in FAQ_DATABASE.keys():
        print(f"  - {keyword}")
    print(f"\n📋 Webhook: POST /webhook/dingtalk")
    print(f"🧪 测试：GET /test")
    print(f"\n⚠️  按 Ctrl+C 停止服务")
    
    app.run(host='0.0.0.0', port=5001, debug=False)
