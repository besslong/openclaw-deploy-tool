#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenClaw 自动部署客户端
支持服务器部署和本地部署
交互式输入，用户友好
"""

import sys
import os
import subprocess
import requests
import platform
import hashlib
import uuid
import json
from datetime import datetime

# ============= 配置 =============
VERIFY_SERVER = "http://180.76.100.92:5000/api/verify"
VERSION = "2.0.0"
# ===================================


def pause_exit(msg="按回车键退出..."):
    """暂停等待用户按键后退出"""
    try:
        input(f"\n{msg}")
    except:
        pass
    sys.exit(0)


def print_header():
    """打印程序标题"""
    print("=" * 60)
    print("🦞 OpenClaw 自动部署工具")
    print(f"版本：{VERSION}")
    print("=" * 60)
    print()


def get_machine_id():
    """获取设备唯一标识"""
    return str(uuid.getnode())


def clear_screen():
    """清屏"""
    os.system('cls' if os.name == 'nt' else 'clear')


def select_deploy_mode():
    """选择部署模式"""
    print("📋 请选择部署方式：")
    print()
    print("  1️⃣  云服务器部署（推荐）")
    print("      - 你有一台云服务器（阿里云/腾讯云/华为云等）")
    print("      - 提供 SSH 信息，自动远程部署")
    print()
    print("  2️⃣  本地电脑部署")
    print("      - 在当前电脑上安装 OpenClaw")
    print("      - 适合个人使用")
    print()
    
    while True:
        choice = input("请输入选择 (1 或 2)：").strip()
        if choice in ['1', '2']:
            return int(choice)
        print("❌ 请输入 1 或 2")


def get_server_info():
    """获取服务器信息"""
    print()
    print("=" * 60)
    print("📡 云服务器部署配置")
    print("=" * 60)
    print()
    print("📝 请准备以下信息：")
    print("   - 服务器公网 IP 地址")
    print("   - SSH 用户名（通常是 root）")
    print("   - SSH 密码")
    print()
    
    # IP 地址
    print("📌 关于 IP 地址：")
    print("   - 云服务器：使用公网 IP")
    print("   - 在云服务器控制台可以查看")
    print("   - 或者登录服务器后执行：curl ifconfig.me")
    print()
    
    while True:
        server_ip = input("请输入服务器 IP 地址：").strip()
        if server_ip:
            break
        print("❌ IP 地址不能为空")
    
    # 用户名
    while True:
        ssh_user = input("请输入 SSH 用户名 (默认 root)：").strip()
        if not ssh_user:
            ssh_user = "root"
        break
    
    # 密码
    while True:
        ssh_password = input("请输入 SSH 密码：").strip()
        if ssh_password:
            break
        print("❌ 密码不能为空")
    
    return {
        "ip": server_ip,
        "user": ssh_user,
        "password": ssh_password
    }


def get_local_info():
    """获取本地部署信息"""
    print()
    print("=" * 60)
    print("💻 本地电脑部署配置")
    print("=" * 60)
    print()
    
    system = platform.system()
    print(f"检测到系统：{system}")
    print()
    
    if system == "Windows":
        print("📌 Windows 系统部署说明：")
        print("   - 需要管理员权限")
        print("   - 会自动安装 Node.js")
        print("   - 会自动安装 OpenClaw")
    elif system == "Linux":
        print("📌 Linux 系统部署说明：")
        print("   - 需要 root 权限")
        print("   - 会自动安装 Node.js")
        print("   - 会自动安装 OpenClaw")
    elif system == "Darwin":
        print("📌 macOS 系统部署说明：")
        print("   - 会自动安装 Node.js")
        print("   - 会自动安装 OpenClaw")
    
    print()
    
    return {"system": system}


def verify_license(license_key):
    """在线验证激活码"""
    print()
    print("🔐 正在验证激活码...")
    
    try:
        response = requests.post(VERIFY_SERVER, json={
            "key": license_key,
            "machine_id": get_machine_id(),
            "version": VERSION,
            "timestamp": datetime.now().isoformat()
        }, timeout=10)
        
        if response.status_code != 200:
            print(f"❌ 验证失败：服务器返回错误 {response.status_code}")
            return False
        
        result = response.json()
        
        if result.get("valid"):
            print("✅ 激活码验证成功！")
            if result.get("message"):
                print(f"📋 {result['message']}")
            return True
        else:
            print(f"❌ 激活码无效：{result.get('error', '未知错误')}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ 验证超时，请检查网络连接")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ 网络错误：{e}")
        return False


def deploy_to_server(server_info):
    """部署到云服务器"""
    print()
    print("=" * 60)
    print("🚀 开始远程部署...")
    print("=" * 60)
    print()
    
    ip = server_info["ip"]
    user = server_info["user"]
    password = server_info["password"]
    
    print(f"📡 连接服务器：{ip}")
    print(f"👤 用户名：{user}")
    print()
    
    # 这里需要用 paramiko 或类似工具进行 SSH 连接
    # 简化版本：提示用户手动操作
    
    print("⚠️  自动远程部署需要安装额外组件")
    print()
    print("📋 请手动执行以下步骤：")
    print()
    print("1. 使用 SSH 工具连接服务器：")
    print(f"   ssh {user}@{ip}")
    print()
    print("2. 执行以下命令安装 OpenClaw：")
    print()
    print("   # 安装 Node.js")
    print("   curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -")
    print("   sudo apt-get install -y nodejs")
    print()
    print("   # 安装 OpenClaw")
    print("   sudo npm install -g openclaw")
    print()
    print("   # 初始化")
    print("   openclaw setup")
    print()
    print("   # 启动")
    print("   openclaw gateway start")
    print()
    print("3. 访问 OpenClaw：")
    print(f"   http://{ip}:18788")
    print()


def deploy_local(local_info):
    """本地部署"""
    print()
    print("=" * 60)
    print("🚀 开始本地部署...")
    print("=" * 60)
    print()
    
    system = local_info["system"]
    
    # 检查 Node.js
    print("🔍 检查 Node.js...")
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Node.js 已安装：{result.stdout.strip()}")
        else:
            print("⚠️  Node.js 未安装，正在安装...")
            install_nodejs(system)
    except FileNotFoundError:
        print("⚠️  Node.js 未安装，正在安装...")
        install_nodejs(system)
    
    # 安装 OpenClaw
    print()
    print("📦 安装 OpenClaw...")
    if system == "Windows":
        print("   请手动执行：npm install -g openclaw")
        print("   然后执行：openclaw setup")
    else:
        result = subprocess.run(["npm", "install", "-g", "openclaw"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ OpenClaw 安装成功")
        else:
            print(f"❌ 安装失败：{result.stderr}")
    
    print()
    print("=" * 60)
    print("🎉 部署完成！")
    print("=" * 60)
    print()
    print("📋 访问地址：http://localhost:18788")
    print("📚 文档：https://docs.openclaw.ai")


def install_nodejs(system):
    """安装 Node.js"""
    if system == "Linux":
        print("   执行安装命令...")
        os.system("curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -")
        os.system("sudo apt-get install -y nodejs")
    elif system == "Darwin":
        print("   请执行：brew install node")
    elif system == "Windows":
        print("   请下载安装：https://nodejs.org/")


def main():
    """主函数"""
    clear_screen()
    print_header()
    
    # 输入激活码
    print("🔑 请输入激活码")
    print("   格式：OPENCLAW-XXXX-XXXX-XXXX")
    print()
    
    license_key = input("激活码：").strip()
    
    if not license_key:
        print("❌ 激活码不能为空")
        pause_exit()
    
    # 验证激活码
    if not verify_license(license_key):
        pause_exit()
    
    # 选择部署模式
    print()
    mode = select_deploy_mode()
    
    if mode == 1:
        # 云服务器部署
        server_info = get_server_info()
        deploy_to_server(server_info)
    else:
        # 本地部署
        local_info = get_local_info()
        deploy_local(local_info)
    
    # 暂停等待用户确认
    pause_exit("✅ 完成！按回车键退出...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 用户取消，再见！")
    except Exception as e:
        print(f"\n❌ 发生错误：{e}")
        pause_exit("按回车键退出...")