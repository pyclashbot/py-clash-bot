# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['run_bot.py'],
    pathex=[],
    binaries=[],
    datas=[('pyclashbot/detection/reference_images', 'pyclashbot/detection/reference_images'), ('platform-tools', 'platform-tools'), ('pyclashbot/interface/assets', 'pyclashbot/interface/assets'), ('assets', 'assets')],
    hiddenimports=['pyclashbot', 'pyclashbot.__main__'],
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
    [],
    exclude_binaries=True,
    name='ClashBot',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['clashbot.icns'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='ClashBot',
)
app = BUNDLE(
    coll,
    name='ClashBot.app',
    icon='clashbot.icns',
    bundle_identifier=None,
)
