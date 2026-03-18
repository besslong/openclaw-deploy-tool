#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
激活码生成工具
直接运行生成激活码，或调用 API
"""

import sqlite3
import secrets
from datetime import datetime, timedelta
import sys
import json

DB_PATH = "licenses.db"


def generate_license_key():
    """生成激活码"""
    prefix = "OPENCLAW"
    parts = [secrets.token_hex(4).upper() for _ in range(3)]
    return f"{prefix}-{'-'.join(parts)}"


def create_license(order_id=None, buyer_info=None, expires_days=365, max_devices=1):
    """创建新激活码"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    key = generate_license_key()
    expires_at = datetime.now() + timedelta(days=expires_days)
    
    c.execute('''
        INSERT INTO licenses (key, status, expires_at, order_id, buyer_info, max_devices)
        VALUES (?, 'active', ?, ?, ?, ?)
    ''', (key, expires_at, order_id, buyer_info, max_devices))
    
    conn.commit()
    conn.close()
    
    return key


def batch_generate(count=1, expires_days=365):
    """批量生成激活码"""
    print(f"\n🔑 正在生成 {count} 个激活码...\n")
    
    licenses = []
    for i in range(count):
        key = create_license(expires_days=expires_days)
        licenses.append(key)
        print(f"  [{i+1}/{count}] {key}")
    
    print(f"\n✅ 生成完成！共 {count} 个激活码")
    print(f"📅 有效期：{expires_days} 天")
    
    # 保存到文件
    filename = f"licenses_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("# OpenClaw 激活码\n")
        f.write(f"# 生成时间：{datetime.now().isoformat()}\n")
        f.write(f"# 有效期：{expires_days} 天\n")
        f.write("#" + "="*50 + "\n\n")
        for key in licenses:
            f.write(f"{key}\n")
    
    print(f"\n💾 已保存到：{filename}")
    
    return licenses


def main():
    """主函数"""
    print("="*60)
    print("🔑 OpenClaw 激活码生成工具")
    print("="*60)
    
    # 初始化数据库
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS licenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT UNIQUE NOT NULL,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP,
            max_devices INTEGER DEFAULT 1,
            order_id TEXT,
            buyer_info TEXT,
            notes TEXT
        )
    ''')
    conn.commit()
    conn.close()
    
    # 命令行参数
    if len(sys.argv) > 1:
        if sys.argv[1] == "batch":
            count = int(sys.argv[2]) if len(sys.argv) > 2 else 10
            expires = int(sys.argv[3]) if len(sys.argv) > 3 else 365
            batch_generate(count, expires)
            return
        elif sys.argv[1] == "single":
            order_id = sys.argv[2] if len(sys.argv) > 2 else None
            buyer = sys.argv[3] if len(sys.argv) > 3 else None
            expires = int(sys.argv[4]) if len(sys.argv) > 4 else 365
            
            key = create_license(order_id, buyer, expires)
            print(f"\n✅ 激活码生成成功：")
            print(f"   {key}")
            print(f"   有效期：{expires} 天")
            return
    
    # 交互模式
    print("\n请选择操作：")
    print("  1. 生成单个激活码")
    print("  2. 批量生成激活码")
    print("  3. 退出")
    
    choice = input("\n请输入选项 (1/2/3): ").strip()
    
    if choice == "1":
        order_id = input("订单号（可选）: ").strip()
        buyer = input("买家信息（可选）: ").strip()
        expires = input("有效期天数（默认 365）: ").strip()
        expires = int(expires) if expires else 365
        
        key = create_license(order_id or None, buyer or None, expires)
        print(f"\n✅ 激活码生成成功：")
        print(f"   {key}")
        print(f"   有效期：{expires} 天")
        
    elif choice == "2":
        count = input("生成数量（默认 10）: ").strip()
        count = int(count) if count else 10
        
        expires = input("有效期天数（默认 365）: ").strip()
        expires = int(expires) if expires else 365
        
        batch_generate(count, expires)
    
    elif choice == "3":
        print("\n👋 再见！")
        return
    
    else:
        print("\n❌ 无效选项")


if __name__ == "__main__":
    main()
