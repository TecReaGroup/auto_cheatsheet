"""Main controller for cheatsheet generation"""
import yaml
import hashlib
from script.svg_processor import generate_svg, post_process_svg
from script.svg_to_png import convert_svg_to_png
from pathlib import Path


def compute_content_hash(yaml_file):
    """Compute SHA256 hash of YAML file content"""
    try:
        with open(yaml_file, 'rb') as f:
            content = f.read()
            return hashlib.sha256(content).hexdigest()
    except Exception as e:
        print(f"✗ Error computing hash for {yaml_file}: {e}")
        return None


def load_content_hashes(data_yaml_path):
    """Load stored content hashes from data.yaml"""
    try:
        if not data_yaml_path.exists():
            return {}
        
        with open(data_yaml_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    except Exception as e:
        print(f"✗ Error loading data.yaml: {e}")
        return {}


def save_content_hashes(data_yaml_path, hashes):
    """Save content hashes to data.yaml"""
    try:
        with open(data_yaml_path, 'w', encoding='utf-8') as f:
            yaml.dump(hashes, f, default_flow_style=False, allow_unicode=True)
    except Exception as e:
        print(f"✗ Error saving data.yaml: {e}")


def load_data(yaml_file):
    """Load command data from YAML file"""
    try:
        with open(yaml_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            
        # Validate required fields
        if not data:
            raise ValueError("YAML file is empty")
        if 'filename' not in data:
            raise ValueError("Missing 'filename' field in YAML")
        if 'sections' not in data or not data['sections']:
            raise ValueError("Missing or empty 'sections' field in YAML")
            
        return data
    except Exception as e:
        print(f"✗ Error loading {yaml_file}: {e}")
        return None


def process_cheatsheet(yaml_file, svg_dir, png_dir, to_png):
    """Process a single cheatsheet: YAML -> SVG -> PNG"""
    try:
        # Load and validate data
        data = load_data(yaml_file)
        if not data:
            return False
        
        # Determine output paths
        filename = data['filename']
        svg_file = svg_dir / f"{filename}.svg"
        png_file = png_dir / f"{filename}.png"
        
        # Generate SVG
        title = generate_svg(data, str(svg_file))
        post_process_svg(str(svg_file), line_width=1060, margin=25)
        print(f"✓ {title} saved as {svg_file}")
        
        # Convert to PNG
        if to_png:
            if convert_svg_to_png(str(svg_file), str(png_file), scale=2.0):
                print(f"✓ PNG version saved as {png_file}")
            else:
                print(f"✗ Failed to generate PNG for {filename}")
                return False
        
        return True
            
    except Exception as e:
        print(f"✗ Error processing {yaml_file.name}: {e}")
        return False


def scan_and_generate(to_png=False):
    """Scan doc directory and generate SVGs/PNGs for all YAML files"""
    # Setup directories
    doc_dir = Path('./src/doc')
    svg_dir = Path('./src/svg')
    png_dir = Path('./src/image')
    
    # Ensure directories exist
    doc_dir.mkdir(parents=True, exist_ok=True)
    svg_dir.mkdir(parents=True, exist_ok=True)
    png_dir.mkdir(parents=True, exist_ok=True)
    
    # Find all YAML files
    yaml_files = list(doc_dir.glob('*.yaml')) + list(doc_dir.glob('*.yml'))
    
    if not yaml_files:
        print(f"✗ No YAML files found in {doc_dir}")
        return
    
    print(f"\n{'='*60}")
    print(f"Found {len(yaml_files)} YAML file(s) in {doc_dir}")
    print(f"{'='*60}\n")
    
    # Process each YAML file
    processed = 0
    skipped = 0
    failed = 0
    
    # Load stored content hashes
    data_yaml_path = Path('./src/data.yaml')
    stored_hashes = load_content_hashes(data_yaml_path)
    updated_hashes = {}
    
    for yaml_file in sorted(yaml_files):
        print(f"\nProcessing: {yaml_file.name}")
        print("-" * 60)
        
        # Load to get filename
        data = load_data(yaml_file)
        if not data:
            failed += 1
            continue
            
        filename = data['filename']
        svg_file = svg_dir / f"{filename}.svg"
        
        # Compute current content hash
        current_hash = compute_content_hash(yaml_file)
        if not current_hash:
            failed += 1
            continue
        
        # Check if content has changed
        stored_hash = stored_hashes.get(filename)
        content_unchanged = (stored_hash == current_hash)
        
        # Skip if content unchanged and outputs exist
        if content_unchanged and svg_file.exists():
            print(f"⊳ Skipping (content unchanged): {filename}")
            updated_hashes[filename] = current_hash
            skipped += 1
            continue
        
        # Process the cheatsheet
        if process_cheatsheet(yaml_file, svg_dir, png_dir, to_png):
            updated_hashes[filename] = current_hash
            processed += 1
        else:
            failed += 1
    
    # Save updated hashes
    if updated_hashes:
        save_content_hashes(data_yaml_path, updated_hashes)
    
    # Summary
    print(f"\n{'='*60}")
    print("Summary:")
    print(f"  Processed: {processed}")
    print(f"  Skipped:   {skipped}")
    print(f"  Failed:    {failed}")
    print(f"  Total:     {len(yaml_files)}")
    print(f"{'='*60}\n")


def main():
    """Main entry point"""
    scan_and_generate(to_png=False)


if __name__ == "__main__":
    main()