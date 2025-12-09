# build.spec

a = Analysis(
    ['main_for_api.py'],
    pathex=[],
    binaries=[],
    datas=[
    ('.env', '.'),
    ('app_creation/vb-audio/*', 'app_creation/vb-audio/'),
    ('app_creation/Set-Audio-Devices.ps1', '.')
        ],

    hiddenimports=[
        'PyQt5.sip',
        'sounddevice'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[ 'torch',
        'tensorflow',
        'keras',
        'scipy',
        'sklearn',
        'pandas',
        'numpy',
        'matplotlib',
        'cv2',
        'sentence_transformers',
        'transformers',
        'torchvision',
        'torchaudio',
        'langchain_community.llms.huggingface_hub',
        'langchain_community.llms.huggingface_textgen_inference',
        'langchain_community.chat_models.azure_openai',
        'langchain_community.embeddings',
        'langchain_community.tools',
        'langchain_community.vectorstores',],  # exclude known heavy libs,
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Whisper AI',
    logo="logo.ico",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    # This is the key change: set to False for a GUI application
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Whisper AI',
)

