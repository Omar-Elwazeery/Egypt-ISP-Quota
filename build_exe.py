import PyInstaller.__main__
import customtkinter
import os
import sys
from PIL import Image

# 1. Prepare Icon
icon_file = 'app_icon.ico'
png_file = 'app_icon.png'

if not os.path.exists(icon_file):
    if os.path.exists(png_file):
        print(f"Converting {png_file} to {icon_file}...")
        try:
            img = Image.open(png_file)
            img.save(icon_file, format='ICO', sizes=[(256, 256)])
            print("Icon created successfully.")
        except Exception as e:
            print(f"Failed to create icon: {e}")
            icon_file = None # Skip icon if conversion fails
    else:
        print("No source image found for icon. Skipping.")
        icon_file = None
else:
    print(f"Using existing {icon_file}")

# 2. Get customtkinter path
ctk_path = os.path.dirname(customtkinter.__file__)
print(f"CustomTkinter path found: {ctk_path}")

# Determine separator for add-data based on OS
separator = ';' if os.name == 'nt' else ':'

# 3. Build Arguments
args = [
    'main_ui.py',
    '--name=EgyptISPQuota',
    '--onedir',
    '--noconsole',
    f'--add-data={ctk_path}{separator}customtkinter/',
    '--clean',
]

if icon_file:
    args.append(f'--icon={icon_file}')

print("Starting build process...")
PyInstaller.__main__.run(args)
print("Build complete! check the 'dist' folder.")
