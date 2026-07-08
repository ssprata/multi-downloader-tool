CYBERPUNK_STYLE = """
/* Cyberpunk/Synthwave Neon QSS Stylesheet */

QMainWindow {
    background-color: #0d0e15;
    color: #ffffff;
}

QWidget {
    font-family: 'Segoe UI', Arial, sans-serif;
    color: #e2e8f0;
}

/* Scrollbars styling */
QScrollBar:vertical {
    border: none;
    background: #0d0e15;
    width: 8px;
    margin: 0px 0 0px 0;
}
QScrollBar::handle:vertical {
    background: #9d4edd;
    min-height: 20px;
    border-radius: 4px;
}
QScrollBar::handle:vertical:hover {
    background: #ff007f;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: none;
}

QScrollBar:horizontal {
    border: none;
    background: #0d0e15;
    height: 8px;
    margin: 0px 0 0px 0;
}
QScrollBar::handle:horizontal {
    background: #9d4edd;
    min-width: 20px;
    border-radius: 4px;
}
QScrollBar::handle:horizontal:hover {
    background: #ff007f;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}
QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
    background: none;
}

/* Sidebar & Cards */
QFrame#sidebar_frame {
    background-color: #12131c;
    border-right: 2px solid #2a2b3d;
}

QFrame#card_frame {
    background-color: #12131c;
    border: 1px solid #2a2b3d;
    border-radius: 8px;
}

/* Labels */
QLabel {
    font-size: 13px;
}
QLabel#header_label {
    font-size: 18px;
    font-weight: bold;
    color: #00f0ff;
    border-bottom: 2px solid #00f0ff;
    padding-bottom: 5px;
}
QLabel#title_label {
    font-size: 24px;
    font-weight: bold;
    color: #ff007f;
    margin-bottom: 10px;
}
QLabel#section_title {
    font-size: 14px;
    font-weight: bold;
    color: #9d4edd;
    margin-top: 10px;
    margin-bottom: 5px;
}

/* Inputs & Textareas */
QLineEdit {
    background-color: #171822;
    border: 1px solid #2a2b3d;
    border-radius: 5px;
    padding: 6px 12px;
    color: #ffffff;
    font-size: 13px;
}
QLineEdit:focus {
    border: 1px solid #00f0ff;
}

QTextEdit, QPlainTextEdit {
    background-color: #171822;
    border: 1px solid #2a2b3d;
    border-radius: 5px;
    padding: 8px;
    color: #ffffff;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 12px;
}
QTextEdit:focus, QPlainTextEdit:focus {
    border: 1px solid #00f0ff;
}

/* Dropdowns / ComboBoxes */
QComboBox {
    background-color: #171822;
    border: 1px solid #2a2b3d;
    border-radius: 5px;
    padding: 6px 12px;
    color: #ffffff;
    font-size: 13px;
    min-width: 120px;
}
QComboBox:focus {
    border: 1px solid #00f0ff;
}
QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 20px;
    border-left-width: 0px;
    border-top-right-radius: 5px;
    border-bottom-right-radius: 5px;
}
QComboBox QAbstractItemView {
    background-color: #171822;
    border: 1px solid #2a2b3d;
    selection-background-color: #9d4edd;
    selection-color: #ffffff;
    color: #ffffff;
}

/* List Widgets (Profiles list) */
QListWidget {
    background-color: #171822;
    border: 1px solid #2a2b3d;
    border-radius: 5px;
    padding: 5px;
    color: #ffffff;
    font-size: 13px;
}
QListWidget::item {
    border-radius: 4px;
    padding: 8px 12px;
    margin-bottom: 4px;
    border-bottom: 1px solid #252635;
}
QListWidget::item:hover {
    background-color: #252635;
}
QListWidget::item:selected {
    background-color: #9d4edd;
    color: #ffffff;
    border-bottom: 1px solid #9d4edd;
}

/* Tree Widgets (Profiles tree list) */
QTreeWidget {
    background-color: #171822;
    border: 1px solid #2a2b3d;
    border-radius: 5px;
    padding: 5px;
    color: #ffffff;
    font-size: 13px;
}
QTreeWidget::item {
    border-radius: 4px;
    padding: 6px 10px;
    margin-top: 2px;
    margin-bottom: 2px;
}
QTreeWidget::item:hover {
    background-color: #252635;
    color: #00f0ff;
}
QTreeWidget::item:selected {
    background-color: #9d4edd;
    color: #ffffff;
}

/* Tabs styling */
QTabWidget::pane {
    border: 1px solid #2a2b3d;
    background-color: #12131c;
    border-radius: 8px;
    top: -1px;
}
QTabBar::tab {
    background-color: #171822;
    border: 1px solid #2a2b3d;
    border-bottom: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    padding: 8px 16px;
    color: #a0a5c0;
    font-size: 13px;
    font-weight: bold;
    margin-right: 4px;
}
QTabBar::tab:hover {
    color: #ffffff;
    background-color: #252635;
}
QTabBar::tab:selected {
    background-color: #12131c;
    border-color: #2a2b3d;
    border-bottom: 1px solid #12131c;
    color: #ff007f;
}

/* Spinboxes & checkboxes */
QSpinBox {
    background-color: #171822;
    border: 1px solid #2a2b3d;
    border-radius: 5px;
    padding: 6px;
    color: #ffffff;
}
QSpinBox:focus {
    border: 1px solid #00f0ff;
}

QCheckBox {
    spacing: 8px;
    font-size: 13px;
}
QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 1px solid #2a2b3d;
    border-radius: 4px;
    background-color: #171822;
}
QCheckBox::indicator:unchecked:hover {
    border: 1px solid #00f0ff;
}
QCheckBox::indicator:checked {
    border: 1px solid #ff007f;
    background-color: #ff007f;
}

/* Progress Bar */
QProgressBar {
    background-color: #171822;
    border: 1px solid #2a2b3d;
    border-radius: 6px;
    text-align: center;
    color: #ffffff;
    font-weight: bold;
}
QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 #ff007f, stop:1 #00f0ff);
    border-radius: 5px;
}

/* Buttons */
QPushButton {
    background-color: #171822;
    border: 1px solid #2a2b3d;
    border-radius: 5px;
    color: #ffffff;
    padding: 8px 16px;
    font-weight: bold;
    font-size: 13px;
}
QPushButton:hover {
    background-color: #252635;
    border: 1px solid #9d4edd;
}
QPushButton:pressed {
    background-color: #9d4edd;
}

/* Glowing Neon buttons */
QPushButton#neon_magenta_btn {
    border: 1px solid #ff007f;
    color: #ffffff;
    background-color: rgba(255, 0, 127, 0.1);
}
QPushButton#neon_magenta_btn:hover {
    background-color: #ff007f;
}

QPushButton#neon_cyan_btn {
    border: 1px solid #00f0ff;
    color: #ffffff;
    background-color: rgba(0, 240, 255, 0.1);
}
QPushButton#neon_cyan_btn:hover {
    background-color: #00f0ff;
    color: #0d0e15;
}

QPushButton#download_btn {
    border: 2px solid #ff007f;
    color: #ffffff;
    background-color: rgba(255, 0, 127, 0.15);
    font-size: 16px;
    border-radius: 8px;
    padding: 12px 24px;
    letter-spacing: 1px;
}
QPushButton#download_btn:hover {
    background-color: #ff007f;
    border-color: #ff007f;
}
QPushButton#download_btn:disabled {
    border-color: #2a2b3d;
    background-color: #171822;
    color: #6b7280;
}

/* Logs and output widget styling */
QPlainTextEdit#logs_console {
    background-color: #08080c;
    border: 1px solid #2a2b3d;
    border-radius: 6px;
    color: #00f0ff;
}

QListWidget#downloads_queue_list {
    background-color: #12131c;
    border: 1px solid #2a2b3d;
}

/* Status overlay for first time setup */
QWidget#splash_overlay {
    background-color: rgba(13, 14, 21, 0.95);
}
"""
