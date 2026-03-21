#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenClaw Doctor - 一键获取访问链接
自动检测服务状态，生成/读取 token，显示访问链接
"""

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import os
import sys
import json
import webbrowser
import secrets
import platform

# ============= 配置 =============
VERSION = "1.0.0"
DEFAULT_PORT = 18789
CONFIG_PATH = os.path.expanduser("~/.openclaw/openclaw.json")

# ============= 品牌配色 =============
COLOR_PRIMARY = "#C62828"      # 品牌红（龙虾红）
COLOR_ACCENT = "#FF6D00"      # 强调色（橙色）
COLOR_BG = "#F5F5F5"          # 背景灰
COLOR_TEXT = "#333333"        # 文字灰
COLOR_SUCCESS = "#2E7D32"     # 成功绿
COLOR_ERROR = "#C62828"       # 错误红
COLOR_WARNING = "#F57C00"     # 警告橙

# 字体
if platform.system() == "Windows":
    FONT_FAMILY = "Microsoft YaHei"
else:
    FONT_FAMILY = "Arial"


class OpenClawDoctor:
    """OpenClaw Doctor 主类"""
    
    def __init__(self):
        self.root = tk.Tk()
        
        # Windows DPI 感知
        try:
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(1)
        except:
            pass
        
        self.root.title("OpenClaw Doctor")
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        
        # 居中显示
        self.center_window()
        
        # 设置样式
        self.setup_styles()
        
        # 状态变量
        self.status = tk.StringVar(value="正在检测...")
        self.token = tk.StringVar(value="")
        self.access_url = tk.StringVar(value="")
        
        # 创建界面
        self.create_ui()
        
        # 自动检测
        self.root.after(500, self.auto_check)
        
    def center_window(self):
        """窗口居中"""
        self.root.update_idletasks()
        width = 500
        height = 400
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
    def setup_styles(self):
        """设置样式"""
        style = ttk.Style()
        style.theme_use('clam')
        self.root.configure(bg=COLOR_BG)
        
        # 按钮样式
        style.configure('Primary.TButton',
                       font=(FONT_FAMILY, 11, 'bold'),
                       padding=(20, 10))
        
        style.configure('TButton',
                       font=(FONT_FAMILY, 10),
                       padding=(15, 8))
        
        # 标题样式
        style.configure('Title.TLabel',
                       font=(FONT_FAMILY, 20, 'bold'),
                       foreground=COLOR_PRIMARY,
                       background=COLOR_BG)
        
        # 正文样式
        style.configure('Body.TLabel',
                       font=(FONT_FAMILY, 11),
                       foreground=COLOR_TEXT,
                       background=COLOR_BG)
        
        # 状态样式
        style.configure('Status.TLabel',
                       font=(FONT_FAMILY, 12, 'bold'),
                       background=COLOR_BG)
        
        # 链接样式
        style.configure('Link.TLabel',
                       font=(FONT_FAMILY, 10),
                       foreground='#0066CC',
                       background=COLOR_BG)
        
    def create_ui(self):
        """创建界面"""
        # 主框架
        main_frame = ttk.Frame(self.root, style='TFrame', padding=30)
        main_frame.pack(fill='both', expand=True)
        
        # 标题
        title_frame = ttk.Frame(main_frame, style='TFrame')
        title_frame.pack(pady=(0, 20))
        
        ttk.Label(title_frame, text="🦞 OpenClaw Doctor", style='Title.TLabel').pack()
        ttk.Label(title_frame, text="一键获取访问链接", font=(FONT_FAMILY, 10), 
                 foreground='gray', background=COLOR_BG).pack()
        
        # 状态区域
        status_frame = ttk.LabelFrame(main_frame, text="服务状态", padding=15)
        status_frame.pack(fill='x', pady=10)
        
        self.status_label = ttk.Label(status_frame, textvariable=self.status, 
                                      style='Status.TLabel')
        self.status_label.pack()
        
        # 访问链接区域
        url_frame = ttk.LabelFrame(main_frame, text="访问链接", padding=15)
        url_frame.pack(fill='x', pady=10)
        
        # 链接显示
        self.url_entry = ttk.Entry(url_frame, textvariable=self.access_url, 
                                   font=(FONT_FAMILY, 10), width=50)
        self.url_entry.pack(pady=5)
        
        # 按钮区域
        btn_frame = ttk.Frame(url_frame, style='TFrame')
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="📋 复制链接", command=self.copy_url, 
                  width=15).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="🌐 打开浏览器", command=self.open_browser,
                  width=15).pack(side='left', padx=5)
        
        # 操作按钮区域
        action_frame = ttk.Frame(main_frame, style='TFrame')
        action_frame.pack(fill='x', pady=20)
        
        ttk.Button(action_frame, text="🔄 重新检测", command=self.auto_check,
                  width=15).pack(side='left', padx=5)
        ttk.Button(action_frame, text="🔧 生成新 Token", command=self.generate_token,
                  width=15).pack(side='left', padx=5)
        
        # 底部信息
        footer_frame = ttk.Frame(main_frame, style='TFrame')
        footer_frame.pack(side='bottom', fill='x')
        
        ttk.Label(footer_frame, text=f"版本 {VERSION}", font=(FONT_FAMILY, 9),
                 foreground='gray', background=COLOR_BG).pack()
        
    def auto_check(self):
        """自动检测服务状态"""
        self.status.set("正在检测...")
        self.status_label.config(foreground=COLOR_WARNING)
        self.root.update()
        
        # 1. 检测 OpenClaw 是否安装
        if not self.check_openclaw_installed():
            self.status.set("❌ OpenClaw 未安装")
            self.status_label.config(foreground=COLOR_ERROR)
            self.access_url.set("")
            return
        
        # 2. 检测服务是否运行
        if not self.check_service_running():
            self.status.set("⚠️ 服务未运行，正在尝试启动...")
            self.status_label.config(foreground=COLOR_WARNING)
            self.root.update()
            
            # 尝试启动服务
            if self.start_service():
                self.status.set("✅ 服务已启动")
            else:
                self.status.set("❌ 服务启动失败，请手动运行 openclaw gateway")
                self.status_label.config(foreground=COLOR_ERROR)
                return
        
        # 3. 获取 token
        token = self.get_token()
        if token:
            self.token.set(token)
            self.status.set("✅ 服务运行中")
            self.status_label.config(foreground=COLOR_SUCCESS)
            self.access_url.set(f"http://127.0.0.1:{DEFAULT_PORT}/#token={token}")
        else:
            # 尝试生成 token
            if self.generate_token():
                self.status.set("✅ Token 已生成")
                self.status_label.config(foreground=COLOR_SUCCESS)
            else:
                self.status.set("❌ Token 获取失败")
                self.status_label.config(foreground=COLOR_ERROR)
                
    def check_openclaw_installed(self):
        """检测 OpenClaw 是否安装"""
        # Windows 下检查 openclaw 命令
        if platform.system() == "Windows":
            try:
                result = subprocess.run(["where", "openclaw"], 
                                       shell=True, capture_output=True, timeout=5)
                if result.returncode == 0:
                    return True
            except:
                pass
            
            # 检查常见安装路径
            npm_path = os.path.expandvars(r"%APPDATA%\npm\openclaw.cmd")
            if os.path.exists(npm_path):
                return True
        else:
            # Linux/Mac
            try:
                result = subprocess.run(["which", "openclaw"],
                                       capture_output=True, timeout=5)
                if result.returncode == 0:
                    return True
            except:
                pass
        
        # 检查配置目录是否存在
        if os.path.exists(os.path.dirname(CONFIG_PATH)):
            return True
            
        return False
    
    def check_service_running(self):
        """检测服务是否运行"""
        try:
            # 检查端口是否被占用
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex(('127.0.0.1', DEFAULT_PORT))
            sock.close()
            return result == 0
        except:
            return False
    
    def start_service(self):
        """尝试启动服务"""
        try:
            # 检查 PM2 是否有 openclaw 进程
            result = subprocess.run(["pm2", "list"], 
                                   shell=True, capture_output=True, text=True, timeout=10)
            if "openclaw" in result.stdout:
                # 有 PM2 进程，尝试恢复
                subprocess.run(["pm2", "resurrect"], 
                              shell=True, capture_output=True, timeout=30)
                import time
                time.sleep(3)
                return self.check_service_running()
            
            # 没有 PM2，尝试直接启动
            if platform.system() == "Windows":
                # Windows: 找到 openclaw 路径
                openclaw_paths = [
                    os.path.expandvars(r"%APPDATA%\npm\openclaw.cmd"),
                    r"C:\Program Files\nodejs\openclaw.cmd",
                ]
                
                for openclaw_path in openclaw_paths:
                    if os.path.exists(openclaw_path):
                        # 后台启动
                        subprocess.Popen([openclaw_path, "gateway"],
                                       shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        import time
                        time.sleep(5)
                        return self.check_service_running()
        except Exception as e:
            print(f"启动服务失败: {e}")
            
        return False
    
    def get_token(self):
        """从配置文件获取 token"""
        try:
            if os.path.exists(CONFIG_PATH):
                with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    token = config.get('gateway', {}).get('auth', {}).get('token', '')
                    return token
        except Exception as e:
            print(f"读取 token 失败: {e}")
        return ""
    
    def generate_token(self):
        """生成新的 token"""
        try:
            # 生成随机 token
            token = secrets.token_hex(16)
            
            # 读取现有配置
            config = {}
            if os.path.exists(CONFIG_PATH):
                try:
                    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                except:
                    pass
            
            # 设置新 token
            if 'gateway' not in config:
                config['gateway'] = {}
            if 'auth' not in config['gateway']:
                config['gateway']['auth'] = {}
            
            config['gateway']['auth']['token'] = token
            
            # 保存配置
            os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
            with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            # 更新界面
            self.token.set(token)
            self.access_url.set(f"http://127.0.0.1:{DEFAULT_PORT}/#token={token}")
            
            return True
        except Exception as e:
            messagebox.showerror("错误", f"生成 Token 失败：{e}")
            return False
    
    def copy_url(self):
        """复制链接到剪贴板"""
        url = self.access_url.get()
        if url:
            self.root.clipboard_clear()
            self.root.clipboard_append(url)
            messagebox.showinfo("成功", "链接已复制到剪贴板！")
        else:
            messagebox.showwarning("提示", "没有可复制的链接")
    
    def open_browser(self):
        """打开浏览器"""
        url = self.access_url.get()
        if url:
            webbrowser.open(url)
        else:
            messagebox.showwarning("提示", "没有可打开的链接")
    
    def run(self):
        """运行程序"""
        self.root.mainloop()


if __name__ == "__main__":
    app = OpenClawDoctor()
    app.run()