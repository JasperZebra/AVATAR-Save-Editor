from cx_Freeze import setup, Executable
import os
import sys

# Define the base directory
base_dir = os.path.abspath(os.path.dirname(__file__))

# Collect all files and folders recursively
def collect_files(directory):
    files = []
    for path, dirs, filenames in os.walk(directory):
        for filename in filenames:
            files.append((os.path.join(path, filename), os.path.relpath(os.path.join(path, filename), base_dir)))
    return files

# List all directories you want to include
# Add or remove directories as needed
directories_to_include = [
    'Face_Images',          # Replace with your actual folder names
    'Icon',
    # Add any other folders you need
]

# Collect all files from these directories
include_files = []
for directory in directories_to_include:
    if os.path.exists(os.path.join(base_dir, directory)):
        include_files.extend(collect_files(os.path.join(base_dir, directory)))

# Add individual files that are in the root directory
root_files = [
    'main.py',    # Replace with your actual filenames
    'achievements_manager.py',
    'checksum_handler.jsx',
    'Face_Image_Window.py',
    'models.py',
    'navigation_manager.py',
    'pandora_pedia_manager.py',
    'stats_manager.py',
    'territory_manager.py',
    'ui_components.py',
    'xml_handler.py',
    'xml_viewer.py'
    # Add any other individual files
]

for file in root_files:
    if os.path.exists(os.path.join(base_dir, file)):
        include_files.append((os.path.join(base_dir, file), file))

# Build options
build_options = {
    'include_files': include_files,
    'packages': [
        # Standard libraries
        'os', 'sys', 'json', 'tkinter', 'pathlib', 'typing', 
        'xml.etree.ElementTree', 'logging',
        # Tkinter related
        'tkinter.ttk', 'tkinter.filedialog', 'tkinter.messagebox', 'tkinter.font',
        # Third-party packages
        'PIL',  # This is the import name for Pillow
        # Add any other dependencies here
    ],
    'excludes': [
        # Packages you want to exclude to reduce size
        'test', 'unittest',
    ],
    'include_msvcr': True,  # Include Microsoft Visual C Runtime
}

# Set up the executable
executables = [
    Executable(
        'main.py',  # Replace with your actual main script
        base='Win32GUI' if sys.platform == 'win32' else None,  # Use console for debugging, Win32GUI for GUI apps
        target_name='AVATAR_The_Game_Save_Editor.exe',  # The name of your final executable
        icon='Icon/avatar_icon.ico',  # Replace with path to your icon file, if you have one
    )
]

# Setup
setup(
    name='AVATAR The Game Save Editor',  # Replace with your application name
    version='1.0.0',
    description='Game Save Editor',  # Replace with your description
    author='Jasper_Zebra',  # Replace with your name
    options={'build_exe': build_options},
    executables=executables
)