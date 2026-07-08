# 🌌 Synth Downloader

A premium, self-contained desktop download manager featuring customizable profiles, multi-engine support, and a responsive **Cyberpunk/Synthwave** user interface. 

Synth Downloader acts as a visual wrapper for popular CLI tools like `aria2c`, `yt-dlp`, and `gallery-dl`, making it easy to schedule, manage, and monitor direct downloads and media links without touching the command prompt.

---

## ✨ Features

- **📂 Profile-Based Exports**: Create download profiles targeting different folders (e.g., `Downloads/Music` for music files, `Downloads/Videos` for video files) and store unique parameters for each tool.
- **⚡ Dual Core Engines**: Powered by `aria2c` for high-speed direct file downloads (supports multi-connection splitting) and `yt-dlp` for videos and media downloads.
- **🖼️ Optional Engines Manager**: Download and integrate optional tools like `gallery-dl` (for image board galleries) and `FFmpeg` (essential for yt-dlp to merge high-resolution video and audio formats) directly from the GUI.
- **📊 Real-time Metrics**: Background threads parse stdout streams to deliver live percentage progress, ETA, and download speeds.
- **🛑 Cancellation Control**: Cancel active downloads cleanly without creating orphaned background processes.
- **🖥️ Cyberpunk Aesthetics**: A sleek dark theme with vibrant neon cyan (`#00f0ff`) and cyber pink (`#ff007f`) accents, custom styling sheet (QSS), scrollbars, and glowing buttons.
- **📜 Engine logs console**: Collapsible live terminal console streaming raw output outputs.
- **📦 Zero-Configuration Startup**: The application detects missing required utilities on launch and auto-downloads them using a beautiful boot splash screen.

---

## 🛠️ Project Structure

```
multi-downloader-tool/
├── .gitignore
├── config.json              # Local settings & profile store (generated on launch)
├── requirements.txt         # Package requirements (PyQt6, requests)
├── run.bat                  # Setup launcher script
├── main.py                  # Entry bootstrap script (handles startup checks)
├── config_manager.py        # Profiles loading and saving logic
├── dependency_manager.py    # Binary checker, downloader, and zip extractor
├── downloader.py            # Async subprocess execution & regex stdout parsing
├── bin/                     # Directory storing engine binaries (generated on launch)
│   ├── aria2c.exe
│   └── yt-dlp.exe
└── ui/
    ├── __init__.py
    ├── styles.py            # Cyan/Magenta neon cyberpunk stylesheet QSS
    └── main_window.py       # GUI layouts, widget wrappers, and callbacks
```

---

## 🚀 Quick Start

Ensure you have **Python 3.8 or newer** installed and configured in your system `PATH`. No other pre-installations are required.

### Run on Windows

1. Download or clone this repository.
2. Double-click **`run.bat`** (or execute `.\run.bat` from PowerShell/Command Prompt).
3. The script will automatically:
   - Initialize a local virtual environment (`.venv/`).
   - Install required Python packages (`PyQt6` and `requests`).
   - Launch the application.
4. On your **first launch**, a splash screen will boot to download `aria2c.exe` and `yt-dlp.exe` directly into the local `bin/` folder.
5. Once completed, the main dashboard will open.

---

## ⚙️ How to Use

1. **Select or Create a Profile**: Select from default templates in the left panel (e.g., *YouTube Music*, *YouTube Video*, or *Default Direct*) or click **+ New** to create a custom profile.
2. **Configure Settings**: For the active profile, adjust the output folder using the **Browse** dialog, select the tool configuration, and modify variables (e.g. connections, formats, subtitles).
3. **Engage Downloads**: 
   - Paste one or more links into the top URLs text area (one link per line for batch execution).
   - Press the glowing pink **ENGAGE DOWNLOAD** button.
4. **Monitor Queue**: Watch the progress bars in the active queue, cancel downloads, or expand the console output below to check command stdout streams.
5. **Manage Optional Tools**: Navigate to the **Engines & Tools** tab to inspect status or click **Download & Install** to fetch `FFmpeg` or `gallery-dl` dynamically.
