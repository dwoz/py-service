# -*- mode: python -*-
import os
root_path = os.path.dirname(os.path.realpath(__file__))
script_path = os.path.join(root_path, 'bin')
print(root_path)
print(script_path)
a = Analysis(['.\simple-service.py'],
	     #pathex=[root_path],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='simple-service.exe',
          debug=False,
          strip=None,
          upx=True,
          console=True)
