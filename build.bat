@echo off
REM ===============================================================
REM 🧠 StackCheckMate Smart Installer Build Script (Windows BAT)
REM Author: Chisom Life Eke (Quick Red Tech)
REM Purpose: Build standalone Windows .exe for Smart Installer
REM ===============================================================

set APP_NAME=SmartInstaller
set MAIN_SCRIPT=smart_installer.py
set ICON_FILE=icon.ico
set DIST_DIR=build_output

echo 🚀 Building %APP_NAME% using PyInstaller...

REM Clean old builds
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist %DIST_DIR% rmdir /s /q %DIST_DIR%

REM Compile to one-file executable with PySide6 support
pyinstaller --noconfirm --onefile --windowed ^
  --name "%APP_NAME%" ^
  --icon "%ICON_FILE%" ^
  --add-data "assets;assets" ^
  --hidden-import PySide6 ^
  --hidden-import PySide6.QtCore ^
  --hidden-import PySide6.QtGui ^
  --hidden-import PySide6.QtWidgets ^
  "%MAIN_SCRIPT%"

REM Create output folder and move built exe
mkdir %DIST_DIR%
move dist\* %DIST_DIR% >nul

echo ✅ Build completed!
echo 📦 EXE located at: %DIST_DIR%\%APP_NAME%.exe

pause