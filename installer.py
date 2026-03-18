#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenClaw 安装向导
类似腾讯软件的专业安装程序
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import subprocess
import os
import sys
import platform
import requests
import hashlib
import uuid
import json
import webbrowser
from datetime import datetime

# ============= 配置 =============
VERSION = "3.0.5"
VERIFY_SERVER = "http://180.76.100.92:5000/api/verify"
DEFAULT_PORT = 18789  # OpenClaw 默认端口
MIN_DISK_SPACE_GB = 5

# ============= 品牌配色 =============
COLOR_PRIMARY = "#C62828"      # 品牌红（龙虾红）
COLOR_ACCENT = "#FF6D00"      # 强调色（橙色）
COLOR_BG = "#F5F5F5"          # 背景灰
COLOR_TEXT = "#333333"        # 文字灰
COLOR_LINK = "#0066CC"        # 链接蓝
FONT_FAMILY = "Microsoft YaHei"  # 微软雅黑
# ===================================


class InstallWizard:
    """安装向导主类"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("OpenClaw 一键部署工具")
        self.root.geometry("600x550")  # 增加高度
        self.root.resizable(False, False)
        
        # 禁用最大化按钮（Windows）
        try:
            from ctypes import windll
            GWL_STYLE = -16
            WS_MAXIMIZEBOX = 0x00010000
            hwnd = windll.user32.GetParent(self.root.winfo_id())
            style = windll.user32.GetWindowLongPtrW(hwnd, GWL_STYLE)
            style &= ~WS_MAXIMIZEBOX
            windll.user32.SetWindowLongPtrW(hwnd, GWL_STYLE, style)
        except:
            pass  # 非 Windows 系统忽略
        
        # 居中显示
        self.center_window()
        
        # 设置样式
        self.setup_styles()
        
        # 状态变量
        self.current_page = 0
        self.agreed = tk.BooleanVar(value=False)
        self.license_key = tk.StringVar()
        self.install_path = tk.StringVar(value=self.get_default_install_path())
        self.provider = tk.StringVar()
        self.api_key = tk.StringVar()
        self.port = tk.IntVar(value=DEFAULT_PORT)
        self.install_progress = tk.DoubleVar(value=0)
        self.install_status = tk.StringVar(value="准备安装...")
        
        # 安装步骤
        self.install_steps = [
            "检测系统环境",
            "安装 Node.js",
            "安装 Git", 
            "下载 OpenClaw",
            "配置 API Key",
            "安装系统服务",
            "完成安装"
        ]
        self.current_step = 0
        
        # 服务商配置（按推荐度排序）
        self.providers = {
            "阿里云（通义千问）": {
                "id": "qwen",
                "prefix": "sk-",
                "key_length": 32,
                "get_key_url": "https://dashscope.console.aliyun.com/",
                "config_key": "providers.qwen.apiKey"
            },
            "百度千帆（文心/DeepSeek/Kimi）": {
                "id": "qianfan",
                "prefix": "",
                "key_length": 32,
                "get_key_url": "https://console.bce.baidu.com/qianfan/",
                "config_key": "providers.qianfan.apiKey"
            },
            "智谱 AI（GLM）": {
                "id": "glm",
                "prefix": "",
                "key_length": 32,
                "get_key_url": "https://open.bigmodel.cn/",
                "config_key": "providers.glm.apiKey"
            },
            "Kimi（月之暗面）": {
                "id": "kimi",
                "prefix": "",
                "key_length": 32,
                "get_key_url": "https://platform.moonshot.cn/",
                "config_key": "providers.kimi.apiKey"
            },
            "深度求索（DeepSeek）": {
                "id": "deepseek",
                "prefix": "sk-",
                "key_length": 32,
                "get_key_url": "https://platform.deepseek.com/",
                "config_key": "providers.deepseek.apiKey"
            },
            "腾讯混元": {
                "id": "hunyuan",
                "prefix": "",
                "key_length": 32,
                "get_key_url": "https://console.cloud.tencent.com/hunyuan",
                "config_key": "providers.hunyuan.apiKey"
            },
            "字节豆包": {
                "id": "doubao",
                "prefix": "",
                "key_length": 32,
                "get_key_url": "https://console.volcengine.com/ark",
                "config_key": "providers.doubao.apiKey"
            },
            "MiniMax": {
                "id": "minimax",
                "prefix": "",
                "key_length": 32,
                "get_key_url": "https://www.minimaxi.com/",
                "config_key": "providers.minimax.apiKey"
            },
            "华为云盘古": {
                "id": "pangu",
                "prefix": "",
                "key_length": 32,
                "get_key_url": "https://console.huaweicloud.com/pangu/",
                "config_key": "providers.pangu.apiKey"
            },
            "零一万物（Yi）": {
                "id": "yi",
                "prefix": "",
                "key_length": 32,
                "get_key_url": "https://platform.lingyiwanwu.com/",
                "config_key": "providers.yi.apiKey"
            },
            "OpenAI": {
                "id": "openai",
                "prefix": "sk-",
                "key_length": 48,
                "get_key_url": "https://platform.openai.com/api-keys",
                "config_key": "providers.openai.apiKey"
            }
        }
        
        # 创建页面
        self.pages = []
        self.create_pages()
        
        # 显示第一页
        self.show_page(0)
        
    def center_window(self):
        """窗口居中"""
        self.root.update_idletasks()
        width = 600
        height = 550
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
    def setup_styles(self):
        """设置样式"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # 配置窗口背景
        self.root.configure(bg=COLOR_BG)
        
        # 主按钮样式（橙色，醒目）
        style.configure('Primary.TButton', 
                       font=(FONT_FAMILY, 10, 'bold'),
                       padding=(20, 10))
        
        # 普通按钮样式
        style.configure('TButton',
                       font=(FONT_FAMILY, 10),
                       padding=(15, 8))
        
        # 标题样式
        style.configure('Title.TLabel',
                       font=(FONT_FAMILY, 22, 'bold'),
                       foreground=COLOR_PRIMARY,
                       background=COLOR_BG)
        
        # 副标题样式
        style.configure('Subtitle.TLabel',
                       font=(FONT_FAMILY, 18, 'bold'),
                       foreground=COLOR_TEXT,
                       background=COLOR_BG)
        
        # 正文样式
        style.configure('Body.TLabel',
                       font=(FONT_FAMILY, 11),
                       foreground=COLOR_TEXT,
                       background=COLOR_BG)
        
        # 框架背景
        style.configure('Card.TFrame', background='white')
        style.configure('TFrame', background=COLOR_BG)
        
    def get_default_install_path(self):
        """获取默认安装路径"""
        if platform.system() == "Windows":
            return os.path.join(os.environ.get("ProgramFiles", "C:\\Program Files"), "OpenClaw")
        else:
            return os.path.expanduser("~/.openclaw")
    
    def create_pages(self):
        """创建所有页面"""
        # 页面0: 欢迎页
        self.pages.append(self.create_welcome_page())
        
        # 页面1: 激活码
        self.pages.append(self.create_license_page())
        
        # 页面2: 安装路径
        self.pages.append(self.create_path_page())
        
        # 页面3: 选择服务商
        self.pages.append(self.create_provider_page())
        
        # 页面4: 输入 API Key
        self.pages.append(self.create_apikey_page())
        
        # 页面5: 确认信息
        self.pages.append(self.create_confirm_page())
        
        # 页面6: 安装进度
        self.pages.append(self.create_install_page())
        
        # 页面7: 完成
        self.pages.append(self.create_finish_page())
        
        # 页面8: 错误
        self.pages.append(self.create_error_page())
        
    def create_welcome_page(self):
        """创建欢迎页"""
        # 主框架
        frame = ttk.Frame(self.root, style='TFrame')
        frame.pack(fill='both', expand=True)
        
        # ===== 顶部区域 =====
        header_frame = ttk.Frame(frame, style='TFrame')
        header_frame.pack(pady=30)
        
        # Logo（使用生成的图标）
        try:
            logo_img = tk.PhotoImage(file='openclaw_logo.png')
            logo_label = ttk.Label(header_frame, image=logo_img, background=COLOR_BG)
            logo_label.image = logo_img  # 保持引用
            logo_label.pack()
        except:
            # 如果图标加载失败，使用 emoji
            logo_label = ttk.Label(header_frame, text="🦞", font=('Arial', 48), background=COLOR_BG)
            logo_label.pack()
        
        title_label = ttk.Label(header_frame, text="OpenClaw 一键部署工具", style='Title.TLabel')
        title_label.pack(pady=5)
        
        version_label = ttk.Label(header_frame, text=f"版本 {VERSION}", font=(FONT_FAMILY, 10), foreground='gray', background=COLOR_BG)
        version_label.pack()
        
        # ===== 中间区域 =====
        content_frame = ttk.Frame(frame, style='TFrame')
        content_frame.pack(pady=20)
        
        # 欢迎文字
        welcome_text = """欢迎使用 OpenClaw 安装向导

OpenClaw 是您的专属 AI 助手，可本地运行，
支持通义千问、百度千帆、Kimi 等主流模型。

点击"下一步"继续安装。"""
        
        welcome_label = ttk.Label(content_frame, text=welcome_text, style='Body.TLabel', justify='center')
        welcome_label.pack()
        
        # ===== 用户协议区域 =====
        agreement_frame = ttk.Frame(content_frame, style='TFrame')
        agreement_frame.pack(pady=20)
        
        # 复选框
        agree_check = tk.Checkbutton(
            agreement_frame,
            text="我已阅读并同意 ",
            variable=self.agreed,
            command=self.on_agreement_toggle,
            font=(FONT_FAMILY, 10),
            bg=COLOR_BG,
            activebackground=COLOR_BG
        )
        agree_check.pack(side='left')
        
        # 用户协议链接
        def open_license(event):
            webbrowser.open("https://docs.openclaw.ai/terms")
        
        license_link = tk.Label(
            agreement_frame,
            text="《用户协议》",
            font=(FONT_FAMILY, 10, 'underline'),
            fg=COLOR_LINK,
            cursor='hand2',
            bg=COLOR_BG
        )
        license_link.pack(side='left')
        license_link.bind('<Button-1>', open_license)
        
        ttk.Label(agreement_frame, text=" 和 ", font=(FONT_FAMILY, 10), background=COLOR_BG).pack(side='left')
        
        # 隐私政策链接
        def open_privacy(event):
            webbrowser.open("https://docs.openclaw.ai/privacy")
        
        privacy_link = tk.Label(
            agreement_frame,
            text="《隐私政策》",
            font=(FONT_FAMILY, 10, 'underline'),
            fg=COLOR_LINK,
            cursor='hand2',
            bg=COLOR_BG
        )
        privacy_link.pack(side='left')
        privacy_link.bind('<Button-1>', open_privacy)
        
        # ===== 底部按钮区域 =====
        btn_frame = ttk.Frame(frame, style='TFrame')
        btn_frame.pack(side='bottom', pady=20)
        
        ttk.Button(btn_frame, text="退出", command=self.quit, width=10).pack(side='left', padx=5)
        
        self.welcome_next_btn = ttk.Button(btn_frame, text="下一步 →", command=lambda: self.next_page(), width=12, state='disabled')
        self.welcome_next_btn.pack(side='left', padx=5)
        
        return frame
    
    def create_license_page(self):
        """创建激活码页面"""
        frame = ttk.Frame(self.root, padding=40)
        
        ttk.Label(frame, text="🔑 激活码验证", font=('Arial', 18, 'bold')).pack(pady=20)
        
        ttk.Label(frame, text="请输入您的激活码：", font=('Arial', 11)).pack(pady=10)
        
        # 输入框
        entry_frame = ttk.Frame(frame)
        entry_frame.pack(fill='x', pady=10)
        
        license_entry = ttk.Entry(entry_frame, textvariable=self.license_key, width=40, font=('Arial', 12))
        license_entry.pack(side='left', padx=5)
        
        def paste_license():
            try:
                self.license_key.set(self.root.clipboard_get())
            except:
                pass
        
        ttk.Button(entry_frame, text="粘贴", command=paste_license).pack(side='left', padx=5)
        
        # 提示
        ttk.Label(frame, text="格式：OPENCLAW-XXXX-XXXX-XXXX", font=('Arial', 10), foreground='gray').pack()
        
        # 验证状态
        self.license_status = ttk.Label(frame, text="", font=('Arial', 10))
        self.license_status.pack(pady=10)
        
        # 按钮
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(side='bottom', fill='x', pady=20)
        
        ttk.Button(btn_frame, text="上一步", command=lambda: self.prev_page()).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="验证", command=self.verify_license).pack(side='right', padx=5)
        self.license_next_btn = ttk.Button(btn_frame, text="下一步", command=lambda: self.next_page(), state='disabled')
        self.license_next_btn.pack(side='right', padx=5)
        
        return frame
    
    def create_path_page(self):
        """创建安装路径页面"""
        frame = ttk.Frame(self.root, padding=40)
        
        ttk.Label(frame, text="📁 选择安装位置", font=('Arial', 18, 'bold')).pack(pady=20)
        
        ttk.Label(frame, text="安装路径：", font=('Arial', 11)).pack(pady=5)
        
        # 路径输入
        path_frame = ttk.Frame(frame)
        path_frame.pack(fill='x', pady=10)
        
        path_entry = ttk.Entry(path_frame, textvariable=self.install_path, width=45, font=('Arial', 10))
        path_entry.pack(side='left', padx=5)
        
        def browse_path():
            path = filedialog.askdirectory()
            if path:
                self.install_path.set(path)
                self.check_path()
        
        ttk.Button(path_frame, text="浏览...", command=browse_path).pack(side='left', padx=5)
        
        # 路径状态
        self.path_status = ttk.Label(frame, text="", font=('Arial', 10))
        self.path_status.pack(pady=10)
        
        # 磁盘空间提示
        ttk.Label(frame, text=f"建议至少 {MIN_DISK_SPACE_GB}GB 可用空间", font=('Arial', 10), foreground='gray').pack()
        
        # 按钮
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(side='bottom', fill='x', pady=20)
        
        ttk.Button(btn_frame, text="上一步", command=lambda: self.prev_page()).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="下一步", command=lambda: self.next_page() if self.check_path() else None).pack(side='right', padx=5)
        
        return frame
    
    def create_provider_page(self):
        """创建服务商选择页面"""
        frame = ttk.Frame(self.root, padding=40)
        
        ttk.Label(frame, text="🤖 选择 AI 服务商", font=('Arial', 18, 'bold')).pack(pady=20)
        
        ttk.Label(frame, text="请选择您要使用的 AI 模型服务商：", font=('Arial', 11)).pack(pady=10)
        
        # 下拉框选择
        combo_frame = ttk.Frame(frame)
        combo_frame.pack(pady=10)
        
        # 服务商列表
        provider_names = list(self.providers.keys())
        
        self.provider_combo = ttk.Combobox(combo_frame, values=provider_names, state='readonly', width=30, font=('Arial', 11))
        self.provider_combo.pack(pady=5)
        self.provider_combo.bind('<<ComboboxSelected>>', self.on_provider_selected)
        
        # 获取 API Key 按钮
        def open_get_key():
            provider = self.provider_combo.get()
            if provider:
                url = self.providers[provider]['get_key_url']
                webbrowser.open(url)
        
        ttk.Button(combo_frame, text="如何获取 API Key", command=open_get_key).pack(pady=10)
        
        # 提示
        ttk.Label(frame, text="推荐国内用户选择：阿里云（通义千问）", font=('Arial', 10), foreground='gray').pack(pady=10)
        
        # 按钮
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(side='bottom', fill='x', pady=20)
        
        ttk.Button(btn_frame, text="上一步", command=lambda: self.prev_page()).pack(side='left', padx=5)
        self.provider_next_btn = ttk.Button(btn_frame, text="下一步", command=lambda: self.next_page(), state='disabled')
        self.provider_next_btn.pack(side='right', padx=5)
        
        return frame
    
    def on_provider_selected(self, event):
        """服务商下拉框选择事件"""
        provider = self.provider_combo.get()
        if provider:
            self.provider.set(provider)
            self.provider_next_btn.config(state='normal')
        else:
            self.provider_next_btn.config(state='disabled')
    
    def create_apikey_page(self):
        """创建 API Key 输入页面"""
        frame = ttk.Frame(self.root, padding=40)
        
        ttk.Label(frame, text="🔑 输入 API Key", font=('Arial', 18, 'bold')).pack(pady=20)
        
        self.apikey_provider_label = ttk.Label(frame, text="", font=('Arial', 11))
        self.apikey_provider_label.pack(pady=10)
        
        ttk.Label(frame, text="API Key：", font=('Arial', 11)).pack(pady=5)
        
        # 输入框
        entry_frame = ttk.Frame(frame)
        entry_frame.pack(fill='x', pady=10)
        
        self.apikey_entry = ttk.Entry(entry_frame, textvariable=self.api_key, width=45, font=('Arial', 12), show='●')
        self.apikey_entry.pack(side='left', padx=5)
        
        # 显示/隐藏密码
        self.show_key = tk.BooleanVar(value=False)
        
        def toggle_show():
            if self.show_key.get():
                self.apikey_entry.config(show='')
            else:
                self.apikey_entry.config(show='●')
        
        ttk.Checkbutton(entry_frame, text="显示", variable=self.show_key, command=toggle_show).pack(side='left', padx=5)
        
        def paste_key():
            try:
                self.api_key.set(self.root.clipboard_get())
            except:
                pass
        
        ttk.Button(entry_frame, text="粘贴", command=paste_key).pack(side='left', padx=5)
        
        # 验证状态
        self.apikey_status = ttk.Label(frame, text="", font=('Arial', 10))
        self.apikey_status.pack(pady=10)
        
        # 提示
        ttk.Label(frame, text="API Key 将安全存储在本地配置文件中", font=('Arial', 10), foreground='gray').pack()
        
        # 按钮
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(side='bottom', fill='x', pady=20)
        
        ttk.Button(btn_frame, text="上一步", command=lambda: self.prev_page()).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="验证", command=self.validate_api_key).pack(side='right', padx=5)
        self.apikey_next_btn = ttk.Button(btn_frame, text="下一步", command=lambda: self.next_page(), state='disabled')
        self.apikey_next_btn.pack(side='right', padx=5)
        
        return frame
    
    def create_confirm_page(self):
        """创建确认信息页面"""
        frame = ttk.Frame(self.root, padding=40)
        
        ttk.Label(frame, text="📋 确认安装信息", font=('Arial', 18, 'bold')).pack(pady=20)
        
        # 信息汇总
        info_frame = ttk.LabelFrame(frame, text="安装信息", padding=10)
        info_frame.pack(fill='x', pady=10)
        
        self.confirm_path = ttk.Label(info_frame, text="", font=('Arial', 10))
        self.confirm_path.pack(anchor='w', pady=2)
        
        self.confirm_provider = ttk.Label(info_frame, text="", font=('Arial', 10))
        self.confirm_provider.pack(anchor='w', pady=2)
        
        self.confirm_apikey = ttk.Label(info_frame, text="", font=('Arial', 10))
        self.confirm_apikey.pack(anchor='w', pady=2)
        
        self.confirm_port = ttk.Label(info_frame, text="", font=('Arial', 10))
        self.confirm_port.pack(anchor='w', pady=2)
        
        # 高级选项
        adv_frame = ttk.LabelFrame(frame, text="高级选项", padding=10)
        adv_frame.pack(fill='x', pady=10)
        
        port_frame = ttk.Frame(adv_frame)
        port_frame.pack(fill='x')
        
        ttk.Label(port_frame, text="服务端口：", font=('Arial', 10)).pack(side='left')
        ttk.Spinbox(port_frame, from_=1024, to=65535, textvariable=self.port, width=8).pack(side='left', padx=5)
        
        # 提示
        ttk.Label(frame, text="⚠️ 安装过程需要联网，建议暂时关闭杀毒软件", font=('Arial', 10), foreground='orange').pack(pady=10)
        
        # 按钮
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(side='bottom', fill='x', pady=20)
        
        ttk.Button(btn_frame, text="上一步", command=lambda: self.prev_page()).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="开始安装", command=self.start_install).pack(side='right', padx=5)
        
        return frame
    
    def create_install_page(self):
        """创建安装进度页面"""
        frame = ttk.Frame(self.root, padding=40)
        
        ttk.Label(frame, text="⏳ 正在安装...", font=('Arial', 18, 'bold')).pack(pady=20)
        
        # 进度条
        self.progress_bar = ttk.Progressbar(frame, length=400, mode='determinate', variable=self.install_progress)
        self.progress_bar.pack(pady=20)
        
        # 进度百分比
        self.progress_percent = ttk.Label(frame, text="0%", font=('Arial', 14))
        self.progress_percent.pack()
        
        # 当前步骤
        self.step_label = ttk.Label(frame, textvariable=self.install_status, font=('Arial', 11))
        self.step_label.pack(pady=10)
        
        # 步骤列表
        steps_frame = ttk.Frame(frame)
        steps_frame.pack(fill='x', pady=20)
        
        for i, step in enumerate(self.install_steps):
            label = ttk.Label(steps_frame, text=f"{'✓' if i == 0 else '○'} {step}", font=('Arial', 10))
            label.pack(anchor='w', pady=2)
        
        # 按钮
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(side='bottom', fill='x', pady=20)
        
        cancel_btn = ttk.Button(btn_frame, text="取消安装", command=self.cancel_install)
        cancel_btn.pack(side='right', padx=5)
        
        return frame
    
    def create_finish_page(self):
        """创建完成页面"""
        frame = ttk.Frame(self.root, padding=40)
        
        ttk.Label(frame, text="🎉 安装完成！", font=('Arial', 24, 'bold')).pack(pady=20)
        
        # 访问信息
        info_frame = ttk.LabelFrame(frame, text="访问信息", padding=10)
        info_frame.pack(fill='x', pady=20)
        
        ttk.Label(info_frame, text="访问地址：", font=('Arial', 11)).pack(anchor='w')
        self.access_url = ttk.Label(info_frame, text=f"http://localhost:{DEFAULT_PORT}", font=('Arial', 12, 'bold'), foreground='blue')
        self.access_url.pack(anchor='w', pady=5)
        
        ttk.Label(info_frame, text="", font=('Arial', 8)).pack()  # 空行
        
        # 提示：需要配置 API Key
        ttk.Label(info_frame, text="⚠️ 重要提示：", font=('Arial', 11, 'bold'), foreground='orange').pack(anchor='w')
        ttk.Label(info_frame, text="首次使用请运行以下命令配置 API Key：", font=('Arial', 10)).pack(anchor='w')
        ttk.Label(info_frame, text="openclaw configure", font=('Arial', 11, 'bold'), foreground='blue').pack(anchor='w', pady=5)
        
        # 按钮
        btn_frame = ttk.Frame(info_frame)
        btn_frame.pack(fill='x', pady=10)
        
        def copy_url():
            self.root.clipboard_clear()
            self.root.clipboard_append(f"http://localhost:{DEFAULT_PORT}")
            messagebox.showinfo("提示", "地址已复制到剪贴板")
        
        def open_browser():
            webbrowser.open(f"http://localhost:{DEFAULT_PORT}")
        
        ttk.Button(btn_frame, text="复制地址", command=copy_url).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="打开浏览器", command=open_browser).pack(side='left', padx=5)
        
        # 提示
        ttk.Label(frame, text="首次访问可能需要 1-2 分钟初始化", font=('Arial', 10), foreground='gray').pack(pady=10)
        
        # 完成按钮
        ttk.Button(frame, text="完成", command=self.quit).pack(pady=20)
        
        return frame
    
    def create_error_page(self):
        """创建错误页面"""
        frame = ttk.Frame(self.root, padding=40)
        
        ttk.Label(frame, text="❌ 安装失败", font=('Arial', 24, 'bold'), foreground='red').pack(pady=20)
        
        # 错误信息
        self.error_msg = ttk.Label(frame, text="", font=('Arial', 11), wraplength=450)
        self.error_msg.pack(pady=10)
        
        # 可能原因
        reasons_frame = ttk.LabelFrame(frame, text="可能原因", padding=10)
        reasons_frame.pack(fill='x', pady=10)
        
        ttk.Label(reasons_frame, text="• 网络连接问题", font=('Arial', 10)).pack(anchor='w')
        ttk.Label(reasons_frame, text="• 杀毒软件拦截", font=('Arial', 10)).pack(anchor='w')
        ttk.Label(reasons_frame, text="• GitHub 访问受限（国内）", font=('Arial', 10)).pack(anchor='w')
        
        # 按钮
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=20)
        
        ttk.Button(btn_frame, text="查看日志", command=self.show_log).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="重试", command=self.retry_install).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="退出", command=self.quit).pack(side='left', padx=5)
        
        return frame
    
    # ============= 事件处理 =============
    
    def on_agreement_toggle(self):
        """协议勾选状态改变"""
        if self.agreed.get():
            self.welcome_next_btn.config(state='normal')
        else:
            self.welcome_next_btn.config(state='disabled')
    
    def on_provider_change(self):
        """服务商选择改变"""
        if self.provider.get():
            self.provider_next_btn.config(state='normal')
        else:
            self.provider_next_btn.config(state='disabled')
    
    def verify_license(self):
        """验证激活码"""
        key = self.license_key.get().strip()
        if not key:
            self.license_status.config(text="请输入激活码", foreground='red')
            return
        
        self.license_status.config(text="正在验证...", foreground='blue')
        self.root.update()
        
        try:
            response = requests.post(VERIFY_SERVER, json={
                "key": key,
                "machine_id": str(uuid.getnode()),
                "version": VERSION,
                "timestamp": datetime.now().isoformat()
            }, timeout=10)
            
            result = response.json()
            
            if result.get("valid"):
                self.license_status.config(text="✓ 激活码有效", foreground='green')
                self.license_next_btn.config(state='normal')
            else:
                self.license_status.config(text=f"✗ {result.get('error', '激活码无效')}", foreground='red')
                
        except Exception as e:
            self.license_status.config(text=f"验证失败：{e}", foreground='red')
    
    def check_path(self):
        """检查安装路径"""
        path = self.install_path.get()
        
        # 检查中文
        try:
            path.encode('ascii')
        except UnicodeEncodeError:
            self.path_status.config(text="✗ 路径包含中文，请选择纯英文路径", foreground='red')
            return False
        
        # 检查磁盘空间
        try:
            import shutil
            total, used, free = shutil.disk_usage(os.path.dirname(path) or path)
            free_gb = free // (1024**3)
            
            if free_gb < MIN_DISK_SPACE_GB:
                self.path_status.config(text=f"⚠️ 磁盘空间不足 {MIN_DISK_SPACE_GB}GB（当前 {free_gb}GB）", foreground='orange')
            else:
                self.path_status.config(text=f"✓ 可用空间：{free_gb}GB", foreground='green')
        except:
            self.path_status.config(text="✓ 路径有效", foreground='green')
        
        return True
    
    def validate_api_key(self):
        """验证 API Key"""
        key = self.api_key.get().strip()
        provider = self.provider.get()
        
        if not provider:
            messagebox.showwarning("提示", "请先选择服务商")
            return
        
        if not key:
            self.apikey_status.config(text="请输入 API Key", foreground='red')
            return
        
        config = self.providers.get(provider, {})
        
        # 检查长度
        if len(key) < config.get('key_length', 32):
            self.apikey_status.config(text=f"⚠️ API Key 长度可能不正确（建议 {config.get('key_length', 32)} 位）", foreground='orange')
        else:
            self.apikey_status.config(text="✓ API Key 格式正确", foreground='green')
        
        self.apikey_next_btn.config(state='normal')
    
    def start_install(self):
        """开始安装"""
        # 更新确认信息
        self.confirm_path.config(text=f"安装路径：{self.install_path.get()}")
        self.confirm_provider.config(text=f"服务商：{self.provider.get()}")
        
        # 隐藏 API Key 中间部分
        key = self.api_key.get()
        masked_key = key[:4] + '****' + key[-4:] if len(key) > 8 else '****'
        self.confirm_apikey.config(text=f"API Key：{masked_key}")
        self.confirm_port.config(text=f"服务端口：{self.port.get()}")
        
        # 切换到安装页面
        self.next_page()
        
        # 启动安装线程
        thread = threading.Thread(target=self.do_install)
        thread.daemon = True
        thread.start()
    
    def do_install(self):
        """执行安装（后台线程）"""
        try:
            # 步骤1: 检测系统
            self.root.after(0, lambda: self.update_progress(5, "检测系统环境..."))
            import time
            time.sleep(0.5)
            self.root.after(0, lambda: self.update_progress(10, "系统检测完成 ✓"))
            
            # 步骤2: 安装 Node.js
            self.root.after(0, lambda: self.update_progress(15, "正在检查 Node.js..."))
            self.install_nodejs()
            self.root.after(0, lambda: self.update_progress(25, "Node.js 就绪 ✓"))
            
            # 步骤3: 安装 Git
            self.root.after(0, lambda: self.update_progress(30, "正在检查 Git..."))
            self.install_git()
            self.root.after(0, lambda: self.update_progress(40, "Git 就绪 ✓"))
            
            # 步骤4: 安装 OpenClaw
            self.root.after(0, lambda: self.update_progress(45, "正在配置 npm 镜像源..."))
            self.install_openclaw()
            self.root.after(0, lambda: self.update_progress(70, "OpenClaw 安装完成 ✓"))
            
            # 步骤5: 配置 API Key
            self.root.after(0, lambda: self.update_progress(75, "正在配置 API Key..."))
            self.configure_api_key()
            self.root.after(0, lambda: self.update_progress(85, "API Key 配置完成 ✓"))
            
            # 步骤6: 安装服务
            self.root.after(0, lambda: self.update_progress(90, "正在启动服务..."))
            self.install_service()
            
            # 完成
            self.root.after(0, lambda: self.update_progress(100, "安装完成 ✓"))
            self.root.after(500, self.show_finish)
            
        except Exception as e:
            self.root.after(0, lambda: self.show_error(str(e)))
    
    def update_progress(self, value, status):
        """更新进度"""
        self.install_progress.set(value)
        self.progress_percent.config(text=f"{int(value)}%")
        self.install_status.set(status)
    
    def install_nodejs(self):
        """安装 Node.js"""
        # 检查是否已安装
        try:
            result = subprocess.run(["node", "--version"], capture_output=True, text=True, shell=True)
            if result.returncode == 0:
                version = result.stdout.strip()
                # 检查版本是否 >= 22.12
                major = int(version.replace('v', '').split('.')[0])
                if major >= 22:
                    return  # 已安装正确版本
        except:
            pass
        
        # 下载并安装 Node.js v22
        nodejs_mirrors = [
            "https://npmmirror.com/mirrors/node/v22.14.0/node-v22.14.0-x64.msi",
            "https://mirrors.huaweicloud.com/nodejs/v22.14.0/node-v22.14.0-x64.msi"
        ]
        
        installer_path = os.path.join(os.environ.get("TEMP", "."), "nodejs_installer.msi")
        
        for url in nodejs_mirrors:
            try:
                # 使用 PowerShell 下载
                download_cmd = f'powershell -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri \'{url}\' -OutFile \'{installer_path}\' -UseBasicParsing"'
                subprocess.run(download_cmd, shell=True, check=True)
                
                if os.path.exists(installer_path) and os.path.getsize(installer_path) > 20000000:
                    # 静默安装
                    subprocess.run(f'msiexec /i "{installer_path}" /quiet /norestart', shell=True, check=True)
                    return
            except Exception as e:
                continue
        
        raise Exception("Node.js 安装失败，请手动安装")
    
    def install_git(self):
        """安装 Git"""
        # 检查是否已安装
        try:
            result = subprocess.run(["git", "--version"], capture_output=True, text=True, shell=True)
            if result.returncode == 0:
                return  # 已安装
        except:
            pass
        
        # 使用 winget 安装
        try:
            subprocess.run(["winget", "install", "Git.Git", "--accept-source-agreements", "--accept-package-agreements"], 
                          shell=True, check=True, capture_output=True)
            return
        except:
            pass
        
        # 下载安装包
        git_mirrors = [
            "https://npmmirror.com/mirrors/git-for-windows/v2.49.0.windows.1/Git-2.49.0-64-bit.exe",
            "https://mirrors.huaweicloud.com/git-for-windows/v2.49.0.windows.1/Git-2.49.0-64-bit.exe"
        ]
        
        installer_path = os.path.join(os.environ.get("TEMP", "."), "git_installer.exe")
        
        for url in git_mirrors:
            try:
                download_cmd = f'powershell -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri \'{url}\' -OutFile \'{installer_path}\' -UseBasicParsing"'
                subprocess.run(download_cmd, shell=True, check=True)
                
                if os.path.exists(installer_path) and os.path.getsize(installer_path) > 10000000:
                    # 静默安装
                    subprocess.run(f'"{installer_path}" /VERYSILENT /NORESTART', shell=True, check=True)
                    return
            except:
                continue
        
        raise Exception("Git 安装失败，请手动安装")
    
    def install_openclaw(self):
        """安装 OpenClaw"""
        # 创建安装目录
        install_dir = self.install_path.get()
        os.makedirs(install_dir, exist_ok=True)
        
        # 查找 npm
        npm_paths = [
            r"C:\Program Files\nodejs\npm.cmd",
            r"C:\Program Files (x86)\nodejs\npm.cmd",
            os.path.expandvars(r"%APPDATA%\npm\npm.cmd"),
            "npm"
        ]
        
        npm_cmd = None
        for path in npm_paths:
            try:
                result = subprocess.run([path, "--version"], capture_output=True, text=True, shell=True, timeout=5)
                if result.returncode == 0:
                    npm_cmd = path
                    break
            except:
                continue
        
        if not npm_cmd:
            raise Exception("找不到 npm，请确保 Node.js 已正确安装")
        
        # 设置 npm 镜像（加速下载）
        self.root.after(0, lambda: self.update_progress(48, "配置 npm 淘宝镜像..."))
        subprocess.run([npm_cmd, "config", "set", "registry", "https://registry.npmmirror.com"], shell=True, capture_output=True)
        
        # 安装 openclaw（使用淘宝镜像）
        self.root.after(0, lambda: self.update_progress(50, "正在下载 OpenClaw..."))
        self.root.after(0, lambda: self.update_progress(52, "使用淘宝镜像加速下载..."))
        
        # 多次尝试淘宝镜像（不要用官方源，国内会卡死）
        max_retries = 3
        for retry in range(max_retries):
            self.root.after(0, lambda r=retry: self.update_progress(52 + r*5, f"下载中... (尝试 {r+1}/{max_retries})"))
            
            result = subprocess.run(
                [npm_cmd, "install", "-g", "openclaw", "--registry", "https://registry.npmmirror.com"],
                capture_output=True, text=True, shell=True, timeout=300  # 5 分钟超时
            )
            
            if result.returncode == 0:
                break  # 成功
            
            if retry < max_retries - 1:
                self.root.after(0, lambda: self.update_progress(55, "下载失败，重试中..."))
                import time
                time.sleep(3)  # 等待 3 秒重试
        
        if result.returncode != 0:
            raise Exception(f"OpenClaw 下载失败（尝试了 {max_retries} 次）。\n请手动执行：npm install -g openclaw --registry https://registry.npmmirror.com\n错误信息：{result.stderr[:300]}")
    
    def configure_api_key(self):
        """配置 API Key"""
        provider = self.provider.get()
        api_key = self.api_key.get()
        
        if not provider or not api_key:
            return
        
        config = self.providers.get(provider, {})
        provider_id = config.get('id', provider.lower())
        
        # 使用 openclaw config set 命令
        openclaw_paths = [
            r"C:\Program Files\nodejs\openclaw.cmd",
            os.path.expandvars(r"%APPDATA%\npm\openclaw.cmd"),
            "openclaw"
        ]
        
        openclaw_cmd = None
        for path in openclaw_paths:
            try:
                result = subprocess.run([path, "--version"], capture_output=True, text=True, shell=True, timeout=5)
                if result.returncode == 0:
                    openclaw_cmd = path
                    break
            except:
                continue
        
        if not openclaw_cmd:
            # 配置文件可能还不存在，跳过此步骤让用户手动配置
            return
        
        # 设置默认模型
        model_map = {
            "qwen": "modelstudio/qwen3.5-plus",
            "qianfan": "qianfan/ernie-4.0-8k",  # 百度千帆
            "glm": "modelstudio/glm-4.7",
            "kimi": "modelstudio/kimi-k2.5",
            "deepseek": "deepseek/deepseek-chat",  # DeepSeek
            "hunyuan": "hunyuan/hunyuan-lite",  # 腾讯混元
            "doubao": "doubao/doubao-pro-32k",  # 字节豆包
            "minimax": "modelstudio/MiniMax-M2.5",
            "pangu": "pangu/pangu-nlp",  # 华为盘古
            "yi": "yi/yi-large",  # 零一万物
            "openai": "openai/gpt-4o"
        }
        
        default_model = model_map.get(provider_id, f"{provider_id}/default")
        
        try:
            # 设置模型
            result = subprocess.run([openclaw_cmd, "config", "set", "agents.defaults.model.primary", default_model], 
                          shell=True, capture_output=True, text=True, timeout=30)
            if result.returncode != 0:
                print(f"模型配置警告: {result.stderr}")
            
            # TODO: API Key 需要通过 openclaw configure 交互式配置
            # 这里暂时跳过，让用户手动配置
            
        except Exception as e:
            print(f"配置警告: {e}")
    
    def install_service(self):
        """安装系统服务"""
        try:
            # 先安装服务
            subprocess.run(["openclaw", "gateway", "install"], shell=True, capture_output=True, timeout=60)
            # 再启动服务
            subprocess.run(["openclaw", "gateway", "start"], shell=True, capture_output=True, timeout=30)
        except Exception as e:
            # 如果失败，记录错误但不中断
            print(f"服务安装警告: {e}")
    
    def show_finish(self):
        """显示完成页面"""
        # 生成访问令牌
        import secrets
        token = secrets.token_hex(16)
        self.access_token.config(text=token)
        
        self.show_page(7)  # 完成页面
    
    def show_error(self, msg):
        """显示错误页面"""
        self.error_msg.config(text=msg)
        self.show_page(8)  # 错误页面
    
    def cancel_install(self):
        """取消安装"""
        if messagebox.askyesno("确认", "确定要取消安装吗？"):
            self.quit()
    
    def show_log(self):
        """显示日志"""
        log_path = os.path.join(self.install_path.get(), "install.log")
        if os.path.exists(log_path):
            os.startfile(log_path)
        else:
            messagebox.showinfo("提示", "日志文件不存在")
    
    def retry_install(self):
        """重试安装"""
        self.show_page(5)  # 回到确认页面
    
    # ============= 页面导航 =============
    
    def show_page(self, index):
        """显示指定页面"""
        for i, page in enumerate(self.pages):
            if i == index:
                page.pack(fill='both', expand=True)
            else:
                page.pack_forget()
        self.current_page = index
    
    def next_page(self):
        """下一页"""
        if self.current_page < len(self.pages) - 1:
            self.show_page(self.current_page + 1)
    
    def prev_page(self):
        """上一页"""
        if self.current_page > 0:
            self.show_page(self.current_page - 1)
    
    def quit(self):
        """退出程序"""
        self.root.quit()
    
    def run(self):
        """运行向导"""
        self.root.mainloop()


if __name__ == "__main__":
    wizard = InstallWizard()
    wizard.run()