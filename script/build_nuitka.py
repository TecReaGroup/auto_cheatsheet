"""Nuitka build script for Auto Cheatsheet"""
import subprocess
import sys
import shutil
from pathlib import Path

def check_nuitka():
    """Check if Nuitka is installed"""
    try:
        import nuitka  # noqa: F401
        return True
    except ImportError:
        print("[ERROR] Nuitka is not installed!")
        print("Install with: pip install nuitka ordered-set zstandard")
        return False

def convert_icon():
    """Convert PNG icon to ICO format"""
    print("[1/4] Converting icon...")
    
    icon_png = Path("asset/icon/icon.png")
    icon_ico = Path("asset/icon/icon.ico")
    
    if not icon_png.exists():
        print(f"[WARNING] Icon not found: {icon_png}")
        return False
    
    try:
        from PIL import Image
        img = Image.open(icon_png)
        # Create multiple sizes for ICO (16, 32, 48, 256)
        img.save(icon_ico, format='ICO', sizes=[(16,16), (32,32), (48,48), (256,256)])
        print(f"[✓] Icon converted: {icon_ico}")
        return True
    except ImportError:
        print("[WARNING] Pillow not installed, trying alternative method...")
        try:
            # Try using imagemagick if available
            result = subprocess.run(
                ["magick", "convert", str(icon_png), "-define", "icon:auto-resize=256,128,64,48,32,16", str(icon_ico)],
                capture_output=True
            )
            if result.returncode == 0:
                print(f"[✓] Icon converted: {icon_ico}")
                return True
        except FileNotFoundError:
            pass
        
        print("[WARNING] Could not convert icon. Install Pillow: pip install Pillow")
        print("Or install ImageMagick: https://imagemagick.org/")
        return False

def clean_build():
    """Remove old build directories"""
    print("[2/4] Cleaning old builds...")
    dirs_to_clean = ["build", "app.dist", "app.build", "app.onefile-build"]
    
    for d in dirs_to_clean:
        if Path(d).exists():
            print(f"  Removing {d}...")
            shutil.rmtree(d, ignore_errors=True)
    
    # Remove old executable
    if Path("app.exe").exists():
        Path("app.exe").unlink()
    
    print("[✓] Cleanup complete")

def ensure_data_dirs():
    """Ensure required data directories exist"""
    print("[2.5/4] Ensuring data directories exist...")
    
    data_dirs = [
        Path("src/svg"),
        Path("src/doc"),
        Path("asset")
    ]
    
    for dir_path in data_dirs:
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"  Created: {dir_path}/")
        else:
            print(f"  Exists: {dir_path}/")
    
    print("[✓] Data directories ready")

def build():
    """Run Nuitka build with maximum optimization"""
    print("[3/4] Building with Nuitka (optimized for size)...")
    print("This may take 10-30 minutes depending on your system...")
    
    cmd = [
        sys.executable, "-m", "nuitka",
        # Standalone executable
        "--standalone",
        "--onefile",  # Single file for easier distribution
        
        # Windows specific
        "--windows-disable-console",  # No console window
        "--windows-icon-from-ico=asset/icon/icon.png",
        
        # PySide6 plugin
        "--enable-plugin=pyside6",
        
        # Include data directories (only if they exist and have content)
        
        # Include required modules
        "--include-module=yaml",
        "--include-module=resvg_py",
        "--include-module=qtawesome",
        "--include-module=requests",
        "--include-package=ui",
        "--include-package=core",
        "--include-package=script",
        
        # SPEED OPTIMIZATION FLAGS (LTO disabled for faster build)
        "--lto=no",  # Disable LTO - saves 15-20 minutes, only adds ~5-10% size
        "--assume-yes-for-downloads",  # Auto-download dependencies
        "--show-progress",  # Show build progress
        
        # Exclude unused Qt modules to reduce size
        "--nofollow-import-to=PySide6.QtWebEngineCore",
        "--nofollow-import-to=PySide6.QtWebEngineWidgets",
        "--nofollow-import-to=PySide6.QtWebChannel",
        "--nofollow-import-to=PySide6.QtPdf",
        "--nofollow-import-to=PySide6.QtPdfWidgets",
        "--nofollow-import-to=PySide6.QtQuick",
        "--nofollow-import-to=PySide6.QtQuickWidgets",
        "--nofollow-import-to=PySide6.QtQml",
        "--nofollow-import-to=PySide6.Qt3DCore",
        "--nofollow-import-to=PySide6.Qt3DRender",
        "--nofollow-import-to=PySide6.QtCharts",
        "--nofollow-import-to=PySide6.QtDataVisualization",
        "--nofollow-import-to=PySide6.QtDesigner",
        "--nofollow-import-to=PySide6.QtMultimedia",
        "--nofollow-import-to=PySide6.QtMultimediaWidgets",
        "--nofollow-import-to=PySide6.QtNetwork",
        "--nofollow-import-to=PySide6.QtNetworkAuth",
        "--nofollow-import-to=PySide6.QtPositioning",
        "--nofollow-import-to=PySide6.QtPrintSupport",
        "--nofollow-import-to=PySide6.QtSensors",
        "--nofollow-import-to=PySide6.QtSerialPort",
        "--nofollow-import-to=PySide6.QtSql",
        "--nofollow-import-to=PySide6.QtTest",
        "--nofollow-import-to=PySide6.QtWebSockets",
        
        # Exclude optional runtime modules
        "--nofollow-import-to=playwright",
        "--nofollow-import-to=patchright",
        "--nofollow-import-to=matplotlib",
        "--nofollow-import-to=IPython",
        "--nofollow-import-to=jupyter",
        "--nofollow-import-to=tkinter",
        "--nofollow-import-to=pytest",
        "--nofollow-import-to=unittest",
        
        # Output configuration
        "--output-dir=build",
        "--output-filename=AutoCheatsheet.exe",
        
        # Target file
        "app.py"
    ]
    
    # Add data directories only if they exist
    if Path("src/svg").exists():
        cmd.insert(-1, "--include-data-dir=src/svg=src/svg")
    if Path("src/doc").exists():
        cmd.insert(-1, "--include-data-dir=src/doc=src/doc")
    if Path("asset").exists():
        cmd.insert(-1, "--include-data-dir=asset=asset")
    
    # Remove icon parameter if icon doesn't exist
    if not Path("icon.ico").exists() and not Path("asset/icon/icon.png").exists():
        cmd = [c for c in cmd if not c.startswith("--windows-icon-from-ico")]
    
    print("\n" + "="*60)
    
    # Run with progress output
    result = subprocess.run(cmd)
    
    return result.returncode == 0

def organize_output():
    """Show build results"""
    print("\n[4/4] Checking build output...")
    
    # Check for onefile output
    exe_path = Path("build/AutoCheatsheet.exe")
    
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print("\n" + "="*60)
        print("✓ Build completed successfully!")
        print("="*60)
        print(f"Executable: {exe_path}")
        print(f"Size: {size_mb:.1f} MB")
        print("="*60)
        print("\nTo run the application:")
        print(f"  {exe_path}")
        print("\nNote: First run may be slower as it extracts resources.")
        return True
    else:
        print("\n[ERROR] Build output not found!")
        print("Expected location: build/AutoCheatsheet.exe")
        
        # Check alternative locations
        alt_paths = [
            Path("AutoCheatsheet.exe"),
            Path("app.exe"),
            Path("build/app.exe")
        ]
        
        for path in alt_paths:
            if path.exists():
                print(f"\nFound executable at alternative location: {path}")
                return True
        
        return False

def main():
    print("="*60)
    print("Building Auto Cheatsheet with Nuitka")
    print("Size-optimized configuration")
    print("="*60 + "\n")
    
    # Check prerequisites
    if not check_nuitka():
        print("\nPlease install Nuitka first:")
        print("  pip install nuitka ordered-set zstandard")
        return 1
    
    # Convert icon (optional, won't fail if unsuccessful)
    convert_icon()
    
    # Clean old builds
    clean_build()
    
    # Ensure data directories exist
    ensure_data_dirs()
    
    # Build
    if not build():
        print("\n[ERROR] Build failed!")
        print("\nTroubleshooting:")
        print("1. Ensure you have a C compiler installed (Visual Studio Build Tools or MinGW)")
        print("2. If using Windows Store Python, install Python from python.org instead")
        print("3. Check that all requirements are installed: pip install -r requirements.txt")
        return 1
    
    # Check output
    if not organize_output():
        return 1
    
    print("\n✓ Build process complete!")
    return 0

if __name__ == "__main__":
    sys.exit(main())