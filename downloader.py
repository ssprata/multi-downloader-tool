import os
import re
import subprocess
import shlex
from PyQt6.QtCore import QThread, pyqtSignal

# Regex for parsing yt-dlp progress
# Matches: [download]  12.3% of 45.67MiB at  1.23MiB/s ETA 00:30
# Or: [download]  12.3% of ~45.67MiB at  1.23MiB/s ETA 00:30
YTDLP_PROGRESS_RE = re.compile(r'\[download\]\s+([\d\.]+)%\s+of\s+(?:~\s*)?([^\s]+)\s+at\s+([^\s]+)\s+ETA\s+([^\s]+)')
YTDLP_FINISHED_RE = re.compile(r'\[download\]\s+100%\s+of\s+([^\s]+)\s+in\s+([^\s]+)')

# Regex for parsing aria2c progress
# Matches: [#59c317 11.2MiB/43.6MiB(25%) CN:5 DL:1.2MiB ETA:25s]
ARIA2_PROGRESS_RE = re.compile(r'\[#\w+\s+([^\/]+)\/([^\(]+)\(([\d]+)%\)\s+CN:\d+\s+DL:([^\s]+)\s+ETA:([^\s]+)\]')

class DownloadWorker(QThread):
    progress_updated = pyqtSignal(str, int, str, str, str)  # id, percent, speed, eta, status
    download_completed = pyqtSignal(str, bool, str)        # id, success, error_msg
    log_received = pyqtSignal(str, str)                    # id, log_line

    def __init__(self, download_id, tool_name, tool_path, url, export_dir, profile_settings):
        super().__init__()
        self.download_id = download_id
        self.tool_name = tool_name
        self.tool_path = tool_path
        self.url = url
        self.export_dir = export_dir
        self.settings = profile_settings
        self.process = None
        self._is_cancelled = False

    def run(self):
        try:
            # Build CLI command parameters
            cmd = [self.tool_path]
            
            # Make sure export dir exists
            os.makedirs(self.export_dir, exist_ok=True)
            
            if self.tool_name == "aria2c":
                cmd.append("-d")
                cmd.append(self.export_dir)
                
                # Append connections & split
                connections = self.settings.get("max_connection_per_server", 16)
                split = self.settings.get("split", 16)
                cmd.append(f"-x{connections}")
                cmd.append(f"-s{split}")
                
                # Rate limit
                rate_limit = self.settings.get("max_download_limit", "0")
                if rate_limit and rate_limit != "0":
                    # Append 'K' or 'M' if needed, or if it is already formatted
                    cmd.append(f"--max-download-limit={rate_limit}")
                
                # Add custom flags
                custom_flags = self.settings.get("custom_flags", "")
                if custom_flags:
                    cmd.extend(shlex.split(custom_flags))
                
                # Finally, the URL
                cmd.append(self.url)
                
            elif self.tool_name == "yt-dlp":
                cmd.append("-P")
                cmd.append(self.export_dir)
                
                # Formatting
                fmt = self.settings.get("format", "bestvideo+bestaudio/best")
                cmd.append("-f")
                cmd.append(fmt)
                
                if self.settings.get("extract_audio", False):
                    cmd.append("-x")
                    audio_fmt = self.settings.get("audio_format", "mp3")
                    cmd.append("--audio-format")
                    cmd.append(audio_fmt)
                    audio_q = self.settings.get("audio_quality", "5")
                    cmd.append("--audio-quality")
                    cmd.append(audio_q)
                
                if self.settings.get("merge_output_format"):
                    cmd.append("--merge-output-format")
                    cmd.append(self.settings.get("merge_output_format"))
                    
                if self.settings.get("embed_subs", False):
                    cmd.append("--embed-subs")
                
                # Include local bin folder in PATH so yt-dlp can find ffmpeg automatically
                env = os.environ.copy()
                bin_dir = os.path.dirname(self.tool_path)
                if bin_dir not in env.get("PATH", ""):
                    env["PATH"] = bin_dir + os.pathsep + env.get("PATH", "")
                
                # Custom flags
                custom_flags = self.settings.get("custom_flags", "")
                if custom_flags:
                    cmd.extend(shlex.split(custom_flags))
                
                cmd.append(self.url)
                
            elif self.tool_name == "gallery-dl":
                cmd.append("-d")
                cmd.append(self.export_dir)
                
                # Custom flags
                custom_flags = self.settings.get("custom_flags", "")
                if custom_flags:
                    cmd.extend(shlex.split(custom_flags))
                
                cmd.append(self.url)
                
            else:
                raise ValueError(f"Unsupported tool: {self.tool_name}")

            # Prepare env if needed
            env = os.environ.copy()
            if self.tool_name == "yt-dlp":
                # Ensure yt-dlp can locate ffmpeg
                bin_path = os.path.dirname(self.tool_path)
                env["PATH"] = bin_path + os.pathsep + env.get("PATH", "")

            # Log command line to logs pane
            cmd_str = " ".join([f'"{arg}"' if ' ' in arg else arg for arg in cmd])
            self.log_received.emit(self.download_id, f"Executing command: {cmd_str}\n")

            # Spawn subprocess
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT, # Merge stdout and stderr
                stdin=subprocess.PIPE,    # Sometimes helps to open pipe
                text=True,
                encoding="utf-8",
                errors="replace",
                env=env,
                creationflags=subprocess.CREATE_NO_WINDOW
            )

            # Read output stream line by line
            while True:
                if self._is_cancelled:
                    self.log_received.emit(self.download_id, "\n[INFO] Download cancelled by user.\n")
                    self.terminate_process()
                    self.download_completed.emit(self.download_id, False, "Cancelled")
                    return
                
                line = self.process.stdout.readline()
                if not line:
                    break
                
                clean_line = line.strip()
                if clean_line:
                    self.log_received.emit(self.download_id, line)
                    self.parse_line_progress(clean_line)
            
            # Wait for exit code
            self.process.wait()
            exit_code = self.process.returncode
            
            if self._is_cancelled:
                self.download_completed.emit(self.download_id, False, "Cancelled")
            elif exit_code == 0:
                self.progress_updated.emit(self.download_id, 100, "Done", "0s", "Completed successfully")
                self.download_completed.emit(self.download_id, True, "")
            else:
                self.download_completed.emit(self.download_id, False, f"Process exited with code {exit_code}")

        except Exception as e:
            self.log_received.emit(self.download_id, f"\n[ERROR] Exception occurred: {str(e)}\n")
            self.download_completed.emit(self.download_id, False, str(e))

    def cancel(self):
        self._is_cancelled = True
        self.terminate_process()

    def terminate_process(self):
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=3)
            except Exception:
                try:
                    self.process.kill()
                except Exception:
                    pass

    def parse_line_progress(self, line):
        if self.tool_name == "yt-dlp":
            # Match downloading state
            match = YTDLP_PROGRESS_RE.match(line)
            if match:
                percent = int(float(match.group(1)))
                size = match.group(2)
                speed = match.group(3)
                eta = match.group(4)
                status = f"Downloading ({size})"
                self.progress_updated.emit(self.download_id, percent, speed, eta, status)
                return
            
            # Match 100% finished state
            match_finished = YTDLP_FINISHED_RE.match(line)
            if match_finished:
                size = match_finished.group(1)
                self.progress_updated.emit(self.download_id, 100, "-", "0s", f"Downloaded ({size})")
                return

            # Special status updates like FFmpeg merging
            if "[ffmpeg]" in line.lower() or "merging formats" in line.lower():
                self.progress_updated.emit(self.download_id, 99, "-", "-", "Post-processing (FFmpeg)...")
                return
                
        elif self.tool_name == "aria2c":
            match = ARIA2_PROGRESS_RE.search(line)
            if match:
                # Group 3 is percent, 4 is speed, 5 is ETA
                percent = int(match.group(3))
                speed = match.group(4) + "/s"
                eta = match.group(5)
                downloaded = match.group(1)
                total = match.group(2)
                status = f"Downloading ({downloaded}/{total})"
                self.progress_updated.emit(self.download_id, percent, speed, eta, status)
                return
                
        elif self.tool_name == "gallery-dl":
            # gallery-dl logs filenames being downloaded. We can show it in status.
            if "[gallery-dl][info]" in line or "downloading" in line.lower():
                # Display dynamic status line
                parts = line.split("Downloading")
                filename = parts[-1].strip() if len(parts) > 1 else ""
                status_msg = f"Downloading {filename}" if filename else "Downloading gallery..."
                self.progress_updated.emit(self.download_id, -1, "-", "-", status_msg)
                return
