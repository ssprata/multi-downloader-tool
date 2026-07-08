import os
import uuid
from PyQt6.QtCore import Qt, pyqtSignal, QThread, pyqtSlot
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPlainTextEdit, QPushButton, QListWidget,
    QComboBox, QProgressBar, QTabWidget, QSpinBox, QCheckBox,
    QFileDialog, QMessageBox, QSplitter, QScrollArea, QFrame,
    QSizePolicy, QFormLayout, QGroupBox, QDialog, QTreeWidget, QTreeWidgetItem
)
from PyQt6.QtGui import QColor, QFont

from config_manager import ConfigManager
from dependency_manager import DependencyManager
from downloader import DownloadWorker

class CyberMessageBox(QDialog):
    def __init__(self, title, message, is_confirm=False, border_color="#ff007f", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        
        self.setObjectName("card_frame")
        self.setStyleSheet(f"""
            QDialog#card_frame {{
                background-color: #12131c;
                border: 2px solid {border_color};
                border-radius: 8px;
            }}
        """)
        self.setup_ui(title, message, is_confirm, border_color)

    def setup_ui(self, title, message, is_confirm, border_color):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)

        title_lbl = QLabel(title.upper())
        title_lbl.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {border_color}; letter-spacing: 1px;")
        title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_lbl)

        msg_lbl = QLabel(message)
        msg_lbl.setStyleSheet("font-size: 13px; color: #e2e8f0;")
        msg_lbl.setWordWrap(True)
        msg_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(msg_lbl)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)

        if is_confirm:
            yes_btn = QPushButton("CONFIRM")
            yes_btn.setObjectName("neon_cyan_btn")
            yes_btn.clicked.connect(self.accept)
            
            no_btn = QPushButton("CANCEL")
            no_btn.setObjectName("neon_magenta_btn")
            no_btn.clicked.connect(self.reject)
            
            btn_layout.addStretch()
            btn_layout.addWidget(yes_btn)
            btn_layout.addWidget(no_btn)
            btn_layout.addStretch()
        else:
            ok_btn = QPushButton("ACKNOWLEDGE")
            if border_color == "#00f0ff":
                ok_btn.setObjectName("neon_cyan_btn")
            else:
                ok_btn.setObjectName("neon_magenta_btn")
            ok_btn.setFixedWidth(140)
            ok_btn.clicked.connect(self.accept)
            
            btn_layout.addStretch()
            btn_layout.addWidget(ok_btn)
            btn_layout.addStretch()

        layout.addLayout(btn_layout)

    @staticmethod
    def show_info(parent, title, message, border_color="#00f0ff"):
        dialog = CyberMessageBox(title, message, is_confirm=False, border_color=border_color, parent=parent)
        if parent:
            dialog.adjustSize()
            geom = parent.geometry()
            x = geom.x() + (geom.width() - dialog.width()) // 2
            y = geom.y() + (geom.height() - dialog.height()) // 2
            dialog.move(x, y)
        dialog.exec()

    @staticmethod
    def show_question(parent, title, message, border_color="#ff007f"):
        dialog = CyberMessageBox(title, message, is_confirm=True, border_color=border_color, parent=parent)
        if parent:
            dialog.adjustSize()
            geom = parent.geometry()
            x = geom.x() + (geom.width() - dialog.width()) // 2
            y = geom.y() + (geom.height() - dialog.height()) // 2
            dialog.move(x, y)
        return dialog.exec() == QDialog.DialogCode.Accepted


# Worker to download tools in background
class ToolDownloadWorker(QThread):
    progress_updated = pyqtSignal(str, float)  # tool_name, percentage
    completed = pyqtSignal(str, bool, str)     # tool_name, success, error_msg

    def __init__(self, dep_manager, tool_name):
        super().__init__()
        self.dep_manager = dep_manager
        self.tool_name = tool_name

    def run(self):
        try:
            def cb(percent):
                self.progress_updated.emit(self.tool_name, percent)
            self.dep_manager.download_tool(self.tool_name, cb)
            self.completed.emit(self.tool_name, True, "")
        except Exception as e:
            self.completed.emit(self.tool_name, False, str(e))


# Custom UI Widget for individual active download progress
class DownloadProgressWidget(QFrame):
    cancelled = pyqtSignal(str) # download_id

    def __init__(self, download_id, url, parent=None):
        super().__init__(parent)
        self.download_id = download_id
        self.url = url
        self.setObjectName("card_frame")
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(6)

        # URL and Close row
        top_row = QHBoxLayout()
        # Limit URL label length for UI integrity
        display_url = self.url
        if len(display_url) > 60:
            display_url = display_url[:57] + "..."
        
        self.url_label = QLabel(display_url)
        self.url_label.setStyleSheet("font-weight: bold; color: #00f0ff;")
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setObjectName("neon_magenta_btn")
        self.cancel_btn.setFixedWidth(80)
        self.cancel_btn.clicked.connect(self.on_cancel_clicked)

        top_row.addWidget(self.url_label)
        top_row.addStretch()
        top_row.addWidget(self.cancel_btn)
        layout.addLayout(top_row)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(12)
        layout.addWidget(self.progress_bar)

        # Status row (Speed, ETA, Percent)
        status_row = QHBoxLayout()
        self.status_label = QLabel("Waiting...")
        self.status_label.setStyleSheet("color: #a0a5c0;")
        
        self.metrics_label = QLabel("- | ETA: -")
        self.metrics_label.setStyleSheet("color: #ff007f;")

        status_row.addWidget(self.status_label)
        status_row.addStretch()
        status_row.addWidget(self.metrics_label)
        layout.addLayout(status_row)

    def update_progress(self, percent, speed, eta, status):
        if percent >= 0:
            self.progress_bar.setValue(percent)
            if percent == 100:
                self.progress_bar.setFormat("100% (Done)")
        else:
            # Indeterminate state for tools like gallery-dl
            self.progress_bar.setMinimum(0)
            self.progress_bar.setMaximum(0)
            self.progress_bar.setFormat("")
        
        self.status_label.setText(status)
        if speed == "-" and eta == "-":
            self.metrics_label.setText("")
        else:
            self.metrics_label.setText(f"{speed} | ETA: {eta}")

    def set_error(self, error_msg):
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("""
            QProgressBar::chunk { background-color: #ff3b30; }
        """)
        self.status_label.setText(f"Error: {error_msg}")
        self.status_label.setStyleSheet("color: #ff3b30;")
        self.metrics_label.setText("")
        self.cancel_btn.setText("Remove")
        # Disconnect and change connection to remove
        self.cancel_btn.clicked.disconnect()
        self.cancel_btn.clicked.connect(self.on_remove_clicked)

    def set_completed(self):
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(100)
        self.status_label.setText("Completed")
        self.status_label.setStyleSheet("color: #00f0ff;")
        self.metrics_label.setText("")
        self.cancel_btn.setText("Clear")
        self.cancel_btn.clicked.disconnect()
        self.cancel_btn.clicked.connect(self.on_remove_clicked)

    def on_cancel_clicked(self):
        self.cancelled.emit(self.download_id)

    def on_remove_clicked(self):
        self.setParent(None)
        self.deleteLater()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cyberpunk Multi-Downloader")
        self.resize(1100, 750)
        self.setMinimumSize(950, 650)

        # Managers
        self.config_manager = ConfigManager()
        self.dep_manager = DependencyManager()

        # Trackers
        self.active_workers = {}
        self.tool_download_workers = {}

        # Build UI
        self.setup_ui()
        self.load_profiles()
        
        # Check initial engines status
        self.refresh_tools_status()

    def setup_ui(self):
        # Central widget and layouts
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Splitter to separate sidebar and content
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)

        # ----------------- SIDEBAR -----------------
        sidebar = QFrame()
        sidebar.setObjectName("sidebar_frame")
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(15, 20, 15, 20)
        sidebar_layout.setSpacing(15)

        # Title Label
        title_lbl = QLabel("SYNTH\nDOWNLOADER")
        title_lbl.setObjectName("title_label")
        title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(title_lbl)

        # Profile selection label
        profiles_lbl = QLabel("PROFILES")
        profiles_lbl.setObjectName("section_title")
        sidebar_layout.addWidget(profiles_lbl)

        # Profiles Tree List
        self.profiles_list = QTreeWidget()
        self.profiles_list.setHeaderHidden(True)
        self.profiles_list.itemClicked.connect(self.on_profile_item_clicked)
        self.expanded_folders = set()
        self.profiles_list.itemExpanded.connect(self.on_folder_expanded)
        self.profiles_list.itemCollapsed.connect(self.on_folder_collapsed)
        sidebar_layout.addWidget(self.profiles_list)

        # Profile buttons row
        prof_btn_row = QHBoxLayout()
        self.add_profile_btn = QPushButton("+ New")
        self.add_profile_btn.setObjectName("neon_cyan_btn")
        self.add_profile_btn.clicked.connect(self.on_add_profile)
        
        self.delete_profile_btn = QPushButton("- Delete")
        self.delete_profile_btn.setObjectName("neon_magenta_btn")
        self.delete_profile_btn.clicked.connect(self.on_delete_profile)
        
        prof_btn_row.addWidget(self.add_profile_btn)
        prof_btn_row.addWidget(self.delete_profile_btn)
        sidebar_layout.addLayout(prof_btn_row)

        # Profile details group
        self.profile_details_frame = QFrame()
        self.profile_details_frame.setObjectName("card_frame")
        details_layout = QVBoxLayout(self.profile_details_frame)
        details_layout.setContentsMargins(10, 10, 10, 10)
        details_layout.setSpacing(10)

        details_title = QLabel("Profile Settings")
        details_title.setStyleSheet("font-weight: bold; color: #9d4edd;")
        details_layout.addWidget(details_title)

        form_layout = QFormLayout()
        form_layout.setSpacing(8)

        self.prof_name_input = QLineEdit()
        form_layout.addRow("Name:", self.prof_name_input)

        self.prof_folder_input = QComboBox()
        self.prof_folder_input.setEditable(True)
        form_layout.addRow("Folder:", self.prof_folder_input)

        self.prof_tool_combo = QComboBox()
        self.prof_tool_combo.addItems(["aria2c", "yt-dlp", "gallery-dl"])
        self.prof_tool_combo.currentTextChanged.connect(self.on_tool_combo_changed)
        form_layout.addRow("Tool:", self.prof_tool_combo)

        # Directory selector layout
        dir_layout = QHBoxLayout()
        self.prof_dir_input = QLineEdit()
        self.prof_dir_btn = QPushButton("Browse")
        self.prof_dir_btn.setFixedWidth(65)
        self.prof_dir_btn.clicked.connect(self.on_browse_directory)
        dir_layout.addWidget(self.prof_dir_input)
        dir_layout.addWidget(self.prof_dir_btn)
        form_layout.addRow("Export:", dir_layout)

        details_layout.addLayout(form_layout)

        self.save_profile_btn = QPushButton("Save Settings")
        self.save_profile_btn.setObjectName("neon_cyan_btn")
        self.save_profile_btn.clicked.connect(self.on_save_profile_settings)
        details_layout.addWidget(self.save_profile_btn)

        sidebar_layout.addWidget(self.profile_details_frame)
        splitter.addWidget(sidebar)

        # ----------------- MAIN PANEL -----------------
        main_content = QWidget()
        content_layout = QVBoxLayout(main_content)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(15)

        # Input: URL Text Area & Logs Toggle
        url_header_layout = QHBoxLayout()
        url_lbl = QLabel("URLs (One per line for batch processing):")
        url_lbl.setObjectName("header_label")
        url_header_layout.addWidget(url_lbl)
        
        url_header_layout.addStretch()
        
        # Logs toggle button
        self.logs_toggle_btn = QPushButton("📜 Hide Logs")
        self.logs_toggle_btn.setCheckable(True)
        self.logs_toggle_btn.setChecked(True)  # Checked by default (Logs visible)
        self.logs_toggle_btn.setObjectName("neon_cyan_btn")
        self.logs_toggle_btn.setFixedWidth(120)
        self.logs_toggle_btn.toggled.connect(self.toggle_logs)
        url_header_layout.addWidget(self.logs_toggle_btn)
        
        content_layout.addLayout(url_header_layout)

        self.urls_input = QPlainTextEdit()
        self.urls_input.setPlaceholderText("https://youtube.com/watch?v=...\nhttps://example.com/file.zip\n...")
        self.urls_input.setMaximumHeight(120)
        content_layout.addWidget(self.urls_input)

        # Configuration Tabs based on tools + tool downloader
        self.config_tabs = QTabWidget()
        
        # Tab 1: aria2c options
        self.aria_tab = QWidget()
        aria_layout = QGridLayout(self.aria_tab)
        aria_layout.setContentsMargins(15, 15, 15, 15)
        aria_layout.setSpacing(10)

        aria_layout.addWidget(QLabel("Max Connections:"), 0, 0)
        self.aria_conn_spin = QSpinBox()
        self.aria_conn_spin.setRange(1, 16)
        self.aria_conn_spin.setValue(16)
        aria_layout.addWidget(self.aria_conn_spin, 0, 1)

        aria_layout.addWidget(QLabel("Split Parts:"), 0, 2)
        self.aria_split_spin = QSpinBox()
        self.aria_split_spin.setRange(1, 16)
        self.aria_split_spin.setValue(16)
        aria_layout.addWidget(self.aria_split_spin, 0, 3)

        aria_layout.addWidget(QLabel("Max Download Speed (e.g. 5M, 500K, 0 for unlimited):"), 1, 0)
        self.aria_speed_input = QLineEdit("0")
        aria_layout.addWidget(self.aria_speed_input, 1, 1, 1, 3)

        aria_layout.addWidget(QLabel("Custom Flags:"), 2, 0)
        self.aria_flags_input = QLineEdit()
        self.aria_flags_input.setPlaceholderText("--header=\"Authorization: Bearer X\" --header=\"...\"")
        aria_layout.addWidget(self.aria_flags_input, 2, 1, 1, 3)
        self.config_tabs.addTab(self.aria_tab, "aria2c Settings")

        # Tab 2: yt-dlp options
        self.ytdlp_tab = QWidget()
        ytdlp_layout = QGridLayout(self.ytdlp_tab)
        ytdlp_layout.setContentsMargins(15, 15, 15, 15)
        ytdlp_layout.setSpacing(10)

        ytdlp_layout.addWidget(QLabel("Quality Format:"), 0, 0)
        self.ytdlp_fmt_combo = QComboBox()
        self.ytdlp_fmt_combo.addItems([
            "bestvideo+bestaudio/best (Best Quality)",
            "bestvideo[height<=1080]+bestaudio/best (FHD 1080p)",
            "bestvideo[height<=720]+bestaudio/best (HD 720p)",
            "bestaudio/best (Audio Only)"
        ])
        ytdlp_layout.addWidget(self.ytdlp_fmt_combo, 0, 1, 1, 3)

        self.ytdlp_audio_cb = QCheckBox("Extract Audio Only")
        self.ytdlp_audio_cb.toggled.connect(self.on_ytdlp_audio_toggled)
        ytdlp_layout.addWidget(self.ytdlp_audio_cb, 1, 0, 1, 2)

        ytdlp_layout.addWidget(QLabel("Audio Format:"), 2, 0)
        self.ytdlp_audio_fmt = QComboBox()
        self.ytdlp_audio_fmt.addItems(["mp3", "m4a", "flac", "opus", "wav"])
        self.ytdlp_audio_fmt.setEnabled(False)
        ytdlp_layout.addWidget(self.ytdlp_audio_fmt, 2, 1)

        ytdlp_layout.addWidget(QLabel("Audio Quality (0-9, 0 is best):"), 2, 2)
        self.ytdlp_audio_q = QSpinBox()
        self.ytdlp_audio_q.setRange(0, 9)
        self.ytdlp_audio_q.setValue(5)
        self.ytdlp_audio_q.setEnabled(False)
        ytdlp_layout.addWidget(self.ytdlp_audio_q, 2, 3)

        self.ytdlp_subs_cb = QCheckBox("Embed Subtitles (when available)")
        self.ytdlp_subs_cb.setChecked(True)
        ytdlp_layout.addWidget(self.ytdlp_subs_cb, 3, 0, 1, 4)

        ytdlp_layout.addWidget(QLabel("Custom Flags:"), 4, 0)
        self.ytdlp_flags_input = QLineEdit()
        self.ytdlp_flags_input.setPlaceholderText("--write-thumbnail --playlist-items 1-5")
        ytdlp_layout.addWidget(self.ytdlp_flags_input, 4, 1, 1, 3)
        self.config_tabs.addTab(self.ytdlp_tab, "yt-dlp Settings")

        # Tab 3: gallery-dl options
        self.gallerydl_tab = QWidget()
        gallery_layout = QGridLayout(self.gallerydl_tab)
        gallery_layout.setContentsMargins(15, 15, 15, 15)
        gallery_layout.setSpacing(10)

        gallery_layout.addWidget(QLabel("Custom Flags:"), 0, 0)
        self.gallerydl_flags_input = QLineEdit()
        self.gallerydl_flags_input.setPlaceholderText("--range 1-10 --chapters")
        gallery_layout.addWidget(self.gallerydl_flags_input, 0, 1, 1, 3)
        
        # Explanatory tip
        tip_lbl = QLabel("gallery-dl is used for downloading image galleries from sites like Imgur, Reddit, Pixiv, etc.")
        tip_lbl.setStyleSheet("color: #a0a5c0; font-style: italic;")
        gallery_layout.addWidget(tip_lbl, 1, 0, 1, 4)
        
        self.config_tabs.addTab(self.gallerydl_tab, "gallery-dl Settings")

        # Tab 4: Engine Setup / Optional Tools Manager
        self.tools_tab = QWidget()
        tools_layout = QVBoxLayout(self.tools_tab)
        tools_layout.setContentsMargins(15, 15, 15, 15)
        tools_layout.setSpacing(12)

        tools_desc = QLabel("Engine Tool Status & Downloader")
        tools_desc.setStyleSheet("font-weight: bold; color: #ff007f;")
        tools_layout.addWidget(tools_desc)

        # Core Tools Group
        core_group = QGroupBox("Core Required Tools")
        core_group_layout = QGridLayout(core_group)
        core_group_layout.setSpacing(10)

        core_group_layout.addWidget(QLabel("aria2c (Direct downloads):"), 0, 0)
        self.aria_status_lbl = QLabel("Checking...")
        core_group_layout.addWidget(self.aria_status_lbl, 0, 1)
        self.aria_download_btn = QPushButton("Download & Update")
        self.aria_download_btn.clicked.connect(lambda: self.download_binary("aria2c"))
        core_group_layout.addWidget(self.aria_download_btn, 0, 2)

        core_group_layout.addWidget(QLabel("yt-dlp (YouTube & video engine):"), 1, 0)
        self.ytdlp_status_lbl = QLabel("Checking...")
        core_group_layout.addWidget(self.ytdlp_status_lbl, 1, 1)
        self.ytdlp_download_btn = QPushButton("Download & Update")
        self.ytdlp_download_btn.clicked.connect(lambda: self.download_binary("yt-dlp"))
        core_group_layout.addWidget(self.ytdlp_download_btn, 1, 2)

        tools_layout.addWidget(core_group)

        # Optional Tools Group
        opt_group = QGroupBox("Optional Tools")
        opt_group_layout = QGridLayout(opt_group)
        opt_group_layout.setSpacing(10)

        opt_group_layout.addWidget(QLabel("FFmpeg (Merges HD videos & extracts audio in yt-dlp):"), 0, 0)
        self.ffmpeg_status_lbl = QLabel("Checking...")
        opt_group_layout.addWidget(self.ffmpeg_status_lbl, 0, 1)
        self.ffmpeg_download_btn = QPushButton("Download & Install")
        self.ffmpeg_download_btn.clicked.connect(lambda: self.download_binary("ffmpeg"))
        opt_group_layout.addWidget(self.ffmpeg_download_btn, 0, 2)

        opt_group_layout.addWidget(QLabel("gallery-dl (Image & Gallery downloader):"), 1, 0)
        self.gallerydl_status_lbl = QLabel("Checking...")
        opt_group_layout.addWidget(self.gallerydl_status_lbl, 1, 1)
        self.gallerydl_download_btn = QPushButton("Download & Install")
        self.gallerydl_download_btn.clicked.connect(lambda: self.download_binary("gallery-dl"))
        opt_group_layout.addWidget(self.gallerydl_download_btn, 1, 2)

        tools_layout.addWidget(opt_group)
        
        # Tool download progress bar inside settings
        self.tool_progress_lbl = QLabel("")
        self.tool_progress_lbl.setStyleSheet("color: #00f0ff;")
        self.tool_progress_bar = QProgressBar()
        self.tool_progress_bar.setVisible(False)
        tools_layout.addWidget(self.tool_progress_lbl)
        tools_layout.addWidget(self.tool_progress_bar)

        tools_layout.addStretch()
        self.config_tabs.addTab(self.tools_tab, "Engines & Tools")

        content_layout.addWidget(self.config_tabs)

        # Big Download Button
        self.download_btn = QPushButton("ENGAGE DOWNLOAD")
        self.download_btn.setObjectName("download_btn")
        self.download_btn.clicked.connect(self.start_download_batch)
        content_layout.addWidget(self.download_btn)

        # Bottom Panel Splitter (Active Queue & Logs)
        bottom_splitter = QSplitter(Qt.Orientation.Vertical)
        content_layout.addWidget(bottom_splitter, 1) # Set stretch to 1

        # Queue panel
        queue_widget = QWidget()
        queue_layout = QVBoxLayout(queue_widget)
        queue_layout.setContentsMargins(0, 0, 0, 0)
        
        queue_header_layout = QHBoxLayout()
        queue_lbl = QLabel("ACTIVE DOWNLOADS QUEUE")
        queue_lbl.setStyleSheet("font-weight: bold; color: #ff007f;")
        
        clear_queue_btn = QPushButton("Clear Completed")
        clear_queue_btn.setFixedWidth(120)
        clear_queue_btn.clicked.connect(self.clear_completed_downloads)
        
        queue_header_layout.addWidget(queue_lbl)
        queue_header_layout.addStretch()
        queue_header_layout.addWidget(clear_queue_btn)
        queue_layout.addLayout(queue_header_layout)

        # Scroll Area for download progress widgets
        self.queue_scroll = QScrollArea()
        self.queue_scroll.setWidgetResizable(True)
        self.queue_scroll_content = QWidget()
        self.queue_list_layout = QVBoxLayout(self.queue_scroll_content)
        self.queue_list_layout.setContentsMargins(5, 5, 5, 5)
        self.queue_list_layout.setSpacing(8)
        self.queue_list_layout.addStretch() # Push items to top
        self.queue_scroll.setWidget(self.queue_scroll_content)
        
        queue_layout.addWidget(self.queue_scroll)
        bottom_splitter.addWidget(queue_widget)

        # Logs panel
        self.logs_widget = QWidget()
        logs_layout = QVBoxLayout(self.logs_widget)
        logs_layout.setContentsMargins(0, 0, 0, 0)
        
        logs_lbl_row = QHBoxLayout()
        logs_lbl = QLabel("ENGINE EXECUTION LOGS")
        logs_lbl.setStyleSheet("font-weight: bold; color: #00f0ff;")
        
        self.clear_logs_btn = QPushButton("Clear Logs")
        self.clear_logs_btn.setFixedWidth(100)
        self.clear_logs_btn.clicked.connect(self.clear_logs)
        
        logs_lbl_row.addWidget(logs_lbl)
        logs_lbl_row.addStretch()
        logs_lbl_row.addWidget(self.clear_logs_btn)
        logs_layout.addLayout(logs_lbl_row)

        self.logs_console = QPlainTextEdit()
        self.logs_console.setObjectName("logs_console")
        self.logs_console.setReadOnly(True)
        self.logs_console.setPlaceholderText("Subprocess standard outputs will stream here...")
        logs_layout.addWidget(self.logs_console)

        bottom_splitter.addWidget(self.logs_widget)
        
        # Set splitter sizes
        bottom_splitter.setSizes([200, 150])

        splitter.addWidget(main_content)
        splitter.setSizes([300, 800])

    # ----------------- PROFILES logic -----------------
    def load_profiles(self):
        self.profiles_list.blockSignals(True)
        self.profiles_list.clear()
        
        profiles = self.config_manager.get_profiles()
        active_name = self.config_manager.get_active_profile_name()
        
        root_profiles = []
        folder_groups = {}
        
        for p in profiles:
            folder = p.get("folder", "")
            if not folder:
                root_profiles.append(p)
            else:
                if folder not in folder_groups:
                    folder_groups[folder] = []
                folder_groups[folder].append(p)
        
        active_item = None
        
        # Add folders first
        for folder_name, folder_profs in sorted(folder_groups.items()):
            folder_item = QTreeWidgetItem(self.profiles_list)
            folder_item.setText(0, f"📁 {folder_name}")
            folder_item.setData(0, Qt.ItemDataRole.UserRole, "folder")
            folder_item.setData(0, Qt.ItemDataRole.UserRole + 1, folder_name)
            
            # Check if this folder was previously expanded
            if folder_name in self.expanded_folders:
                folder_item.setExpanded(True)
            
            for p in folder_profs:
                child_item = QTreeWidgetItem(folder_item)
                child_item.setText(0, f"📄 {p['name']}")
                child_item.setData(0, Qt.ItemDataRole.UserRole, "profile")
                child_item.setData(0, Qt.ItemDataRole.UserRole + 1, p["name"])
                
                if p["name"] == active_name:
                    active_item = child_item
                    
        # Add root profiles
        for p in root_profiles:
            root_item = QTreeWidgetItem(self.profiles_list)
            root_item.setText(0, f"📄 {p['name']}")
            root_item.setData(0, Qt.ItemDataRole.UserRole, "profile")
            root_item.setData(0, Qt.ItemDataRole.UserRole + 1, p["name"])
            
            if p["name"] == active_name:
                active_item = root_item
                
        if active_item:
            self.profiles_list.setCurrentItem(active_item)
            parent = active_item.parent()
            if parent:
                parent.setExpanded(True)
                self.expanded_folders.add(parent.data(0, Qt.ItemDataRole.UserRole + 1))
                
        self.profiles_list.blockSignals(False)
        self.display_active_profile_details()

    def update_folder_combobox(self):
        self.prof_folder_input.blockSignals(True)
        self.prof_folder_input.clear()
        self.prof_folder_input.addItem("") # None/Root
        
        folders = set()
        for p in self.config_manager.get_profiles():
            f = p.get("folder", "")
            if f:
                folders.add(f)
                
        for f in sorted(folders):
            self.prof_folder_input.addItem(f)
            
        self.prof_folder_input.blockSignals(False)

    def display_active_profile_details(self):
        active_prof = self.config_manager.get_active_profile()
        if not active_prof:
            return

        self.prof_name_input.setText(active_prof["name"])
        
        # Populate and select the current folder
        self.update_folder_combobox()
        self.prof_folder_input.setCurrentText(active_prof.get("folder", ""))
        
        self.prof_tool_combo.setCurrentText(active_prof["tool"])
        self.prof_dir_input.setText(active_prof["export_dir"])

        # Switch tab index to match selected tool for convenience
        tool = active_prof["tool"]
        if tool == "aria2c":
            self.config_tabs.setCurrentIndex(0)
            # Load specific aria settings
            aria_s = active_prof.get("aria2_settings", {})
            self.aria_conn_spin.setValue(aria_s.get("max_connection_per_server", 16))
            self.aria_split_spin.setValue(aria_s.get("split", 16))
            self.aria_speed_input.setText(aria_s.get("max_download_limit", "0"))
            self.aria_flags_input.setText(aria_s.get("custom_flags", ""))
        elif tool == "yt-dlp":
            self.config_tabs.setCurrentIndex(1)
            # Load specific ytdlp settings
            ytdlp_s = active_prof.get("ytdlp_settings", {})
            fmt = ytdlp_s.get("format", "bestvideo+bestaudio/best")
            
            # Match combo box index
            idx = 0
            for i in range(self.ytdlp_fmt_combo.count()):
                if self.ytdlp_fmt_combo.itemText(i).startswith(fmt):
                    idx = i
                    break
            self.ytdlp_fmt_combo.setCurrentIndex(idx)
            
            self.ytdlp_audio_cb.setChecked(ytdlp_s.get("extract_audio", False))
            self.ytdlp_audio_fmt.setCurrentText(ytdlp_s.get("audio_format", "mp3"))
            self.ytdlp_audio_q.setValue(int(ytdlp_s.get("audio_quality", 5)))
            self.ytdlp_subs_cb.setChecked(ytdlp_s.get("embed_subs", True))
            self.ytdlp_flags_input.setText(ytdlp_s.get("custom_flags", ""))
        elif tool == "gallery-dl":
            self.config_tabs.setCurrentIndex(2)
            gdl_s = active_prof.get("gallerydl_settings", {})
            self.gallerydl_flags_input.setText(gdl_s.get("custom_flags", ""))

    def on_profile_item_clicked(self, item, column):
        role = item.data(0, Qt.ItemDataRole.UserRole)
        if role == "profile":
            profile_name = item.data(0, Qt.ItemDataRole.UserRole + 1)
            self.config_manager.set_active_profile(profile_name)
            self.display_active_profile_details()

    def on_folder_expanded(self, item):
        role = item.data(0, Qt.ItemDataRole.UserRole)
        if role == "folder":
            folder_name = item.data(0, Qt.ItemDataRole.UserRole + 1)
            self.expanded_folders.add(folder_name)

    def on_folder_collapsed(self, item):
        role = item.data(0, Qt.ItemDataRole.UserRole)
        if role == "folder":
            folder_name = item.data(0, Qt.ItemDataRole.UserRole + 1)
            self.expanded_folders.discard(folder_name)

    def on_add_profile(self):
        # Auto-detect folder to group new profile under
        default_folder = ""
        curr_item = self.profiles_list.currentItem()
        if curr_item:
            role = curr_item.data(0, Qt.ItemDataRole.UserRole)
            if role == "folder":
                default_folder = curr_item.data(0, Qt.ItemDataRole.UserRole + 1)
            elif role == "profile":
                parent = curr_item.parent()
                if parent:
                    default_folder = parent.data(0, Qt.ItemDataRole.UserRole + 1)

        # Generate a unique profile name
        profiles = self.config_manager.get_profiles()
        idx = 1
        name = f"Custom Profile {idx}"
        existing_names = [p["name"] for p in profiles]
        while name in existing_names:
            idx += 1
            name = f"Custom Profile {idx}"

        new_profile = {
            "name": name,
            "tool": "aria2c",
            "folder": default_folder,
            "export_dir": os.path.expanduser("~/Downloads"),
            "aria2_settings": {
                "max_connection_per_server": 8,
                "split": 8,
                "max_download_limit": "0",
                "custom_flags": ""
            },
            "ytdlp_settings": {
                "format": "bestvideo+bestaudio/best",
                "extract_audio": False,
                "embed_subs": True,
                "custom_flags": ""
            },
            "gallerydl_settings": {
                "custom_flags": ""
            }
        }
        
        self.config_manager.add_profile(new_profile)
        self.config_manager.set_active_profile(name)
        self.load_profiles()

    def on_delete_profile(self):
        curr_item = self.profiles_list.currentItem()
        if not curr_item:
            return

        role = curr_item.data(0, Qt.ItemDataRole.UserRole)
        if role == "folder":
            folder_name = curr_item.data(0, Qt.ItemDataRole.UserRole + 1)
            profs_in_folder = [p for p in self.config_manager.get_profiles() if p.get("folder", "") == folder_name]
            
            reply = CyberMessageBox.show_question(
                self, "Confirm Delete Folder",
                f"Are you sure you want to delete folder '{folder_name}' and all of its {len(profs_in_folder)} profiles?"
            )
            if reply:
                for p in profs_in_folder:
                    self.config_manager.delete_profile(p["name"])
                self.load_profiles()
        elif role == "profile":
            current_name = curr_item.data(0, Qt.ItemDataRole.UserRole + 1)
            
            if len(self.config_manager.get_profiles()) <= 1:
                CyberMessageBox.show_info(self, "Cannot Delete", "You must keep at least one profile.", border_color="#ff007f")
                return

            reply = CyberMessageBox.show_question(
                self, "Confirm Delete",
                f"Are you sure you want to delete profile '{current_name}'?"
            )
            
            if reply:
                self.config_manager.delete_profile(current_name)
                self.load_profiles()

    def on_browse_directory(self):
        current_dir = self.prof_dir_input.text()
        if not os.path.exists(current_dir):
            current_dir = os.path.expanduser("~")
            
        selected_dir = QFileDialog.getExistingDirectory(
            self, "Select Download Export Folder", current_dir
        )
        if selected_dir:
            self.prof_dir_input.setText(selected_dir.replace("/", "\\"))

    def on_tool_combo_changed(self, tool_name):
        # Auto-switch settings tabs based on tool choice
        if tool_name == "aria2c":
            self.config_tabs.setCurrentIndex(0)
        elif tool_name == "yt-dlp":
            self.config_tabs.setCurrentIndex(1)
        elif tool_name == "gallery-dl":
            self.config_tabs.setCurrentIndex(2)

    def on_ytdlp_audio_toggled(self, checked):
        self.ytdlp_audio_fmt.setEnabled(checked)
        self.ytdlp_audio_q.setEnabled(checked)

    def on_save_profile_settings(self):
        active_name = self.config_manager.get_active_profile_name()
        if not active_name:
            return

        new_name = self.prof_name_input.text().strip()
        if not new_name:
            CyberMessageBox.show_info(self, "Invalid Name", "Profile name cannot be empty.", border_color="#ff007f")
            return

        # Ensure name uniqueness if name changed
        if new_name != active_name:
            existing = [p["name"] for p in self.config_manager.get_profiles() if p["name"] != active_name]
            if new_name in existing:
                CyberMessageBox.show_info(self, "Duplicate Name", f"A profile named '{new_name}' already exists.", border_color="#ff007f")
                return

        tool = self.prof_tool_combo.currentText()
        folder = self.prof_folder_input.currentText().strip()
        export_dir = self.prof_dir_input.text().strip()

        # Update specific dictionary settings based on UI configuration
        aria_settings = {
            "max_connection_per_server": self.aria_conn_spin.value(),
            "split": self.aria_split_spin.value(),
            "max_download_limit": self.aria_speed_input.text().strip(),
            "custom_flags": self.aria_flags_input.text().strip()
        }

        # Format mapping
        fmt_text = self.ytdlp_fmt_combo.currentText()
        # Extract format part before space
        fmt = fmt_text.split(" ")[0]

        ytdlp_settings = {
            "format": fmt,
            "extract_audio": self.ytdlp_audio_cb.isChecked(),
            "audio_format": self.ytdlp_audio_fmt.currentText(),
            "audio_quality": str(self.ytdlp_audio_q.value()),
            "embed_subs": self.ytdlp_subs_cb.isChecked(),
            "custom_flags": self.ytdlp_flags_input.text().strip()
        }

        gallerydl_settings = {
            "custom_flags": self.gallerydl_flags_input.text().strip()
        }

        updated_profile = {
            "name": new_name,
            "tool": tool,
            "folder": folder,
            "export_dir": export_dir,
            "aria2_settings": aria_settings,
            "ytdlp_settings": ytdlp_settings,
            "gallerydl_settings": gallerydl_settings
        }

        self.config_manager.update_profile(active_name, updated_profile)
        self.load_profiles()
        CyberMessageBox.show_info(self, "Settings Saved", f"Profile '{new_name}' settings saved successfully.", border_color="#00f0ff")

    # ----------------- TOOL DOWNLOADER logic -----------------
    def refresh_tools_status(self):
        tools = ["aria2c", "yt-dlp", "ffmpeg", "gallery-dl"]
        labels = {
            "aria2c": self.aria_status_lbl,
            "yt-dlp": self.ytdlp_status_lbl,
            "ffmpeg": self.ffmpeg_status_lbl,
            "gallery-dl": self.gallerydl_status_lbl
        }
        buttons = {
            "aria2c": self.aria_download_btn,
            "yt-dlp": self.ytdlp_download_btn,
            "ffmpeg": self.ffmpeg_download_btn,
            "gallery-dl": self.gallerydl_download_btn
        }

        for t in tools:
            is_ins = self.dep_manager.is_installed(t)
            lbl = labels[t]
            btn = buttons[t]

            if is_ins:
                lbl.setText("Installed")
                lbl.setStyleSheet("color: #00f0ff; font-weight: bold;")
                btn.setText("Redownload")
            else:
                lbl.setText("Missing")
                lbl.setStyleSheet("color: #ff007f; font-weight: bold;")
                btn.setText("Download & Install")

    def download_binary(self, tool_name):
        if tool_name in self.tool_download_workers:
            CyberMessageBox.show_info(self, "Downloading", f"Already downloading {tool_name}.", border_color="#ff007f")
            return

        # Disable button
        self.aria_download_btn.setEnabled(False)
        self.ytdlp_download_btn.setEnabled(False)
        self.ffmpeg_download_btn.setEnabled(False)
        self.gallerydl_download_btn.setEnabled(False)

        self.tool_progress_bar.setValue(0)
        self.tool_progress_bar.setVisible(True)
        self.tool_progress_lbl.setText(f"Initializing download for {tool_name}...")

        worker = ToolDownloadWorker(self.dep_manager, tool_name)
        worker.progress_updated.connect(self.on_tool_download_progress)
        worker.completed.connect(self.on_tool_download_completed)
        
        self.tool_download_workers[tool_name] = worker
        worker.start()

    @pyqtSlot(str, float)
    def on_tool_download_progress(self, tool_name, percentage):
        self.tool_progress_bar.setValue(int(percentage))
        self.tool_progress_lbl.setText(f"Downloading {tool_name}: {percentage:.1f}%")

    @pyqtSlot(str, bool, str)
    def on_tool_download_completed(self, tool_name, success, error_msg):
        # Enable buttons
        self.aria_download_btn.setEnabled(True)
        self.ytdlp_download_btn.setEnabled(True)
        self.ffmpeg_download_btn.setEnabled(True)
        self.gallerydl_download_btn.setEnabled(True)

        self.tool_progress_bar.setVisible(False)
        self.tool_progress_lbl.setText("")

        # Cleanup worker
        if tool_name in self.tool_download_workers:
            worker = self.tool_download_workers.pop(tool_name)
            worker.quit()
            worker.wait()

        if success:
            CyberMessageBox.show_info(self, "Install Completed", f"Successfully installed/updated {tool_name}.", border_color="#00f0ff")
        else:
            CyberMessageBox.show_info(self, "Install Failed", f"Failed to install {tool_name}:\n{error_msg}", border_color="#ff007f")

        self.refresh_tools_status()

    # ----------------- DOWNLOAD EXECUTION logic -----------------
    def start_download_batch(self):
        active_prof = self.config_manager.get_active_profile()
        if not active_prof:
            CyberMessageBox.show_info(self, "No Profile", "Please select a download profile first.", border_color="#ff007f")
            return

        tool_name = active_prof["tool"]
        tool_path = self.dep_manager.get_tool_path(tool_name)
        
        # Verify tool is installed
        if not tool_path:
            CyberMessageBox.show_info(
                self, "Engine Missing",
                f"The engine for '{tool_name}' is not installed.\n"
                f"Please go to 'Engines & Tools' tab and install it.",
                border_color="#ff007f"
            )
            self.config_tabs.setCurrentIndex(3) # Switch to Tools tab
            return

        # Parse URLs
        urls_text = self.urls_input.toPlainText().strip()
        if not urls_text:
            CyberMessageBox.show_info(self, "No URLs", "Please enter one or more URLs to download.", border_color="#ff007f")
            return

        urls = [line.strip() for line in urls_text.split("\n") if line.strip()]
        if not urls:
            CyberMessageBox.show_info(self, "No URLs", "No valid URLs found.", border_color="#ff007f")
            return

        # Clear inputs
        self.urls_input.clear()

        # Extract profile configurations
        export_dir = active_prof["export_dir"]
        
        # Profile settings mapping
        if tool_name == "aria2c":
            settings = active_prof.get("aria2_settings", {})
        elif tool_name == "yt-dlp":
            settings = active_prof.get("ytdlp_settings", {})
        elif tool_name == "gallery-dl":
            settings = active_prof.get("gallerydl_settings", {})
        else:
            settings = {}

        # Add downloads to queue and launch them
        for url in urls:
            download_id = str(uuid.uuid4())
            
            # Create progress card in scroll area
            progress_card = DownloadProgressWidget(download_id, url)
            progress_card.cancelled.connect(self.cancel_download)
            
            # Insert at the top of the layouts (index 0, before the spacer)
            self.queue_list_layout.insertWidget(0, progress_card)

            # Create and launch downloader worker thread
            worker = DownloadWorker(download_id, tool_name, tool_path, url, export_dir, settings)
            worker.progress_updated.connect(self.on_download_progress)
            worker.download_completed.connect(self.on_download_completed)
            worker.log_received.connect(self.on_download_log)
            
            self.active_workers[download_id] = (worker, progress_card)
            worker.start()

    @pyqtSlot(str, int, str, str, str)
    def on_download_progress(self, download_id, percent, speed, eta, status):
        if download_id in self.active_workers:
            _, card = self.active_workers[download_id]
            card.update_progress(percent, speed, eta, status)

    @pyqtSlot(str, bool, str)
    def on_download_completed(self, download_id, success, error_msg):
        if download_id in self.active_workers:
            worker, card = self.active_workers[download_id]
            if success:
                card.set_completed()
            else:
                card.set_error(error_msg)
            
            # Clean up worker thread
            worker.quit()
            worker.wait()
            # Note: We keep the card in active_workers so logs/cancellation logic
            # is accessible, but remove thread resource
            del self.active_workers[download_id]

    @pyqtSlot(str, str)
    def on_download_log(self, download_id, log_line):
        # Simply append to logs console
        self.logs_console.appendPlainText(log_line)

    @pyqtSlot(str)
    def cancel_download(self, download_id):
        # Cancel worker thread
        if download_id in self.active_workers:
            worker, card = self.active_workers[download_id]
            worker.cancel()
            card.set_error("Cancelled by user")

    def clear_completed_downloads(self):
        # We walk through all child widgets of the scroll container
        # and delete any cards that are marked Completed or Error (which have Clear/Remove buttons)
        for i in reversed(range(self.queue_list_layout.count())):
            widget = self.queue_list_layout.itemAt(i).widget()
            if isinstance(widget, DownloadProgressWidget):
                btn_text = widget.cancel_btn.text()
                if btn_text in ["Clear", "Remove"]:
                    widget.setParent(None)
                    widget.deleteLater()

    def clear_logs(self):
        self.logs_console.clear()

    def toggle_logs(self, checked):
        # checked is True if logs should be visible (button checked)
        self.logs_widget.setVisible(checked)
        if checked:
            self.logs_toggle_btn.setText("📜 Hide Logs")
            self.logs_toggle_btn.setObjectName("neon_cyan_btn")
        else:
            self.logs_toggle_btn.setText("📜 Show Logs")
            self.logs_toggle_btn.setObjectName("")
            
        # Refresh styles
        self.logs_toggle_btn.style().unpolish(self.logs_toggle_btn)
        self.logs_toggle_btn.style().polish(self.logs_toggle_btn)

    def closeEvent(self, event):
        # Terminate any running downloads on window close
        for download_id, (worker, _) in list(self.active_workers.items()):
            worker.cancel()
            worker.quit()
            worker.wait()
        event.accept()
