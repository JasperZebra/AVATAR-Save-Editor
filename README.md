# Avatar: The Game - Save Editor (WIP)

A Python-based save editor for Avatar: The Game for the Xbox 360 version of the game, featuring a graphical user interface for modifying game saves.

## Features

- Edit player stats and character information
- Manage territory control and base configurations
- Track and modify achievements **(WIP)**
- View and edit character face selections **(WIP)**
- Built-in XML editor for advanced modifications **(WIP)**
- Automatic backup system

## Requirements

- Python 3.x
- tkinter
- Pillow (PIL)
- xml.etree.ElementTree

## Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install pillow
```

## Usage

1. Run the editor:
```bash
python main.py
```

2. Click "Load Save File" to open your .sav file
3. Modify settings in any of the available tabs:
   - Player Stats: Modify character attributes, faction alignment, and game progress
   - Territory Control: Manage territory ownership and unit deployment
   - Achievements: View and unlock achievements **(WIP)**

## Features Detail

### Player Stats
- Character appearance customization **(WIP)**
- Faction alignment (Na'vi/RDA)
- Experience points and level management **(WIP)**
- Game time tracking
- Location coordinates

### Territory Management
- Territory ownership assignment
- Unit deployment (Ground/Air/Troops)
- Base configuration
- Defense flag management

### Achievements **(WIP)**
- View achievement status
- Unlock individual or all achievements
- Track completion progress

### XML Editor **(WIP)**
- Direct XML editing capability
- Syntax validation
- Pretty-printing
- Section navigation

## File Structure
- `main.py`: Main application entry point
- `stats_manager.py`: Player statistics handling
- `territory_manager.py`: Territory control management
- `achievements_manager.py`: Achievement system
- `xml_handler.py`: Save file XML processing
- `Face_Image_Window.py`: Character face preview
- `ui_components.py`: Common UI elements

## Safety Features
- Automatic backup creation
- Size validation for save files
- XML structure validation
- Error logging

## Technical Notes
- Save file size must match the expected 444 KB
- Handles UTF-8 encoding with error correction
- Maintains original file structure outside XML section

## Error Handling
The editor includes comprehensive error handling and logging:
- Invalid file format detection
- XML parsing error recovery
- Size validation warnings
- Automatic backup on modifications

## Contributing
Found a bug or want to contribute? Please create an issue or submit a pull request.

## Support
For issues and support, please create a GitHub issue with:
- Save file version
- Error message/logs
- Steps to reproduce the problem
