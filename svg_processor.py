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
    """Replace dashed lines with solid SVG lines"""
    with open(svg_file, "r", encoding="utf-8") as f:
        svg_content = f.read()
    
    pattern = r'<text class="([^"]*)" x="([^"]+)" y="([^"]+)"[^>]*>&#160;(─+)&#160;</text>'
    
    def replace_with_line(match):
        x = float(match.group(2))
        y = float(match.group(3))
        return f'<line x1="{x + margin}" y1="{y-5}" x2="{x + line_width + margin}" y2="{y-5}" stroke="#c5c8c6" stroke-width="1.5"/>'
    
    svg_content = re.sub(pattern, replace_with_line, svg_content)
    
    with open(svg_file, "w", encoding="utf-8") as f:
        f.write(svg_content)