# Cheatsheet Viewer Application

A modern PySide6 application for viewing and managing SVG cheatsheets with a draggable floating orb interface.

## Features

### Core Features
- **Draggable Floating Orb** - Main entry point that can be positioned anywhere on screen
- **SVG Selection Menu** - Browse, search, and select cheatsheet files
- **High-Quality SVG Rendering** - Proper aspect ratio preservation with QSvgWidget
- **Smooth Scrolling** - Vertical and horizontal navigation with mouse wheel support
- **Manual PNG Export** - Export displayed cheatsheets to high-quality PNG files

### UI/UX Features
- **Modern Interface** - Polished design with visual feedback
- **Dark/Light Themes** - Toggle between themes with Ctrl+T
- **Responsive Layout** - Adapts to content and window size
- **Hover Effects** - Visual feedback on interactive elements
- **Smooth Animations** - Animated orb scaling and transitions

### Navigation & Viewing
- **Zoom Controls** - Zoom in/out with toolbar, slider, or Ctrl+Mouse Wheel
- **Fit to Width/Height** - Quick fit options (Ctrl+W, Ctrl+H)
- **Reset Zoom** - Return to 100% with Ctrl+0
- **Zoom Range** - 25% to 400% with fine control

### Organization
- **Recent Files** - Quick access to recently viewed cheatsheets
- **Favorites System** - Star your most-used cheatsheets
- **Search Functionality** - Filter cheatsheets by name
- **Tabbed Interface** - All, Recent, and Favorites tabs

### Persistence
- **Settings Saved** - Window geometry, zoom level, and orb position
- **Recent History** - Last 10 opened files remembered
- **Favorites Stored** - Favorites persist across sessions
- **Theme Preference** - Theme choice saved

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Ensure you have SVG files in `./src/svg/` directory

## Usage

### Starting the Application

```bash
python app.py
```

### Basic Workflow

1. **Launch** - A floating orb appears on screen
2. **Click Orb** - Opens the selection menu
3. **Select File** - Choose a cheatsheet from All/Recent/Favorites
4. **View** - SVG opens in viewer window with full controls
5. **Export** - Save as PNG if needed (Ctrl+E)

### Keyboard Shortcuts

#### File Operations
- `Ctrl+E` - Export as PNG
- `Ctrl+W` - Close window

#### Zoom Controls
- `Ctrl++` or `Ctrl+=` - Zoom in
- `Ctrl+-` - Zoom out
- `Ctrl+0` - Reset zoom to 100%
- `Ctrl+W` - Fit to width
- `Ctrl+H` - Fit to height
- `Ctrl+Mouse Wheel` - Zoom in/out

#### Appearance
- `Ctrl+T` - Toggle theme (light/dark)

### Orb Features

- **Drag** - Click and hold to move the orb anywhere
- **Click** - Single click opens selection menu
- **Hover** - Orb scales up slightly on hover
- **Position Saved** - Orb remembers its position

### Selection Menu Features

- **Tabs** - Switch between All, Recent, and Favorites
- **Search** - Type to filter cheatsheets
- **Double-Click** - Quick open
- **Favorites** - Star/unstar files for quick access
- **Theme** - Matches application theme

### Viewer Features

- **Toolbar Controls** - Quick access to zoom and export
- **Menu Bar** - Full feature access via File and View menus
- **Status Bar** - Shows current zoom and file info
- **Mouse Wheel** - Scroll vertically, or zoom with Ctrl held
- **High Quality Export** - 2x resolution PNG export

## Architecture

### Modular Design

```
app.py                  # Main application entry point
core/
  settings_manager.py   # Persistent settings management
ui/
  floating_orb.py       # Draggable orb widget
  selection_menu.py     # File selection interface
  svg_viewer.py         # SVG viewing window
```

### Key Components

#### CheatsheetApp
- Main application class
- Manages orb and viewer instances
- Coordinates between components

#### SettingsManager
- QSettings-based persistence
- Stores window geometry, zoom, favorites
- Manages theme preferences

#### FloatingOrb
- Frameless, translucent window
- Custom painting with gradients
- Drag and drop functionality
- Animated hover effects

#### SelectionMenu
- Tabbed interface for file browsing
- Search and filter capabilities
- Recent files and favorites management
- Theme-aware styling

#### SVGViewerWindow
- QSvgWidget for rendering
- Zoom and fit controls
- High-quality PNG export
- Keyboard shortcuts
- Theme support

## Customization

### Adding Cheatsheets

Place SVG files in `./src/svg/` directory. The application will automatically discover them.

### Theme Customization

Themes are defined in the `apply_theme()` methods of each widget. Modify the QSS stylesheets to customize colors and appearance.

### Default Settings

Edit `core/settings_manager.py` to change default values:
- Default zoom level (currently 1.0)
- Recent files limit (currently 10)
- Default theme (currently "dark")

## Technical Details

### Dependencies
- PySide6 - Qt for Python framework
- QSvgWidget - SVG rendering
- QSettings - Persistent storage

### SVG Rendering
- Uses Qt's native SVG renderer
- Maintains aspect ratio during zoom
- Anti-aliasing enabled for smooth rendering

### Export Quality
- PNG exports at 2x resolution
- Full anti-aliasing
- Configurable quality settings

### Performance
- Efficient SVG rendering
- Minimal resource usage when idle
- Fast file loading and switching

## Troubleshooting

### No SVG files showing
- Check that files are in `./src/svg/` directory
- Ensure files have `.svg` extension
- Verify files are valid SVG format

### Orb not visible
- Check if positioned off-screen
- Delete settings to reset position
- Look in corners of screen

### Export fails
- Ensure write permissions to output directory
- Check disk space
- Verify output path is valid

### Theme not applying
- Restart application
- Check QSettings permissions
- Try toggling theme with Ctrl+T

## Future Enhancements

Potential additions:
- Multi-monitor support
- Custom keyboard shortcuts
- Batch export functionality
- Annotations and markup
- Print support
- Thumbnail previews
- Collections/categories
- Cloud sync
- Auto-update checking

## License

This application is part of the auto_cheatsheet project.