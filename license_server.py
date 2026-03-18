#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
激活码验证服务器
在线验证 + 设备绑定 + 使用统计
"""

from flask import Flask, request, jsonify
import sqlite3
import secrets
import hashlib
from datetime import datetime, timedelta
import json
import os

app = Flask(__name__)
DB_PATH = "licenses.db"

# ============= 配置 =============
SECRET_KEY = secrets.token_hex(32)  # 生成后请保存好
MAX_DEVICES_PER_KEY = 1  # 一个激活码可用几台设备
# =================================


def init_db():
    """初始化数据库"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # 激活码表
    c.execute('''
        CREATE TABLE IF NOT EXISTS licenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT UNIQUE NOT NULL,
            status TEXT DEFAULT 'active',  -- active, used, revoked, expired
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP,
            max_devices INTEGER DEFAULT 1,
            order_id TEXT,
            buyer_info TEXT,
            notes TEXT
        )
    ''')
    
    # 设备绑定表
    c.execute('''
        CREATE TABLE IF NOT EXISTS devices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            license_key TEXT NOT NULL,
            machine_id TEXT NOT NULL,
            first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            system_info TEXT,
            FOREIGN KEY (license_key) REFERENCES licenses(key)
        )
    ''')
    
    # 部署记录表
    c.execute('''
        CREATE TABLE IF NOT EXISTS deployments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            license_key TEXT NOT NULL,
            machine_id TEXT NOT NULL,
            status TEXT,
            system_info TEXT,
            deployed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (license_key) REFERENCES licenses(key)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ 数据库初始化完成")


def generate_license_key():
    """生成激活码"""
    # 格式：OPENCLAW-XXXX-XXXX-XXXX
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


@app.route('/api/verify', methods=['POST'])
def verify_license():
    """验证激活码"""
    data = request.json
    key = data.get('key', '')
    machine_id = data.get('machine_id', '')
    version = data.get('version', '1.0.0')
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # 查询激活码
    c.execute('SELECT * FROM licenses WHERE key = ?', (key,))
    license_row = c.fetchone()
    
    if not license_row:
        conn.close()
        return jsonify({
            "valid": False,
            "error": "激活码不存在"
        })
    
    # 检查状态 (license_row[2] is status)
    status = license_row[2]
    if status != 'active':
        conn.close()
        return jsonify({
            "valid": False,
            "error": f"激活码已{status}"
        })
    
    # 检查过期 (license_row[4] is expires_at)
    try:
        expires_str = license_row[4].split('.')[0]  # Remove microseconds
        expires_at = datetime.fromisoformat(expires_str)
        if datetime.now() > expires_at:
            c.execute('UPDATE licenses SET status = ? WHERE key = ?', ('expired', key))
            conn.commit()
            conn.close()
            return jsonify({
                "valid": False,
                "error": "激活码已过期"
            })
    except Exception as e:
        pass  # Date parse error, continue
    
    # 检查设备绑定
    c.execute('SELECT * FROM devices WHERE license_key = ? AND machine_id = ?', (key, machine_id))
    device_row = c.fetchone()
    
    if not device_row:
        # 新设备，检查是否超出限制
        c.execute('SELECT COUNT(*) FROM devices WHERE license_key = ?', (key,))
        device_count = c.fetchone()[0]
        max_devices = license_row[7]
        
        max_devices = license_row[5] or 1  # Default to 1 if None
        if device_count >= max_devices:
            conn.close()
            return jsonify({
                "valid": False,
                "error": "激活码已达设备上限"
            })
        
        # 绑定新设备
        system_info = json.dumps(data.get('system_info', {}))
        c.execute('''
            INSERT INTO devices (license_key, machine_id, system_info)
            VALUES (?, ?, ?)
        ''', (key, machine_id, system_info))
        conn.commit()
    
    # 更新最后活跃时间
    c.execute('UPDATE devices SET last_seen = ? WHERE license_key = ? AND machine_id = ?',
              (datetime.now().isoformat(), key, machine_id))
    conn.commit()
    conn.close()
    
    return jsonify({
        "valid": True,
        "message": "验证成功，开始部署",
        "expires_at": expires_at.isoformat()
    })


@app.route('/api/report', methods=['POST'])
def report_deployment():
    """上报部署结果"""
    data = request.json
    key = data.get('key', '')
    machine_id = data.get('machine_id', '')
    status = data.get('status', 'unknown')
    system_info = json.dumps(data.get('system_info', {}))
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''
        INSERT INTO deployments (license_key, machine_id, status, system_info)
        VALUES (?, ?, ?, ?)
    ''', (key, machine_id, status, system_info))
    
    conn.commit()
    conn.close()
    
    return jsonify({"status": "ok"})


@app.route('/api/generate', methods=['POST'])
def api_generate_license():
    """API 生成激活码（供你调用）"""
    # 可以加认证
    data = request.json
    order_id = data.get('order_id')
    buyer_info = data.get('buyer_info')
    expires_days = data.get('expires_days', 365)
    
    key = create_license(order_id, buyer_info, expires_days)
    
    return jsonify({
        "key": key,
        "expires_days": expires_days
    })


@app.route('/api/list', methods=['GET'])
def list_licenses():
    """查看所有激活码"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''
        SELECT l.key, l.status, l.created_at, l.expires_at, l.order_id, l.buyer_info,
               COUNT(d.id) as device_count
        FROM licenses l
        LEFT JOIN devices d ON l.key = d.license_key
        GROUP BY l.key
        ORDER BY l.created_at DESC
    ''')
    
    rows = c.fetchall()
    conn.close()
    
    licenses = []
    for row in rows:
        licenses.append({
            "key": row[0],
            "status": row[1],
            "created_at": row[2],
            "expires_at": row[3],
            "order_id": row[4],
            "buyer_info": row[5],
            "device_count": row[6]
        })
    
    return jsonify(licenses)


@app.route('/api/revoke/<key>', methods=['POST'])
def revoke_license(key):
    """吊销激活码"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('UPDATE licenses SET status = ? WHERE key = ?', ('revoked', key))
    conn.commit()
    conn.close()
    
    return jsonify({"status": "ok", "message": "激活码已吊销"})


if __name__ == "__main__":
    init_db()
    print("\n🚀 启动验证服务器...")
    print("📋 API 端点：")
    print("   POST /api/verify    - 验证激活码")
    print("   POST /api/report    - 上报部署结果")
    print("   POST /api/generate  - 生成激活码")
    print("   GET  /api/list      - 查看激活码列表")
    print("   POST /api/revoke/:key - 吊销激活码")
    print("\n⚠️  按 Ctrl+C 停止服务")
    
    app.run(host='0.0.0.0', port=5000, debug=False)
