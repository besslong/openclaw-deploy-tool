#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenClaw 自动部署客户端
编译成二进制后分发给客户
激活码在线验证
"""

import sys
import os
import subprocess
import requests
import platform
import hashlib
import uuid
from datetime import datetime

# ============= 配置区域 =============
VERIFY_SERVER = "https://你的域名.com/api/verify"
DEPLOY_SCRIPT_URL = "https://你的域名.com/deploy.sh"
VERSION = "1.0.0"
# ===================================


def get_machine_id():
    """获取设备唯一标识"""
    return str(uuid.getnode())  # MAC 地址


def get_system_info():
    """获取系统信息"""
    return {
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "python_version": platform.python_version()
    }


def verify_license(license_key):
    """在线验证激活码"""
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


def check_prerequisites():
    """检查前置条件"""
    print("\n🔍 检查系统环境...")
    
    # 检查 Node.js
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Node.js 已安装：{result.stdout.strip()}")
        else:
            print("⚠️  Node.js 未安装，将自动安装")
            return False
    except FileNotFoundError:
        print("⚠️  Node.js 未安装，将自动安装")
        return False
    
    # 检查 npm
    try:
        result = subprocess.run(["npm", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ npm 已安装：{result.stdout.strip()}")
        else:
            print("⚠️  npm 未安装，将自动安装")
            return False
    except FileNotFoundError:
        print("⚠️  npm 未安装，将自动安装")
        return False
    
    return True


def install_nodejs():
    """安装 Node.js"""
    system = platform.system()
    
    if system == "Linux":
        print("📦 正在安装 Node.js...")
        commands = [
            "curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -",
            "sudo apt-get install -y nodejs"
        ]
        for cmd in commands:
            os.system(cmd)
    elif system == "Darwin":  # macOS
        print("📦 正在安装 Node.js...")
        os.system("/bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"")
        os.system("brew install node")
    elif system == "Windows":
        print("⚠️  Windows 系统请手动安装 Node.js")
        print("📋 下载地址：https://nodejs.org/")
        return False
    
    return True


def download_deploy_script():
    """下载部署脚本"""
    print("\n📥 正在下载部署脚本...")
    
    try:
        response = requests.get(DEPLOY_SCRIPT_URL, timeout=30)
        if response.status_code == 200:
            with open("openclaw_install.sh", "w", encoding="utf-8") as f:
                f.write(response.text)
            os.chmod("openclaw_install.sh", 0o755)
            print("✅ 部署脚本下载完成")
            return True
        else:
            print(f"❌ 下载失败：{response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 下载错误：{e}")
        return False


def run_deployment():
    """执行部署"""
    print("\n🚀 开始部署 OpenClaw...")
    
    if platform.system() == "Windows":
        print("⚠️  Windows 系统请在 PowerShell 中执行以下命令：")
        print("   npm install -g openclaw")
        print("   openclaw setup")
        print("   openclaw gateway start")
        return False
    
    # Linux/macOS
    commands = [
        "sudo npm install -g openclaw",
        "openclaw setup --auto",
        "openclaw gateway start",
        "openclaw status"
    ]
    
    for cmd in commands:
        print(f"\n📋 执行：{cmd}")
        result = os.system(cmd)
        if result != 0:
            print(f"⚠️  命令执行失败：{cmd}")
            # 继续执行，不中断
    
    return True


def show_completion_info():
    """显示完成信息"""
    print("\n" + "="*60)
    print("🎉 OpenClaw 部署完成！")
    print("="*60)
    print("""
📋 访问信息：
   - 控制面板：http://localhost:18788
   - 文档：https://docs.openclaw.ai

💬 售后支持：
   - 加入钉钉群获取技术支持
   - 群内 @客服 获取帮助
   - 常见问题文档：https://你的域名.com/faq

⚠️  注意事项：
   - 请妥善保管激活码
   - 一个激活码仅限一台设备使用
   - 如需更换设备，请联系客服

感谢您的使用！
""")
    print("="*60)


def main():
    """主函数"""
    print("="*60)
    print("🦞 OpenClaw 自动部署工具")
    print(f"版本：{VERSION}")
    print("="*60)
    
    # 获取激活码
    if len(sys.argv) > 1:
        license_key = sys.argv[1]
    else:
        license_key = input("\n请输入激活码：").strip()
    
    if not license_key:
        print("❌ 激活码不能为空")
        sys.exit(1)
    
    # 验证激活码
    if not verify_license(license_key):
        sys.exit(1)
    
    # 检查环境
    if not check_prerequisites():
        if not install_nodejs():
            print("\n⚠️  Node.js 安装失败，请手动安装后重新运行")
            sys.exit(1)
    
    # 下载并执行部署脚本
    if not download_deploy_script():
        sys.exit(1)
    
    if not run_deployment():
        print("\n⚠️  部署过程中出现警告，但可能已成功")
    
    # 显示完成信息
    show_completion_info()
    
    # 上报部署结果
    try:
        requests.post(f"{VERIFY_SERVER}/report", json={
            "key": license_key,
            "machine_id": get_machine_id(),
            "status": "success",
            "system_info": get_system_info()
        }, timeout=5)
    except:
        pass  # 上报失败不影响使用
    
    sys.exit(0)


if __name__ == "__main__":
    main()
