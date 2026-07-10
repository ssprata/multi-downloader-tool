# Synth Downloader

Synth Downloader is a self-contained desktop download manager designed for Windows. It features customizable hierarchical download profiles, support for multiple download engines, and a dark, modern user interface. 

The application serves as a graphical front-end for popular command-line utilities, including `aria2c` for high-speed file transfers, `yt-dlp` for video and audio extraction, and `gallery-dl` for image board gallery scraping. By wrapping these command-line tools in a PyQt6 graphical interface, it simplifies direct downloading, batch scheduling, profile management, and post-processing.

---

## Key Features

* **Hierarchical Profile Management**: Organize download profiles into expandable and collapsible category folders. This is configured locally via a structured JSON configuration.
* **Drag-and-Drop Reorganization**: Move profile cards between category folders directly through the graphical user interface. Changes are immediately persisted in the configuration file.
* **Visual Profile Creator**: Create custom download categories and profiles dynamically using built-in themed dialog inputs.
* **Real-time Download Metrics**: Background threads parse stdout streams from running download subprocesses to extract and display live progress metrics (percentage, speed, and estimated time of arrival).
* **Engines and Post-Processing Manager**: Download and integrate optional binaries such as `gallery-dl` and `FFmpeg` directly from the dashboard. FFmpeg is utilized by `yt-dlp` to automatically merge high-definition audio and video streams.
* **Integrated Process Control**: Pause, resume, or cleanly cancel active downloads without orphaned subprocesses running in the background.
* **Automated Bootstrap**: Checks for missing required engine binaries on launch and auto-downloads them dynamically using an integrated splash loader.

---

## Directory Structure

```
multi-downloader-tool/
├── .gitignore
├── config.json              # Active settings, categories, and profiles store
├── requirements.txt         # Python dependencies (PyQt6, requests)
├── run.bat                  # Bootstrap and launcher script
├── main.py                  # Entry bootstrap script (validates requirements and launches GUI)
├── config_manager.py        # Logic for loading, saving, and updating profile configurations
├── dependency_manager.py    # Binary manager for downloading and extracting required executables
├── downloader.py            # Asynchronous subprocess management and stdout regex parsing
├── bin/                     # Auto-generated directory containing local CLI binaries
│   ├── aria2c.exe           # High-speed download engine
│   ├── yt-dlp.exe           # Media downloader engine
│   ├── gallery-dl.exe       # Optional gallery scraper engine (if downloaded)
│   ├── ffmpeg.exe           # Optional post-processing converter (if downloaded)
│   └── ffprobe.exe          # Optional media streams analyzer (if downloaded)
└── ui/
    ├── __init__.py
    ├── styles.py            # Cyberpunk/Synthwave stylesheet definitions (QSS)
    └── main_window.py       # Main GUI layout, custom dialogs, tree view, and event callbacks
```

---

## Quick Start Guide

### Prerequisites

Synth Downloader is designed to run on Windows 10 or Windows 11. It requires Python 3.8 or newer.

If Python is not installed on your system or is missing from your system `PATH`, the bootstrap launcher will automatically download and install Python 3.11.9 to your user profile directory (`%LOCALAPPDATA%\Programs\Python\Python311`).

### Running the Application

1. Clone or download this repository.
2. Double-click the **`run.bat`** file in the root directory.
3. The bootstrap script will:
   * Detect or install Python.
   * Create a local virtual environment in the `.venv` directory.
   * Upgrade `pip` and install all dependencies listed in `requirements.txt`.
   * Start the PyQt6 application.
4. On the first launch, the boot splash screen will automatically fetch the core binaries (`aria2c.exe` and `yt-dlp.exe`) and place them in the `bin/` subdirectory.

---

## Configuration Schema

All settings, profiles, and directories are stored in `config.json`. The application auto-generates this file on launch if it is missing.

### Configuration Format Example

```json
{
  "active_profile": "Downloads",
  "profiles": [
    {
      "name": "Sprata MP4",
      "tool": "yt-dlp",
      "folder": "Sprata",
      "export_dir": "F:\\Sprata\\Mp4",
      "aria2_settings": {
        "max_connection_per_server": 16,
        "split": 16,
        "max_download_limit": "0",
        "custom_flags": ""
      },
      "ytdlp_settings": {
        "format": "bestvideo+bestaudio/best",
        "video_format": "mp4",
        "extract_audio": false,
        "audio_format": "mp3",
        "audio_quality": "0",
        "embed_subs": false,
        "custom_flags": ""
      },
      "gallerydl_settings": {
        "custom_flags": ""
      }
    },
    {
      "name": "Downloads",
      "tool": "aria2c",
      "folder": "Downloads",
      "export_dir": "C:\\Users\\User\\Downloads",
      "aria2_settings": {
        "max_connection_per_server": 16,
        "split": 16,
        "max_download_limit": "0",
        "custom_flags": ""
      },
      "ytdlp_settings": {
        "format": "bestaudio/best",
        "video_format": "best",
        "extract_audio": false,
        "audio_format": "mp3",
        "audio_quality": "5",
        "embed_subs": false,
        "custom_flags": ""
      },
      "gallerydl_settings": {
        "custom_flags": ""
      }
    }
  ]
}
```

### Profile Field Description

| Field | Type | Description |
| :--- | :--- | :--- |
| `name` | String | Unique identifier for the download profile. |
| `tool` | String | The selected engine for the profile: `"aria2c"`, `"yt-dlp"`, or `"gallery-dl"`. |
| `folder` | String | The parent category folder name. |
| `export_dir` | String | Directory where downloaded files will be saved. |
| `aria2_settings` | Object | Connection, split, and bandwidth settings specific to aria2c execution. |
| `ytdlp_settings` | Object | Target format, video container format, audio extraction options, and quality settings for yt-dlp. |
| `gallerydl_settings` | Object | Custom command-line flags and parameters for gallery-dl extraction. |

---

## Subprocess Execution and Regex Metrics Extraction

Downloads are spawned asynchronously using Python's `subprocess.Popen`. Standard output and standard error streams are redirected, read on separate background threads, and matched against regex patterns to calculate metrics:

* **aria2c Parsing**: Matches percent progress `(15%)`, current speed `CN:16 DL:4.2MiB`, and connection counts.
* **yt-dlp Parsing**: Matches progress patterns `[download]  45.2% of  120.50MiB at  3.12MiB/s ETA 00:24`.
* **gallery-dl Parsing**: Logs output matching downloaded targets.
