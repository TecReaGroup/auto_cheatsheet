"""Main controller for cheatsheet generation"""
import yaml
from svg_processor import generate_svg, post_process_svg
from svg_to_png import convert_svg_to_png
from pathlib import Path


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


def process_cheatsheet(yaml_file, svg_dir, png_dir):
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
        if convert_svg_to_png(str(svg_file), str(png_file), scale=2.0):
            print(f"✓ PNG version saved as {png_file}")
            return True
        else:
            print(f"✗ Failed to generate PNG for {filename}")
            return False
            
    except Exception as e:
        print(f"✗ Error processing {yaml_file.name}: {e}")
        return False


def scan_and_generate():
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
        png_file = png_dir / f"{filename}.png"
        
        # Check if outputs already exist
        if svg_file.exists() and png_file.exists():
            print(f"⊳ Skipping (already exists): {filename}")
            skipped += 1
            continue
        
        # Process the cheatsheet
        if process_cheatsheet(yaml_file, svg_dir, png_dir):
            processed += 1
        else:
            failed += 1
    
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
    scan_and_generate()


if __name__ == "__main__":
    main()