# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py', 'pyFile/get_jion_path.py','pyFile/kuwo_music.py','pyFile/sql_song.py','pyFile/sqlite_lib.py','pyFile/Ui_Window.py'],
    pathex=["/Users/v_linyanjun/Documents/MyMusic"],
    binaries=[('sqlConfig/songs.db','sqlConfig')],
    datas=[('images/*.png', 'images'), ('images/*.icns', 'images')],
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
    name='Music Player',
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
    icon=['/Users/v_linyanjun/Documents/MyMusic/images/ImageReady.icns'],
)
app = BUNDLE(
    exe,
    name='Music Player.app',
    icon='/Users/v_linyanjun/Documents/MyMusic/images/ImageReady.icns',
    bundle_identifier=None,
)
