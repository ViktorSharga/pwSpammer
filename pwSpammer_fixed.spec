# -*- mode: python ; coding: utf-8 -*-

import sys
from PyInstaller.utils.hooks import collect_all, collect_submodules

# Collect all data files and hidden imports for Windows APIs
hiddenimports = [
    # Windows API modules
    'win32gui',
    'win32api', 
    'win32con',
    'win32process',
    
    # Process utilities
    'psutil',
    'psutil._psutil_windows',
    'psutil._pswindows',
    
    # System modules
    'ctypes',
    'ctypes.wintypes',
    '_ctypes',
    
    # GUI modules  
    'tkinter.ttk',
    'tkinter.messagebox',
    'tkinter.filedialog',
    
    # File system
    'pathlib',
    
    # Standard library modules
    'json',
    'threading',
    'platform',
    'traceback',
    'logging.handlers',
]

# Add psutil submodules
hiddenimports.extend(collect_submodules('psutil'))

# Collect binary files
binaries = []
datas = [
    ('pwSpammer.manifest', '.'),  # Include manifest file
]

# Add Windows system DLLs if needed
if sys.platform == 'win32':
    # Note: System DLLs are usually available, but we can add them if needed
    # binaries.extend([
    #     ('C:/Windows/System32/user32.dll', '.'),
    #     ('C:/Windows/System32/kernel32.dll', '.'),
    # ])
    pass

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=['hook-runtime-win32.py'],
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
    name='pwSpammer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # Disable UPX compression to avoid DLL issues
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Enable console for debugging
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
    uac_admin=True,  # Request admin privileges
    uac_uiaccess=False,
    manifest='pwSpammer.manifest',  # Add Windows manifest
)