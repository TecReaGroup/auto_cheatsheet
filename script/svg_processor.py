"""SVG processing module for cheatsheet generation"""
from rich.console import Console
from rich.table import Table
from rich.align import Align
from io import StringIO
from rich import box
import re


def create_table(section):
    """Create a Rich table for a section"""
    table = Table(
        title=section['title'],
        show_header=True,
        header_style="bold cyan",
        box=box.SIMPLE,
        title_justify="center",
        padding=(0, 2),
        expand=False
    )
    table.add_column("Command", style="green", width=40, justify="left")
    table.add_column("Description", style="yellow", width=40, justify="left")
    
    for cmd in section['commands']:
        table.add_row(cmd['command'], cmd['description'])
    
    return table


def generate_svg(data, output_file, console_width=100):
    """Generate SVG from data"""
    console = Console(record=True, file=StringIO(), width=console_width)
    
    for section in data['sections']:
        table = create_table(section)
        console.print(Align.center(table))
        console.print()
    
    svg_title = data.get('terminal_title')
    console.save_svg(output_file, title=svg_title)
    
    return svg_title


def post_process_svg(svg_file, line_width=1060, margin=25):
    """Replace dashed lines with solid SVG lines, center section titles, and adjust terminal title size"""
    with open(svg_file, "r", encoding="utf-8") as f:
        svg_content = f.read()
    
    # Extract viewBox width for centering calculations
    viewbox_match = re.search(r'viewBox="0 0 (\d+(?:\.\d+)?)', svg_content)
    svg_width = float(viewbox_match.group(1)) if viewbox_match else 1238
    
    # Change terminal title font size in CSS
    title_font_pattern = r'(\.terminal-\d+-title\s*\{[^}]*font-size:\s*)18px'
    svg_content = re.sub(title_font_pattern, r'\g<1>20px', svg_content)
    
    # Add inline font-size attribute to title text element for Qt compatibility
    title_text_pattern = r'(<text class="terminal-\d+-title"[^>]*?)>'
    svg_content = re.sub(title_text_pattern, r'\1 font-size="20">', svg_content)
    
    # Add spacing below terminal title by adjusting content group position
    content_group_pattern = r'(<g transform="translate\(9,\s*)(\d+)(\)"\s+clip-path)'
    svg_content = re.sub(content_group_pattern, lambda m: f'{m.group(1)}{int(m.group(2)) + 15}{m.group(3)}', svg_content)
    
    # Replace dashed lines with solid SVG lines
    pattern = r'<text class="([^"]*)" x="([^"]+)" y="([^"]+)"[^>]*>&#160;(─+)&#160;</text>'
    
    def replace_with_line(match):
        x = float(match.group(2))
        y = float(match.group(3))
        return f'<line x1="{x + margin}" y1="{y-5}" x2="{x + line_width + margin}" y2="{y-5}" stroke="#c5c8c6" stroke-width="1.5"/>'
    
    svg_content = re.sub(pattern, replace_with_line, svg_content)
    
    # Center section titles (italic text with padding spaces)
    title_pattern = r'<text class="([^"]*-r2)" x="([^"]+)" y="([^"]+)"[^>]*>&#160;+([^<]+?)&#160;+</text>'
    
    def center_title(match):
        css_class = match.group(1)
        y = match.group(3)
        title_text = match.group(4)
        
        # Remove any remaining &#160; entities and strip
        clean_title = title_text.replace('&#160;', ' ').strip()
        
        # Calculate character width (approximate for monospace font at 20px)
        char_width = 12.2
        title_width = len(clean_title) * char_width
        
        # Calculate centered x position
        centered_x = (svg_width - title_width) / 2
        
        return f'<text class="{css_class}" x="{centered_x:.1f}" y="{y}" textLength="{title_width}">{clean_title}</text>'
    
    svg_content = re.sub(title_pattern, center_title, svg_content)
    
    with open(svg_file, "w", encoding="utf-8") as f:
        f.write(svg_content)