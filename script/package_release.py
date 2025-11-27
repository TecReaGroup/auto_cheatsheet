"""Package Auto Cheatsheet for distribution"""
import shutil
import zipfile
from pathlib import Path
from datetime import datetime

def create_package():
    """Create distribution package with exe, log, and src folders"""
    print("="*60)
    print("Creating Auto Cheatsheet distribution package...")
    print("="*60)
    
    # Check if exe exists
    exe_path = Path("build/app.exe")
    if not exe_path.exists():
        print("Error: app.exe not found in build/ directory")
        print("Please run the build script first: python script/build_nuitka.py")
        return False
    
    # Create dist directory
    dist_dir = Path("dist")
    dist_dir.mkdir(exist_ok=True)
    
    # Create package directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    package_name = f"AutoCheatsheet_{timestamp}"
    package_dir = dist_dir / package_name
    
    # Clean up if exists
    if package_dir.exists():
        shutil.rmtree(package_dir)
    package_dir.mkdir()
    
    print("\n[1/4] Copying executable...")
    shutil.copy2(exe_path, package_dir / "AutoCheatsheet.exe")
    print("  ✓ Copied: AutoCheatsheet.exe")
    
    print("\n[2/4] Creating empty log directory...")
    log_dir = package_dir / "log"
    log_dir.mkdir()
    print("  ✓ Created: log/ (empty)")
    
    print("\n[3/4] Creating empty src directory...")
    src_dir = package_dir / "src"
    src_dir.mkdir()
    print("  ✓ Created: src/ (empty)")
    
    print("\n[4/4] Creating zip archive...")
    zip_path = dist_dir / f"{package_name}.zip"
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add all files and directories (including empty ones)
        for item in package_dir.rglob('*'):
            arcname = item.relative_to(package_dir.parent)
            if item.is_file():
                zipf.write(item, arcname)
            elif item.is_dir():
                # Add directory entry with trailing slash
                zipf.write(item, str(arcname) + '/')
    
    # Get file size
    size_mb = zip_path.stat().st_size / (1024 * 1024)
    
    print("\n" + "="*60)
    print("✓ Package created successfully!")
    print("="*60)
    print(f"Package: {zip_path}")
    print(f"Size: {size_mb:.1f} MB")
    print("\nContents:")
    print("  - AutoCheatsheet.exe")
    print("  - log/ (empty directory for runtime logs)")
    print("  - src/ (empty directory for cheatsheet data)")
    print("="*60)
    
    # Clean up temporary directory
    shutil.rmtree(package_dir)
    
    return True

if __name__ == "__main__":
    create_package()