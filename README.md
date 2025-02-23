# Avatar: The Game - Save Editor (WIP)

A Python-based save editor for Avatar: The Game for the Xbox 360 version of the game, featuring a graphical user interface for modifying game saves.

## Features

- Edit player stats and character information
- Manage territory control and base configurations
- Track and modify achievements **(WIP)**
- View and edit character face selections **(WIP)**
- Built-in XML editor for advanced modifications **(WIP)**
- Automatic backup system

![Screenshot 2025-02-22 000615](https://github.com/user-attachments/assets/2f129354-69a5-4192-8cd6-7eab12b5a099)
![Screenshot 2025-02-22 000614](https://github.com/user-attachments/assets/78253f82-48a1-4ba7-bc51-bc72a2e78d43)
![Screenshot 2025-02-22 000613](https://github.com/user-attachments/assets/da73c199-a265-4563-9c8b-b848627789e1)
![Screenshot 2025-02-22 000612](https://github.com/user-attachments/assets/9d68e73e-2a34-459e-bc19-675ed679c675)
![Screenshot 2025-02-22 000611](https://github.com/user-attachments/assets/2cb10f4f-9379-4db4-9962-44e61251c1e0)


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
