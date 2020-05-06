# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['Main_Application.py'],
             pathex=['E:\\DigLab\\PyCharm_Projects\\v0.2\\volume_calculator_tool_v0.2\\src'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=['hook.py'],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='Main_Application',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True , icon='img\\icon_3V8_icon.ico')
