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
import platform
import hashlib
import uuid
import json
import traceback
import logging
from datetime import datetime

# ============= 配置 =============
VERSION = "2.0.0"
LOG_FILE = "deploy_client_error.log"
# ===================================


def setup_logging():
    """配置错误日志记录到文件"""
    logging.basicConfig(
        level=logging.ERROR,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE, encoding='utf-8'),
            logging.StreamHandler(sys.stderr)
        ]
    )
    return logging.getLogger(__name__)


def check_dependencies():
    """启动时检查依赖库是否已安装"""
    missing_deps = []
    required_modules = ['requests']
    
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_deps.append(module)
    
    if missing_deps:
        error_msg = f"缺少必要的依赖库：{', '.join(missing_deps)}\n"
        error_msg += f"请运行以下命令安装：pip install {' '.join(missing_deps)}\n"
        error_msg += f"\n如果是打包后的 exe，请确保打包时包含了所有依赖。"
        
        # 记录到日志
        logger = logging.getLogger(__name__)
        logger.error(error_msg.replace('\n', ' | '))
        
        # 显示错误信息并等待用户
        print("=" * 60)
        print("❌ 启动失败 - 缺少依赖库")
        print("=" * 60)
        print()
        print(error_msg)
        print()
        
        # Windows 下双击运行时确保能看到错误
        if os.name == 'nt':
            print("按回车键退出...")
            input()
        else:
            print("按回车键退出...")
            try:
                input()
            except:
                pass
        
        sys.exit(1)
    
    # 依赖检查通过后才能导入 requests
    import requests
    return requests


def pause_exit(msg="按回车键退出..."):
    """暂停等待用户按键后退出"""
    try:
        # Windows 下确保控制台窗口不会立即关闭
        if os.name == 'nt':
            print()
            print(msg)
            input()
        else:
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


def verify_license(license_key, requests):
    """在线验证激活码"""
    logger = logging.getLogger(__name__)
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
            error_msg = f"验证失败：服务器返回错误 {response.status_code}"
            print(f"❌ {error_msg}")
            logger.error(error_msg)
            return False
        
        result = response.json()
        
        if result.get("valid"):
            print("✅ 激活码验证成功！")
            if result.get("message"):
                print(f"📋 {result['message']}")
            return True
        else:
            error_msg = f"激活码无效：{result.get('error', '未知错误')}"
            print(f"❌ {error_msg}")
            logger.error(error_msg)
            return False
            
    except requests.exceptions.Timeout:
        error_msg = "验证超时，请检查网络连接"
        print(f"❌ {error_msg}")
        logger.error(error_msg, exc_info=True)
        return False
    except requests.exceptions.RequestException as e:
        error_msg = f"网络错误：{e}"
        print(f"❌ {error_msg}")
        logger.error(error_msg, exc_info=True)
        return False
    except Exception as e:
        error_msg = f"验证过程发生错误：{e}"
        print(f"❌ {error_msg}")
        logger.error(error_msg, exc_info=True)
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
            version_str = result.stdout.strip()
            print(f"✅ Node.js 已安装：{version_str}")
            
            # 检查版本是否 >= 22.12
            try:
                major = int(version_str.replace('v', '').split('.')[0])
                minor = int(version_str.replace('v', '').split('.')[1])
                if major < 22 or (major == 22 and minor < 12):
                    print(f"⚠️  Node.js 版本过低，OpenClaw 需要 v22.12+")
                    print("   正在升级 Node.js...")
                    install_nodejs(system)
            except:
                pass
        else:
            print("⚠️  Node.js 未安装，正在安装...")
            install_nodejs(system)
    except FileNotFoundError:
        print("⚠️  Node.js 未安装，正在安装...")
        install_nodejs(system)
    except Exception as e:
        print(f"⚠️  检查 Node.js 失败：{e}")
        logger = logging.getLogger(__name__)
        logger.error(f"Node.js 检查失败：{e}", exc_info=True)
    
    # 安装 OpenClaw
    print()
    print("📦 安装 OpenClaw...")
    
    if system == "Windows":
        # Windows 下自动安装
        print("   ⏳ 正在安装 OpenClaw，请稍候...")
        
        # 尝试使用完整路径
        npm_paths = [
            r"C:\Program Files\nodejs\npm.cmd",
            r"C:\Program Files (x86)\nodejs\npm.cmd",
            os.path.expandvars(r"%APPDATA%\npm\npm.cmd"),
            "npm"  # 依赖 PATH
        ]
        
        npm_cmd = None
        for path in npm_paths:
            try:
                test_result = subprocess.run([path, "--version"], capture_output=True, text=True, shell=True, timeout=5)
                if test_result.returncode == 0:
                    npm_cmd = path
                    break
            except:
                continue
        
        if npm_cmd:
            # Windows 上先检查 Git
            print("   🔍 检查 Git...")
            if not check_git():
                print("   ⚠️  未检测到 Git，正在安装...")
                install_git_windows()
                print()
                print("   📌 Git 安装完成，请重新运行此工具")
                print("   或者关闭窗口后重新打开命令提示符，再运行:")
                print("   npm install -g openclaw@latest --registry https://registry.npmjs.org")
                return
            else:
                print("   ✅ Git 已安装")
            
            # 先卸载旧版本（可能存在）
            print("   🔧 清理旧版本...")
            subprocess.run([npm_cmd, "uninstall", "-g", "openclaw"], capture_output=True, text=True, shell=True)
            
            # 强制使用官方源安装最新版本
            print("   📥 从官方源安装最新版本...")
            result = subprocess.run(
                [npm_cmd, "install", "-g", "openclaw@latest", "--registry", "https://registry.npmjs.org"],
                capture_output=True, text=True, shell=True
            )
            
            if result.returncode == 0:
                # 验证安装版本
                print("   🔍 验证安装...")
                verify_result = subprocess.run([npm_cmd, "list", "-g", "openclaw"], capture_output=True, text=True, shell=True)
                
                # 检查版本是否正确（应该是 2026.x.x 而不是 0.0.1）
                if "openclaw@" in verify_result.stdout:
                    version_line = [l for l in verify_result.stdout.split('\n') if 'openclaw@' in l]
                    if version_line:
                        import re
                        match = re.search(r'openclaw@([\d.]+)', version_line[0])
                        if match:
                            version = match.group(1)
                            if version.startswith('2026'):
                                print(f"   ✅ OpenClaw {version} 安装成功！")
                                print()
                                
                                # 配置 API Key
                                config_api_key(system)
                                
                                print()
                                print("   " + "=" * 50)
                                print("   🎉 安装完成！")
                                print("   " + "=" * 50)
                                print()
                                print("   启动步骤：")
                                print("   1. 关闭当前窗口")
                                print("   2. 打开新的命令提示符（管理员）")
                                print("   3. 运行: openclaw gateway start")
                                print("   4. 访问: http://localhost:18788")
                                print()
                                print("   常用命令：")
                                print("   • 查看状态: openclaw status")
                                print("   • 配置模型: openclaw configure")
                                print("   • 查看帮助: openclaw --help")
                                print()
                            else:
                                # 版本不对，尝试其他方法
                                print(f"   ⚠️  安装了错误版本：{version}")
                                print("   正在尝试修复...")
                                
                                # 尝试清理缓存后重装
                                subprocess.run([npm_cmd, "cache", "clean", "--force"], capture_output=True, text=True, shell=True)
                                subprocess.run([npm_cmd, "uninstall", "-g", "openclaw"], capture_output=True, text=True, shell=True)
                                
                                result2 = subprocess.run(
                                    [npm_cmd, "install", "-g", "openclaw@2026.3.13", "--registry", "https://registry.npmjs.org"],
                                    capture_output=True, text=True, shell=True
                                )
                                
                                if result2.returncode == 0:
                                    print("   ✅ 修复成功！请按上面的步骤操作")
                                else:
                                    print("   ❌ 自动修复失败")
                                    print("   请手动执行以下命令：")
                                    print("   npm uninstall -g openclaw")
                                    print("   npm install -g openclaw@2026.3.13 --registry https://registry.npmjs.org")
                else:
                    print("   ⚠️  无法验证安装版本")
                    print("   请手动检查: npm list -g openclaw")
            else:
                print(f"   ❌ 安装失败：{result.stderr}")
                print()
                print("   请手动执行以下命令：")
                print("   npm install -g openclaw@latest --registry https://registry.npmjs.org")
        else:
            print("   ⚠️  未找到 npm，请确保 Node.js 已安装")
            print("   安装 Node.js 后，重新运行此工具")
    else:
        # Linux/macOS
        # 先卸载旧版本
        subprocess.run(["npm", "uninstall", "-g", "openclaw"], capture_output=True, text=True)
        
        # 安装最新版本
        result = subprocess.run(
            ["npm", "install", "-g", "openclaw@latest", "--registry", "https://registry.npmjs.org"],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            # 验证版本
            verify_result = subprocess.run(["npm", "list", "-g", "openclaw"], capture_output=True, text=True)
            if "2026" in verify_result.stdout:
                print("✅ OpenClaw 安装成功")
                
                # 配置 API Key
                config_api_key(system)
                
                print()
                print("=" * 60)
                print("🎉 安装完成！")
                print("=" * 60)
                print()
                print("启动步骤：")
                print("  1. 运行: openclaw gateway start")
                print("  2. 访问: http://localhost:18788")
                print()
            else:
                print("⚠️  版本验证失败，请手动检查")
        else:
            print(f"❌ 安装失败：{result.stderr}")
    
    print()
    print("=" * 60)
    print("🎉 部署完成！")
    print("=" * 60)
    print()
    print("📋 访问地址：http://localhost:18788")
    print("📚 文档：https://docs.openclaw.ai")


def config_api_key(system):
    """配置 AI 模型 API Key"""
    print()
    print("=" * 60)
    print("🔑 AI 模型配置")
    print("=" * 60)
    print()
    
    # 先检查 openclaw 是否可用（刚安装后 PATH 可能未更新）
    openclaw_cmd = None
    if system == "Windows":
        # Windows 上尝试多个路径
        possible_paths = [
            r"C:\Program Files\nodejs\openclaw.cmd",
            r"C:\Program Files (x86)\nodejs\openclaw.cmd",
            os.path.expandvars(r"%APPDATA%\npm\openclaw.cmd"),
            "openclaw"
        ]
        for path in possible_paths:
            try:
                result = subprocess.run([path, "--version"], capture_output=True, text=True, shell=True, timeout=5)
                if result.returncode == 0:
                    openclaw_cmd = path
                    break
            except:
                continue
    else:
        try:
            result = subprocess.run(["openclaw", "--version"], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                openclaw_cmd = "openclaw"
        except:
            pass
    
    if not openclaw_cmd:
        print("⚠️  检测到 OpenClaw 命令暂不可用")
        print("   这是因为刚安装完成，系统环境变量还未更新")
        print()
        print("📌 请按以下步骤配置 API Key：")
        print("   1. 关闭当前窗口")
        print("   2. 重新打开命令提示符（管理员）")
        print("   3. 运行: openclaw configure")
        print()
        print("支持的 AI 服务：")
        print("  • 通义千问 (Qwen) - 推荐，国内稳定")
        print("  • OpenAI (GPT-4) - 需要科学上网")
        return False
    
    print("OpenClaw 需要配置 AI 模型才能工作。")
    print()
    print("请选择要使用的 AI 服务：")
    print()
    print("  1️⃣  通义千问 (Qwen) - 推荐，国内访问稳定")
    print("      价格便宜，中文效果好")
    print()
    print("  2️⃣  OpenAI (GPT-4)")
    print("      需要科学上网")
    print()
    print("  3️⃣  跳过，稍后手动配置")
    print()
    
    while True:
        try:
            choice = input("请选择 (1/2/3)：").strip()
            if choice in ['1', '2', '3']:
                break
            print("❌ 请输入 1、2 或 3")
        except EOFError:
            choice = '3'
            break
    
    if choice == '3':
        print()
        print("📌 稍后可以运行以下命令配置：")
        print("   openclaw configure")
        return False
    
    print()
    
    if choice == '1':
        # 通义千问
        print("=" * 60)
        print("📢 通义千问 (Qwen) 配置")
        print("=" * 60)
        print()
        print("获取 API Key 步骤：")
        print("  1. 访问：https://dashscope.console.aliyun.com/")
        print("  2. 登录阿里云账号")
        print("  3. 开通 DashScope 服务")
        print("  4. 创建 API Key")
        print()
        
        try:
            api_key = input("请输入通义千问 API Key：").strip()
        except EOFError:
            api_key = ""
        
        if api_key:
            print()
            print("⏳ 正在配置...")
            
            # 配置 openclaw
            try:
                # 设置模型
                subprocess.run([openclaw_cmd, "config", "set", "model", "qwen"], capture_output=True, shell=True)
                # 设置 API Key
                result = subprocess.run(
                    [openclaw_cmd, "config", "set", "providers.qwen.apiKey", api_key],
                    capture_output=True, text=True, shell=True
                )
                
                if result.returncode == 0:
                    print("✅ 通义千问 API Key 配置成功！")
                    return True
                else:
                    print(f"⚠️  配置失败：{result.stderr}")
                    print("   请稍后运行: openclaw configure")
            except Exception as e:
                print(f"⚠️  配置出错：{e}")
                print("   请稍后运行: openclaw configure")
        else:
            print("⚠️  未输入 API Key")
            print("   请稍后运行: openclaw configure")
    
    elif choice == '2':
        # OpenAI
        print("=" * 60)
        print("📢 OpenAI 配置")
        print("=" * 60)
        print()
        print("获取 API Key 步骤：")
        print("  1. 访问：https://platform.openai.com/api-keys")
        print("  2. 登录 OpenAI 账号")
        print("  3. 创建 API Key")
        print()
        print("⚠️  注意：使用 OpenAI 需要科学上网")
        print()
        
        try:
            api_key = input("请输入 OpenAI API Key：").strip()
        except EOFError:
            api_key = ""
        
        if api_key:
            print()
            print("⏳ 正在配置...")
            
            try:
                subprocess.run([openclaw_cmd, "config", "set", "model", "openai"], capture_output=True, shell=True)
                result = subprocess.run(
                    [openclaw_cmd, "config", "set", "providers.openai.apiKey", api_key],
                    capture_output=True, text=True, shell=True
                )
                
                if result.returncode == 0:
                    print("✅ OpenAI API Key 配置成功！")
                    return True
                else:
                    print(f"⚠️  配置失败：{result.stderr}")
            except Exception as e:
                print(f"⚠️  配置出错：{e}")
        else:
            print("⚠️  未输入 API Key")
    
    return False
    
    print()
    
    if choice == '1':
        # 通义千问
        print("=" * 60)
        print("📢 通义千问 (Qwen) 配置")
        print("=" * 60)
        print()
        print("获取 API Key 步骤：")
        print("  1. 访问：https://dashscope.console.aliyun.com/")
        print("  2. 登录阿里云账号")
        print("  3. 开通 DashScope 服务")
        print("  4. 创建 API Key")
        print()
        
        api_key = input("请输入通义千问 API Key：").strip()
        
        if api_key:
            print()
            print("⏳ 正在配置...")
            
            # 配置 openclaw
            try:
                # 设置模型
                subprocess.run(["openclaw", "config", "set", "model", "qwen"], capture_output=True)
                # 设置 API Key
                result = subprocess.run(
                    ["openclaw", "config", "set", "providers.qwen.apiKey", api_key],
                    capture_output=True, text=True
                )
                
                if result.returncode == 0:
                    print("✅ 通义千问 API Key 配置成功！")
                    return True
                else:
                    print(f"⚠️  配置失败：{result.stderr}")
                    print("   请稍后运行: openclaw configure")
            except Exception as e:
                print(f"⚠️  配置出错：{e}")
                print("   请稍后运行: openclaw configure")
        else:
            print("⚠️  未输入 API Key")
            print("   请稍后运行: openclaw configure")
    
    elif choice == '2':
        # OpenAI
        print("=" * 60)
        print("📢 OpenAI 配置")
        print("=" * 60)
        print()
        print("获取 API Key 步骤：")
        print("  1. 访问：https://platform.openai.com/api-keys")
        print("  2. 登录 OpenAI 账号")
        print("  3. 创建 API Key")
        print()
        print("⚠️  注意：使用 OpenAI 需要科学上网")
        print()
        
        api_key = input("请输入 OpenAI API Key：").strip()
        
        if api_key:
            print()
            print("⏳ 正在配置...")
            
            try:
                subprocess.run(["openclaw", "config", "set", "model", "openai"], capture_output=True)
                result = subprocess.run(
                    ["openclaw", "config", "set", "providers.openai.apiKey", api_key],
                    capture_output=True, text=True
                )
                
                if result.returncode == 0:
                    print("✅ OpenAI API Key 配置成功！")
                    return True
                else:
                    print(f"⚠️  配置失败：{result.stderr}")
            except Exception as e:
                print(f"⚠️  配置出错：{e}")
        else:
            print("⚠️  未输入 API Key")
    
    return False


def check_git():
    """检查 Git 是否安装"""
    try:
        result = subprocess.run(["git", "--version"], capture_output=True, text=True, shell=True)
        return result.returncode == 0
    except:
        return False


def install_git_windows():
    """在 Windows 上安装 Git"""
    print("   正在安装 Git...")
    
    # 方法1: 使用 winget
    try:
        result = subprocess.run(["winget", "--version"], capture_output=True, text=True, shell=True)
        if result.returncode == 0:
            print("   使用 winget 安装 Git...")
            install_result = subprocess.run(
                ["winget", "install", "Git.Git", "--accept-source-agreements", "--accept-package-agreements"],
                capture_output=True, text=True, shell=True
            )
            if install_result.returncode == 0:
                print("   ✅ Git 安装成功")
                return True
    except:
        pass
    
    # 方法2: 使用 chocolatey
    try:
        result = subprocess.run(["choco", "--version"], capture_output=True, text=True, shell=True)
        if result.returncode == 0:
            print("   使用 Chocolatey 安装 Git...")
            os.system("choco install git -y")
            return True
    except:
        pass
    
    # 方法3: 下载安装包（使用国内镜像）
    print("   📥 正在下载 Git 安装包...")
    print("   使用国内镜像加速下载...")
    
    # 使用国内镜像
    git_mirrors = [
        ("https://mirrors.huaweicloud.com/git-for-windows/v2.47.1.windows.1/Git-2.47.1-64-bit.exe", "华为云镜像"),
        ("https://npmmirror.com/mirrors/git-for-windows/v2.47.1.windows.1/Git-2.47.1-64-bit.exe", "淘宝镜像"),
        ("https://github.com/git-for-windows/git/releases/download/v2.47.1.windows.1/Git-2.47.1-64-bit.exe", "GitHub官方"),
    ]
    
    installer_path = os.path.join(os.environ.get("TEMP", "."), "git_installer.exe")
    download_success = False
    
    for git_url, mirror_name in git_mirrors:
        print(f"   尝试 {mirror_name}...")
        try:
            download_cmd = f'powershell -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri \'{git_url}\' -OutFile \'{installer_path}\' -UseBasicParsing"'
            result = os.system(download_cmd)
            
            if os.path.exists(installer_path) and os.path.getsize(installer_path) > 10000000:  # 至少 10MB
                print(f"   ✅ 从 {mirror_name} 下载成功")
                download_success = True
                break
            else:
                print(f"   ⚠️  {mirror_name} 下载失败，尝试下一个...")
        except Exception as e:
            print(f"   ⚠️  {mirror_name} 失败: {e}")
    
    if download_success and os.path.exists(installer_path):
        print("   ✅ 下载完成，正在启动安装程序...")
        print("   ⚠️  请在弹出的安装窗口中完成安装")
        print("   提示：安装选项全部默认即可，一路点 Next")
        os.system(f'"{installer_path}"')
        return True
    else:
        print("   ❌ 自动下载失败")
        print()
        print("   请手动下载安装 Git：")
        print("   华为镜像：https://mirrors.huaweicloud.com/git-for-windows/")
        print("   淘宝镜像：https://npmmirror.com/mirrors/git-for-windows/")
        print("   官网：https://git-scm.com/download/win")


def install_nodejs(system):
    """安装 Node.js"""
    if system == "Linux":
        print("   执行安装命令...")
        print("   安装 Node.js v22 LTS...")
        os.system("curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -")
        os.system("sudo apt-get install -y nodejs")
    elif system == "Darwin":
        print("   请执行：brew install node")
    elif system == "Windows":
        print("   正在检测安装方式...")
        
        # 方法1: 尝试使用 winget (Windows 11 自带)
        try:
            result = subprocess.run(["winget", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                print("   ✅ 检测到 winget，正在自动安装 Node.js...")
                print("   ⏳ 这可能需要几分钟，请稍候...")
                
                install_result = subprocess.run(
                    ["winget", "install", "OpenJS.NodeJS.LTS", "--accept-source-agreements", "--accept-package-agreements"],
                    capture_output=True, text=True, shell=True
                )
                
                if install_result.returncode == 0:
                    print("   ✅ Node.js 安装成功！")
                    return True
                else:
                    print(f"   ⚠️  winget 安装失败：{install_result.stderr}")
        except FileNotFoundError:
            pass
        
        # 方法2: 尝试使用 chocolatey
        try:
            result = subprocess.run(["choco", "--version"], capture_output=True, text=True, shell=True)
            if result.returncode == 0:
                print("   ✅ 检测到 Chocolatey，正在自动安装 Node.js...")
                os.system("choco install nodejs-lts -y")
                print("   ✅ Node.js 安装完成！")
                return True
        except FileNotFoundError:
            pass
        
        # 方法3: 下载安装包（使用国内镜像）
        print("   📥 正在下载 Node.js 安装包...")
        print("   使用国内镜像加速下载...")
        print("   安装版本：Node.js v22.22.1 (LTS)")
        
        nodejs_mirrors = [
            ("https://npmmirror.com/mirrors/node/v22.22.1/node-v22.22.1-x64.msi", "淘宝镜像"),
            ("https://mirrors.huaweicloud.com/nodejs/v22.22.1/node-v22.22.1-x64.msi", "华为云镜像"),
            ("https://nodejs.org/dist/v22.22.1/node-v22.22.1-x64.msi", "Node.js官方"),
        ]
        
        installer_path = os.path.join(os.environ.get("TEMP", "."), "nodejs_installer.msi")
        download_success = False
        
        for nodejs_url, mirror_name in nodejs_mirrors:
            print(f"   尝试 {mirror_name}...")
            try:
                download_cmd = f'powershell -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri \'{nodejs_url}\' -OutFile \'{installer_path}\' -UseBasicParsing"'
                result = os.system(download_cmd)
                
                if os.path.exists(installer_path) and os.path.getsize(installer_path) > 20000000:  # 至少 20MB
                    print(f"   ✅ 从 {mirror_name} 下载成功")
                    download_success = True
                    break
                else:
                    # 删除不完整的文件
                    if os.path.exists(installer_path):
                        os.remove(installer_path)
                    print(f"   ⚠️  {mirror_name} 下载失败，尝试下一个...")
            except Exception as e:
                print(f"   ⚠️  {mirror_name} 失败: {e}")
        
        if download_success:
            print("   ✅ 下载完成，正在启动安装程序...")
            print("   ⚠️  请在弹出的安装窗口中完成安装")
            os.system(f'msiexec /i "{installer_path}"')
            return True
        else:
            print("   ❌ 自动下载失败")
            print()
            print("   请手动下载安装 Node.js：")
            print("   淘宝镜像：https://npmmirror.com/mirrors/node/")
            print("   官网：https://nodejs.org/")
    
    return True


def main(requests):
    """主函数"""
    logger = logging.getLogger(__name__)
    
    clear_screen()
    print_header()
    
    # 输入激活码
    print("🔑 请输入激活码")
    print("   格式：OPENCLAW-XXXX-XXXX-XXXX")
    print()
    
    try:
        license_key = input("激活码：").strip()
    except EOFError:
        error_msg = "输入错误：无法读取输入（可能是以非交互方式启动）"
        print(f"\n❌ {error_msg}")
        logger.error(error_msg)
        pause_exit()
        return
    
    if not license_key:
        print("❌ 激活码不能为空")
        pause_exit()
        return
    
    # 验证激活码
    if not verify_license(license_key, requests):
        pause_exit()
        return
    
    # 选择部署模式
    print()
    try:
        mode = select_deploy_mode()
    except EOFError:
        error_msg = "输入错误：无法读取输入"
        print(f"\n❌ {error_msg}")
        logger.error(error_msg)
        pause_exit()
        return
    
    if mode == 1:
        # 云服务器部署
        try:
            server_info = get_server_info()
            deploy_to_server(server_info)
        except Exception as e:
            error_msg = f"服务器配置过程出错：{e}"
            print(f"\n❌ {error_msg}")
            logger.error(error_msg, exc_info=True)
            pause_exit()
            return
    else:
        # 本地部署
        try:
            local_info = get_local_info()
            deploy_local(local_info)
        except Exception as e:
            error_msg = f"本地部署过程出错：{e}"
            print(f"\n❌ {error_msg}")
            logger.error(error_msg, exc_info=True)
            pause_exit()
            return
    
    # 暂停等待用户确认
    pause_exit("✅ 完成！按回车键退出...")


def global_exception_handler(exc_type, exc_value, exc_traceback):
    """全局异常处理器 - 捕获所有未处理的异常"""
    logger = logging.getLogger(__name__)
    
    # 忽略 KeyboardInterrupt（用户按 Ctrl+C）
    if issubclass(exc_type, KeyboardInterrupt):
        print("\n\n👋 用户取消，再见！")
        return
    
    # 记录完整错误信息到日志
    error_message = f"未处理的异常 - 类型：{exc_type.__name__}, 消息：{exc_value}"
    traceback_str = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    
    logger.error(error_message)
    logger.error(traceback_str)
    
    # 显示用户友好的错误信息
    print()
    print("=" * 60)
    print("❌ 程序发生错误")
    print("=" * 60)
    print()
    print(f"错误类型：{exc_type.__name__}")
    print(f"错误信息：{exc_value}")
    print()
    print("详细错误信息已记录到日志文件：deploy_client_error.log")
    print()
    print("如果问题持续，请联系技术支持并提供日志文件。")
    print()
    
    # Windows 下确保控制台窗口不会立即关闭
    if os.name == 'nt':
        print("按回车键退出...")
        try:
            input()
        except:
            pass
    else:
        pause_exit("按回车键退出...")


# 配置 VERIFY_SERVER 在依赖检查之后
VERIFY_SERVER = "http://180.76.100.92:5000/api/verify"


if __name__ == "__main__":
    # 设置日志
    logger = setup_logging()
    
    # 安装全局异常处理器
    sys.excepthook = global_exception_handler
    
    try:
        # 检查依赖
        requests = check_dependencies()
        
        # 运行主程序
        main(requests)
        
    except SystemExit:
        # 正常退出，不处理
        raise
    except Exception as e:
        # 最后的防线 - 捕获任何漏网之鱼
        logger.critical(f"程序崩溃：{e}", exc_info=True)
        print(f"\n❌ 程序崩溃：{e}")
        print("详细信息请查看日志文件：deploy_client_error.log")
        if os.name == 'nt':
            print("\n按回车键退出...")
            try:
                input()
            except:
                pass
        sys.exit(1)
