import os
import zipfile
import requests
import tempfile
import shutil

BIN_DIR = os.path.abspath("bin")

TOOLS = {
    "yt-dlp": {
        "filename": "yt-dlp.exe",
        "url": "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe",
        "is_zip": False
    },
    "aria2c": {
        "filename": "aria2c.exe",
        "url": "https://github.com/aria2/aria2/releases/download/release-1.37.0/aria2-1.37.0-win-64bit-build1.zip",
        "is_zip": True,
        "extract_target": "aria2c.exe"
    },
    "gallery-dl": {
        "filename": "gallery-dl.exe",
        "url": "https://github.com/mikf/gallery-dl/releases/latest/download/gallery-dl.exe",
        "is_zip": False
    },
    "ffmpeg": {
        "filename": "ffmpeg.exe",
        # Use a stable version from GyanD GitHub releases to ensure reliable downloading
        "url": "https://github.com/GyanD/codexffmpeg/releases/download/7.0.1/ffmpeg-7.0.1-essentials_build.zip",
        "is_zip": True,
        # We need both ffmpeg.exe and ffprobe.exe
        "extract_target": ["ffmpeg.exe", "ffprobe.exe"]
    },
    "spotdl": {
        "filename": "spotdl.exe",
        "url": "https://github.com/spotDL/spotify-downloader/releases/download/v4.2.8/spotdl-4.2.8-win-amd64.exe",
        "is_zip": False
    }
}

class DependencyManager:
    def __init__(self):
        os.makedirs(BIN_DIR, exist_ok=True)

    def get_tool_path(self, name):
        """Get the absolute path of a tool. Returns None if not found/installed."""
        if name not in TOOLS:
            return None
        
        info = TOOLS[name]
        if name == "ffmpeg":
            # Check both ffmpeg and ffprobe
            ffmpeg_path = os.path.join(BIN_DIR, "ffmpeg.exe")
            ffprobe_path = os.path.join(BIN_DIR, "ffprobe.exe")
            if os.path.exists(ffmpeg_path) and os.path.exists(ffprobe_path):
                return ffmpeg_path
        else:
            path = os.path.join(BIN_DIR, info["filename"])
            if os.path.exists(path):
                return path
        return None

    def is_installed(self, name):
        return self.get_tool_path(name) is not None

    def check_core_dependencies(self):
        """Returns True if core dependencies (yt-dlp and aria2c) are installed."""
        return self.is_installed("yt-dlp") and self.is_installed("aria2c")

    def download_tool(self, name, progress_callback=None):
        """
        Downloads a tool. progress_callback is called with (percent: float, speed_str: str)
        """
        if name not in TOOLS:
            raise ValueError(f"Unknown tool: {name}")

        info = TOOLS[name]
        url = info["url"]
        
        # Dynamically query latest spotdl release version
        if name == "spotdl":
            try:
                response_api = requests.get("https://api.github.com/repos/spotDL/spotify-downloader/releases/latest", timeout=8)
                if response_api.status_code == 200:
                    data = response_api.json()
                    for asset in data.get("assets", []):
                        asset_name = asset.get("name", "")
                        if asset_name.endswith(".exe") and "win" in asset_name.lower():
                            url = asset.get("browser_download_url")
                            break
            except Exception as e:
                print(f"Failed to fetch dynamic spotdl url, falling back: {e}")
        
        # Download file to a temp location
        response = requests.get(url, stream=True)
        if response.status_code != 200:
            raise Exception(f"Failed to download tool from {url} (status code: {response.status_code})")

        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        
        # Determine temporary file suffix
        suffix = ".zip" if info["is_zip"] else ".exe"
        
        # Stream download
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_path = temp_file.name
            try:
                for chunk in response.iter_content(chunk_size=1024 * 64):
                    if chunk:
                        temp_file.write(chunk)
                        downloaded += len(chunk)
                        if progress_callback and total_size > 0:
                            percent = (downloaded / total_size) * 100
                            # Simple speed string approximation
                            progress_callback(percent)
                
                temp_file.close()

                # Process extraction
                if info["is_zip"]:
                    # Extract zip
                    with zipfile.ZipFile(temp_path, 'r') as zip_ref:
                        targets = info["extract_target"]
                        if isinstance(targets, str):
                            targets = [targets]
                        
                        extracted_count = 0
                        for file_info in zip_ref.infolist():
                            # Check if the file matches any of our target names (ignoring directories)
                            basename = os.path.basename(file_info.filename)
                            if basename in targets:
                                target_dest = os.path.join(BIN_DIR, basename)
                                with zip_ref.open(file_info) as source, open(target_dest, 'wb') as dest:
                                    shutil.copyfileobj(source, dest)
                                extracted_count += 1
                        
                        if extracted_count == 0:
                            raise Exception(f"Targets {targets} not found in zip archive.")
                else:
                    # Move exe to bin directory
                    dest_path = os.path.join(BIN_DIR, info["filename"])
                    shutil.move(temp_path, dest_path)
                    
            finally:
                # Cleanup temp file if it still exists
                if os.path.exists(temp_path):
                    try:
                        os.remove(temp_path)
                    except Exception:
                        pass
        
        return self.get_tool_path(name)
