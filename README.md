# 🌌 Synth Downloader

A premium, self-contained desktop download manager featuring customizable hierarchical profiles, multi-engine support, and a responsive **Cyberpunk/Synthwave** user interface. 

Synth Downloader acts as a visual wrapper for popular CLI tools like `aria2c`, `yt-dlp`, and `gallery-dl`, making it easy to schedule, manage, and monitor direct downloads and media links without touching the command prompt.

---

## ✨ Features

- **📂 Hierarchical Profiles**: Organize your download profiles into expandable and collapsible category folders (e.g., `Music` or `Videos`) to keep the workspace clean.
- **🖱️ Drag-and-Drop Reorganization**: Drag profile cards and drop them directly inside folders or root sections to dynamically update their parent categories inside `config.json` instantly.
- **📁 Folder Creation**: Create custom categories using the `+ Folder` footer button, which prompts a custom-themed cyberpunk text input dialog.
- **🎬 Video Container Format Selector**: Convert or merge video streams into container formats like `mp4`, `mkv`, and `webm` losslessly using `--remux-video`.
- **⚡ Tab Settings Real-Time Auto-Save**: Toggling or modifying checkboxes, formats, or split connections immediately writes and commits updates directly into the active profile's settings inside `config.json` in real-time.
- **🎛️ Logs Visibility Toggle**: Toggle logs on or off dynamically via the `📜 Hide Logs` / `📜 Show Logs` header switch to save screen space and focus on active downloads.
- **🌌 Silent CyberMessageBox Overlay**: Replaces standard system warning and confirmation dialogs with beautiful custom-themed, frameless dialogs, eliminating annoying Windows default information and question sounds.
- **⚡ Dual Core Engines**: Powered by `aria2c` for high-speed direct file downloads (supports multi-connection splitting) and `yt-dlp` for videos and media downloads.
- **🖼️ Optional Engines Manager**: Download and integrate optional tools like `gallery-dl` (for image board galleries) and `FFmpeg` (essential for yt-dlp to merge high-resolution video and audio formats) directly from the GUI.
- **📊 Real-time Metrics**: Background threads parse stdout streams to deliver live percentage progress, ETA, and download speeds.
- **🛑 Cancellation Control**: Cancel active downloads cleanly without creating orphaned background processes.
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
    └── main_window.py       # GUI layouts, custom dialogs, drag-and-drop tree, and callbacks
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

1. **Category Folder Creation**: Click `+ Folder` at the bottom of the sidebar, enter a folder name (e.g. `Anime`), and click `Confirm` to add a new category.
2. **Interactive Grouping**: Grab any profile card (`📄`) and drag it into a folder (`📁`) to group it.
3. **Configure Settings**: Select the profile to modify, edit its export directory using the **Browse** dialog, select the tool configuration, and modify settings (e.g., connections, audio extraction).
4. **Engage Downloads**: 
   - Paste one or more links into the top URLs text area (one link per line for batch execution).
   - Press the glowing pink **ENGAGE DOWNLOAD** button.
5. **Monitor Queue**: Watch progress bars in the active queue, cancel downloads, or expand/hide the console logs below using the `📜 Hide/Show Logs` toggle.
6. **Manage Optional Tools**: Navigate to the **Engines & Tools** tab to inspect status or click **Download & Install** to fetch `FFmpeg` or `gallery-dl` dynamically.
