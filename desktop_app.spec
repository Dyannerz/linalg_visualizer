# desktop_app.spec

import os
import manim  # ✅ Required to get path to package

block_cipher = None

# Get full path to manim package
manim_path = os.path.dirname(manim.__file__)

a = Analysis(
    ['desktop_app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('templates', 'templates'),
        ('static', 'static'),
        ('ffmpeg', 'ffmpeg'),
        ('latex', 'latex'),
        ('change_of_basis.py', '.'),     # Required for Manim
        ('transformation.py', '.'),      # Required for Manim
        ('app.ico', '.'),                # Used as icon
        (manim_path, 'manim'),           # ✅ Force include entire manim package
    ],
    hiddenimports=[
        'requests',
        'manim',
        'manim.animation.transform',
        'manim.mobject.geometry',
        'manim.mobject.vector_field',
        'manim.mobject.coordinate_systems',
        'manim.scene.scene',
        'manim.scene.vector_space_scene',
        'manim.scene.graph_scene',
        'manim.utils.color',
        'manim.utils.space_ops',
        'manim.renderer.cairo_renderer',
        "scipy.special._ufuncs",
        "scipy.special._ufuncs_cxx",
        "scipy.special._cdflib",     
        "scipy.special._ellip_harm_2",
        "scipy.special._eval_cheby",
        "encodings", 
        "codecs",
        "scipy.special._testutils",
        "manimpango",
        "manimpango.utils",     # <== 🛠️ This is the missing piece
        "manimpango.cmanimpango",  # Include Cython extension
    
        # ✅ Matplotlib internals (fonts, plots)
        "matplotlib.backends.backend_agg",
        "matplotlib.backends.backend_tkagg",
        "matplotlib.pyplot",

        # ✅ Cairo, OpenGL
        "cairo",
        "pyopengl",
        "pyopengl_accelerate",

        # ✅ FFMPEG utils
        "imageio_ffmpeg",

        # ✅ Font tools and packaging
        "pkg_resources",
        "importlib_metadata",
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    name='LinearAlgebraApp',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Set to False if you want to hide the terminal window
    icon='app.ico'
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    name='LinearAlgebraApp'
)
