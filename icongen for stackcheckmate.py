# ===============================================================
# StackCheckMate Icon Builder
# Purpose: Convert a single PNG into .ICO (Windows), .ICNS (macOS),
#          and optimized .PNG (Linux) for universal app building.
# Author: Chisom Life Eke
# ===============================================================

import os
from PIL import Image

def create_all_icons(source_png="icon.png"):
    if not os.path.exists(source_png):
        print(f"❌ Source file '{source_png}' not found. Please place your icon.png in this folder.")
        return

    # Load the image
    img = Image.open(source_png)

    # Define export file names
    icon_ico = "icon.ico"
    icon_icns = "icon.icns"
    icon_linux = "icon_linux.png"

    # Generate multi-size ICO for Windows
    try:
        img.save(icon_ico, format="ICO", sizes=[(16,16), (32,32), (48,48), (64,64), (128,128), (256,256)])
        print("✅ icon.ico (Windows) created successfully!")
    except Exception as e:
        print(f"⚠️ ICO generation failed: {e}")

    # Generate ICNS for macOS
    try:
        # Convert to correct size for macOS icons (512x512 recommended)
        icns_img = img.resize((512, 512))
        icns_img.save(icon_icns, format="ICNS")
        print("✅ icon.icns (macOS) created successfully!")
    except Exception as e:
        print(f"⚠️ ICNS generation failed: {e}")

    # Generate optimized PNG for Linux
    try:
        linux_img = img.resize((256, 256))
        linux_img.save(icon_linux, format="PNG", optimize=True)
        print("✅ icon_linux.png (Linux) created successfully!")
    except Exception as e:
        print(f"⚠️ PNG optimization failed: {e}")

    print("\n🎉 All possible icon formats generated successfully!")


if __name__ == "__main__":
    create_all_icons()