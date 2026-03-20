# -*- mode: python ; coding: utf-8 -*-
# OpenClaw 部署工具 - PyInstaller 配置
# 混合方案：预打包 OpenClaw 核心

a = Analysis(
    ['installer.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('openclaw_logo.png', '.'),
        ('openclaw_logo.ico', '.'),
        ('bundle', 'bundle'),  # 预打包的 OpenClaw
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='OpenClaw-Installer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='openclaw_logo.ico',
)