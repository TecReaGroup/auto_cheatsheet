"""Convert SVG to PNG using persistent Playwright browser"""
from pathlib import Path
import time
import re
from urllib.request import urlretrieve


class BrowserDaemon:
    """Persistent Playwright browser instance"""
    _instance = None
    _playwright = None
    _browser = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def __init__(self):
        try:
            from playwright.sync_api import sync_playwright
            self._playwright = sync_playwright().start()
            self._browser = self._playwright.chromium.launch()
            print("✓ Browser daemon started")
        except ImportError:
            raise ImportError("playwright not installed. Install it with: pip install playwright && playwright install chromium")
    
    def get_page(self, width, height):
        return self._browser.new_page(viewport={'width': width, 'height': height})
    
    def close(self):
        if self._browser:
            self._browser.close()
        if self._playwright:
            self._playwright.stop()
        print("✓ Browser daemon stopped")


def download_fonts(svg_content, font_dir="./asset/font"):
    """Download fonts from SVG if not available locally"""
    font_path = Path(font_dir)
    font_path.mkdir(parents=True, exist_ok=True)
    
    font_urls = re.findall(r'url\("(https://[^"]+\.woff2?)"\)', svg_content)
    
    for url in font_urls:
        font_name = url.split('/')[-1]
        local_path = font_path / font_name
        
        if not local_path.exists():
            try:
                print(f"Downloading font: {font_name}")
                urlretrieve(url, local_path)
                print(f"✓ Font saved to {local_path}")
            except Exception as e:
                print(f"Warning: Failed to download {font_name}: {e}")


def convert_svg_to_png(svg_path, png_path, scale=2.0):
    """Convert SVG to PNG using persistent browser"""
    try:
        # Lazy import playwright - only when actually needed
        try:
            from playwright.sync_api import sync_playwright  # noqa: F401
        except ImportError:
            print("Error: playwright not installed. Install it with: pip install playwright && playwright install chromium")
            return False
        
        start_time = time.time()
        svg_path = Path(svg_path).absolute()
        png_path = Path(png_path).absolute()
        
        if not svg_path.exists():
            print(f"Error: SVG file not found: {svg_path}")
            return False
        
        with open(svg_path, 'r', encoding='utf-8') as f:
            svg_content = f.read()
        
        download_fonts(svg_content)
        
        viewbox_match = re.search(r'viewBox="[\d\s.]+ ([\d.]+) ([\d.]+)"', svg_content)
        if viewbox_match:
            width = int(float(viewbox_match.group(1)) * scale)
            height = int(float(viewbox_match.group(2)) * scale)
        else:
            width, height = 1600, 1200
        
        daemon = BrowserDaemon.get_instance()
        page = daemon.get_page(width, height)
        page.set_content(f'<!DOCTYPE html><html><body style="margin:0">{svg_content}</body></html>')
        page.wait_for_timeout(1000)
        page.screenshot(path=str(png_path), full_page=True)
        page.close()
        
        total_time = time.time() - start_time
        print(f"Total conversion time: {total_time:.2f}s")
        return True
        
    except ImportError:
        print("Error: playwright not installed. Install it with: pip install playwright && playwright install chromium")
        return False
    except Exception as e:
        print(f"Error converting SVG to PNG: {e}")
        return False


if __name__ == "__main__":
    # Test conversion
    svg_file = "./src/svg/git_cheatsheet.svg"
    png_file = "./src/image/git_cheatsheet.png"
    
    if convert_svg_to_png(svg_file, png_file, scale=2.0):
        print(f"✓ Successfully converted {svg_file} to {png_file}")
    else:
        print(f"✗ Failed to convert {svg_file}")