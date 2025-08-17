#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build Script for Make ID Photo Generator
Creates a single executable file with all dependencies
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def install_pyinstaller():
    """Install PyInstaller if not already installed"""
    try:
        import PyInstaller
        print("✓ PyInstaller already installed")
        return True
    except ImportError:
        print("Installing PyInstaller...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            print("✓ PyInstaller installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("✗ Failed to install PyInstaller")
            return False

def create_spec_file():
    """Create PyInstaller spec file for the project"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Add data files - these will be available at runtime
added_files = [
    ('dnn_models', 'dnn_models'),
    ('id_template', 'id_template'),
    ('font.otf', '.'),
    ('config.json', '.'),
]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=added_files,
    hiddenimports=[
        'cv2',
        'numpy',
        'PIL',
        'PIL.Image',
        'PIL.ImageDraw', 
        'PIL.ImageFont',
        'pypinyin',
        'pypinyin.core',
        'pypinyin.style',
        'pathlib',
        'json',
        'argparse',
        're',
        'shutil',
        'os',
        'sys',
        'traceback'
    ],
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
    name='MakeID',
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
    icon=None
)
'''
    
    with open('MakeID.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("✓ Created MakeID.spec file")

def build_executable():
    """Build the executable using PyInstaller"""
    print("Building executable...")
    try:
        # Use the spec file to build
        subprocess.check_call(['pyinstaller', 'MakeID.spec', '--clean'])
        print("✓ Executable built successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Build failed: {e}")
        return False

def copy_output_files():
    """Copy the built executable and config files to output directory"""
    output_dir = Path("dist")
    if not output_dir.exists():
        print("✗ Output directory not found")
        return False
    
    # Create final output directory
    final_dir = Path("MakeID_Executable")
    if final_dir.exists():
        shutil.rmtree(final_dir)
    final_dir.mkdir()
    
    # Copy executable
    exe_file = output_dir / "MakeID.exe"
    if exe_file.exists():
        shutil.copy2(exe_file, final_dir)
        print("✓ Copied MakeID.exe")
    else:
        print("✗ Executable not found")
        return False
    
    # Copy config file
    if Path("config.json").exists():
        shutil.copy2("config.json", final_dir)
        print("✓ Copied config.json")
    
    # Copy README
    if Path("README.md").exists():
        shutil.copy2("README.md", final_dir)
        print("✓ Copied README.md")
    
    # Create a simple batch file for easy execution
    batch_content = '''@echo off
echo Starting Make ID Photo Generator...
echo.
MakeID.exe
echo.
echo Press any key to exit...
pause >nul
'''
    
    with open(final_dir / "Run_MakeID.bat", 'w', encoding='utf-8') as f:
        f.write(batch_content)
    print("✓ Created Run_MakeID.bat")
    
    print(f"\n✓ All files copied to: {final_dir}")
    return True

def cleanup():
    """Clean up build artifacts"""
    print("Cleaning up build artifacts...")
    
    # Remove build directories
    for dir_name in ['build', '__pycache__']:
        if Path(dir_name).exists():
            shutil.rmtree(dir_name)
            print(f"✓ Removed {dir_name}")
    
    # Remove spec file
    if Path("MakeID.spec").exists():
        Path("MakeID.spec").unlink()
        print("✓ Removed MakeID.spec")
    
    # Keep dist directory for now (contains the exe)

def main():
    """Main build process"""
    print("=" * 60)
    print("MAKE ID PHOTO GENERATOR - EXECUTABLE BUILDER")
    print("=" * 60)
    
    # Check if we're in the right directory
    required_files = ['main.py', 'crop_photo.py', 'make_id.py', 'py_to_en.py', 'config.json']
    missing_files = [f for f in required_files if not Path(f).exists()]
    
    if missing_files:
        print(f"✗ Missing required files: {missing_files}")
        print("Please run this script from the project root directory")
        return False
    
    # Install PyInstaller
    if not install_pyinstaller():
        return False
    
    # Create spec file
    create_spec_file()
    
    # Build executable
    if not build_executable():
        return False
    
    # Copy output files
    if not copy_output_files():
        return False
    
    # Cleanup
    cleanup()
    
    print("\n" + "=" * 60)
    print("✓ BUILD COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print(f"Your executable is ready in: MakeID_Executable/")
    print("Files included:")
    print("  - MakeID.exe (main executable)")
    print("  - config.json (configuration)")
    print("  - README.md (documentation)")
    print("  - Run_MakeID.bat (easy launcher)")
    print("\nYou can now distribute these files to any Windows machine!")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n✗ Build failed!")
        sys.exit(1) 