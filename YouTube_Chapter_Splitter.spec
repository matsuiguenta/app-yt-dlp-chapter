# -*- mode: python ; coding: utf-8 -*-
import os
import customtkinter

ctk_path = os.path.dirname(customtkinter.__file__)

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[
        ('bin/yt-dlp.exe', 'bin'),
        ('bin/ffmpeg.exe', 'bin')
    ],
    datas=[
        (ctk_path, 'customtkinter')
    ],
    hiddenimports=['customtkinter', 'yt_dlp'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='YouTube_Chapter_Splitter',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
