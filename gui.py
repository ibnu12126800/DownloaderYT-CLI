#!/usr/bin/env python3
"""
YouTube Downloader - Desktop GUI (PyQt6)
"""

import os
import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QRadioButton, QButtonGroup,
    QComboBox, QProgressBar, QFileDialog, QMessageBox, QFrame,
    QGroupBox, QSizePolicy, QScrollArea
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QIcon

from downloader import YouTubeHandler

# Quality options
VIDEO_QUALITIES = [
    ("🌟 Best Available", "bestvideo+bestaudio/best"),
    ("📺 4K (2160p)", "bestvideo[height<=2160]+bestaudio/best[height<=2160]"),
    ("🖥️ 2K (1440p)", "bestvideo[height<=1440]+bestaudio/best[height<=1440]"),
    ("📀 Full HD (1080p)", "bestvideo[height<=1080]+bestaudio/best[height<=1080]"),
    ("💿 HD (720p)", "bestvideo[height<=720]+bestaudio/best[height<=720]"),
    ("📼 SD (480p)", "bestvideo[height<=480]+bestaudio/best[height<=480]"),
    ("📱 Low (360p)", "bestvideo[height<=360]+bestaudio/best[height<=360]"),
]

AUDIO_QUALITIES = [
    ("🎧 MP3 (Best)", "mp3"),
    ("🎼 M4A (AAC)", "m4a"),
    ("🎹 FLAC (Lossless)", "flac"),
    ("🔉 WAV", "wav"),
]


class FetchThread(QThread):
    """Thread untuk mengambil metadata tanpa blocking UI."""
    finished = pyqtSignal(dict, str)  # info, error
    
    def __init__(self, url):
        super().__init__()
        self.url = url
        self.handler = YouTubeHandler()
    
    def run(self):
        info, error = self.handler.get_video_info(self.url)
        self.finished.emit(info or {}, error or "")


class DownloadThread(QThread):
    """Thread untuk download tanpa blocking UI."""
    progress = pyqtSignal(int, str)  # percentage, status
    finished = pyqtSignal(bool, str)  # success, message
    
    def __init__(self, url, options):
        super().__init__()
        self.url = url
        self.options = options
        self.handler = YouTubeHandler()
        self._is_cancelled = False
    
    def run(self):
        def progress_hook(d):
            if self._is_cancelled:
                raise Exception("Download dibatalkan")
            
            if d['status'] == 'downloading':
                try:
                    total = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
                    downloaded = d.get('downloaded_bytes', 0)
                    
                    if total > 0:
                        percentage = int((downloaded / total) * 100)
                    else:
                        percentage = 0
                    
                    speed = d.get('speed', 0) or 0
                    if speed > 1024 * 1024:
                        speed_str = f"{speed / 1024 / 1024:.1f} MB/s"
                    elif speed > 1024:
                        speed_str = f"{speed / 1024:.1f} KB/s"
                    else:
                        speed_str = f"{speed:.0f} B/s"
                    
                    info_dict = d.get('info_dict', {})
                    title = info_dict.get('title', 'Downloading...')
                    if len(title) > 40:
                        title = title[:40] + '...'
                    
                    status = f"{title} | {speed_str}"
                    self.progress.emit(percentage, status)
                except Exception:
                    pass
            elif d['status'] == 'finished':
                self.progress.emit(100, "Processing...")
        
        success, msg = self.handler.download(self.url, self.options, progress_hook)
        self.finished.emit(success, msg)
    
    def cancel(self):
        self._is_cancelled = True


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.handler = YouTubeHandler()
        self.video_info = None
        self.download_thread = None
        self.fetch_thread = None
        
        self.init_ui()
        self.apply_styles()
    
    def init_ui(self):
        self.setWindowTitle("🎬 YouTube Downloader")
        self.setMinimumSize(500, 500)
        self.resize(550, 650)
        
        # Scroll area untuk responsivitas
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.setCentralWidget(scroll)
        
        # Container widget
        container = QWidget()
        scroll.setWidget(container)
        layout = QVBoxLayout(container)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # === Header ===
        header = QLabel("🎬 YouTube Downloader")
        header.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        subtitle = QLabel("Download video & audio dari YouTube")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: #888; font-size: 12px;")
        layout.addWidget(subtitle)
        
        # === URL Input ===
        url_group = QGroupBox("URL YouTube")
        url_layout = QHBoxLayout(url_group)
        
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Paste URL video atau playlist YouTube...")
        self.url_input.returnPressed.connect(self.fetch_info)
        url_layout.addWidget(self.url_input)
        
        self.fetch_btn = QPushButton("🔍 Fetch")
        self.fetch_btn.setFixedWidth(80)
        self.fetch_btn.clicked.connect(self.fetch_info)
        url_layout.addWidget(self.fetch_btn)
        
        layout.addWidget(url_group)
        
        # === Video Info ===
        self.info_group = QGroupBox("Informasi Video")
        info_layout = QVBoxLayout(self.info_group)
        
        self.title_label = QLabel("Judul: -")
        self.title_label.setWordWrap(True)
        self.title_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        info_layout.addWidget(self.title_label)
        
        self.channel_label = QLabel("Channel: -")
        info_layout.addWidget(self.channel_label)
        
        self.details_label = QLabel("Durasi: - | Views: -")
        self.details_label.setStyleSheet("color: #888;")
        info_layout.addWidget(self.details_label)
        
        self.info_group.setVisible(False)
        layout.addWidget(self.info_group)
        
        # === Download Options ===
        options_group = QGroupBox("Opsi Download")
        options_layout = QVBoxLayout(options_group)
        
        # Type selection
        type_layout = QHBoxLayout()
        type_label = QLabel("Tipe:")
        type_label.setFixedWidth(60)
        type_layout.addWidget(type_label)
        
        self.type_group = QButtonGroup(self)
        self.video_radio = QRadioButton("🎬 Video")
        self.video_radio.setChecked(True)
        self.video_radio.toggled.connect(self.update_quality_options)
        self.audio_radio = QRadioButton("🎵 Audio")
        
        self.type_group.addButton(self.video_radio)
        self.type_group.addButton(self.audio_radio)
        
        type_layout.addWidget(self.video_radio)
        type_layout.addWidget(self.audio_radio)
        type_layout.addStretch()
        options_layout.addLayout(type_layout)
        
        # Quality selection
        quality_layout = QHBoxLayout()
        quality_label = QLabel("Kualitas:")
        quality_label.setFixedWidth(60)
        quality_layout.addWidget(quality_label)
        
        self.quality_combo = QComboBox()
        self.quality_combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.update_quality_options()
        quality_layout.addWidget(self.quality_combo)
        options_layout.addLayout(quality_layout)
        
        # Output folder
        output_layout = QHBoxLayout()
        output_label = QLabel("Output:")
        output_label.setFixedWidth(60)
        output_layout.addWidget(output_label)
        
        self.output_input = QLineEdit("downloads")
        output_layout.addWidget(self.output_input)
        
        browse_btn = QPushButton("📁")
        browse_btn.setFixedWidth(40)
        browse_btn.clicked.connect(self.browse_folder)
        output_layout.addWidget(browse_btn)
        options_layout.addLayout(output_layout)
        
        layout.addWidget(options_group)
        
        # === Progress ===
        progress_group = QGroupBox("Progress")
        progress_layout = QVBoxLayout(progress_group)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        progress_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("Siap untuk download")
        self.status_label.setStyleSheet("color: #888; font-size: 11px;")
        progress_layout.addWidget(self.status_label)
        
        layout.addWidget(progress_group)
        
        # === Buttons ===
        btn_layout = QHBoxLayout()
        
        self.download_btn = QPushButton("⬇️  Download")
        self.download_btn.setFixedHeight(45)
        self.download_btn.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.download_btn.clicked.connect(self.start_download)
        self.download_btn.setEnabled(False)
        btn_layout.addWidget(self.download_btn)
        
        self.cancel_btn = QPushButton("❌ Cancel")
        self.cancel_btn.setFixedHeight(45)
        self.cancel_btn.setFixedWidth(100)
        self.cancel_btn.clicked.connect(self.cancel_download)
        self.cancel_btn.setVisible(False)
        btn_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(btn_layout)
        
        # Spacer
        layout.addStretch()
    
    def apply_styles(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e2e;
            }
            QWidget {
                background-color: #1e1e2e;
                color: #cdd6f4;
                font-family: 'Segoe UI', sans-serif;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #45475a;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QLineEdit {
                background-color: #313244;
                border: 1px solid #45475a;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border-color: #89b4fa;
            }
            QPushButton {
                background-color: #89b4fa;
                color: #1e1e2e;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #b4befe;
            }
            QPushButton:pressed {
                background-color: #74c7ec;
            }
            QPushButton:disabled {
                background-color: #45475a;
                color: #6c7086;
            }
            QRadioButton {
                spacing: 8px;
                font-size: 13px;
            }
            QRadioButton::indicator {
                width: 16px;
                height: 16px;
            }
            QComboBox {
                background-color: #313244;
                border: 1px solid #45475a;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 13px;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox QAbstractItemView {
                background-color: #313244;
                border: 1px solid #45475a;
                selection-background-color: #89b4fa;
                selection-color: #1e1e2e;
            }
            QProgressBar {
                background-color: #313244;
                border: none;
                border-radius: 6px;
                height: 20px;
                text-align: center;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #89b4fa, stop:1 #cba6f7);
                border-radius: 6px;
            }
        """)
    
    def update_quality_options(self):
        self.quality_combo.clear()
        if self.video_radio.isChecked():
            for name, value in VIDEO_QUALITIES:
                self.quality_combo.addItem(name, value)
        else:
            for name, value in AUDIO_QUALITIES:
                self.quality_combo.addItem(name, value)
    
    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Pilih Folder Output")
        if folder:
            self.output_input.setText(folder)
    
    def fetch_info(self):
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Error", "Masukkan URL YouTube!")
            return
        
        self.fetch_btn.setEnabled(False)
        self.fetch_btn.setText("...")
        self.status_label.setText("Mengambil informasi video...")
        self.download_btn.setEnabled(False)
        
        self.fetch_thread = FetchThread(url)
        self.fetch_thread.finished.connect(self.on_fetch_finished)
        self.fetch_thread.start()
    
    def on_fetch_finished(self, info, error):
        self.fetch_btn.setEnabled(True)
        self.fetch_btn.setText("🔍 Fetch")
        
        if error:
            self.status_label.setText(f"Error: {error[:50]}...")
            QMessageBox.critical(self, "Error", f"Gagal mengambil info:\n{error}")
            return
        
        self.video_info = info
        is_playlist = info.get('_type') == 'playlist'
        
        if is_playlist:
            self.title_label.setText(f"📋 {info.get('title', 'Playlist')}")
            self.channel_label.setText(f"Uploader: {info.get('uploader', 'N/A')}")
            count = info.get('playlist_count') or len(info.get('entries', []))
            self.details_label.setText(f"Jumlah Video: {count}")
        else:
            self.title_label.setText(f"🎬 {info.get('title', 'N/A')}")
            self.channel_label.setText(f"Channel: {info.get('uploader', 'N/A')}")
            
            duration = info.get('duration', 0)
            if duration:
                m, s = divmod(duration, 60)
                h, m = divmod(m, 60)
                dur_str = f"{int(h)}:{int(m):02d}:{int(s):02d}" if h else f"{int(m)}:{int(s):02d}"
            else:
                dur_str = "-"
            
            views = info.get('view_count', 0)
            if views >= 1_000_000:
                views_str = f"{views/1_000_000:.1f}M"
            elif views >= 1_000:
                views_str = f"{views/1_000:.1f}K"
            else:
                views_str = str(views)
            
            self.details_label.setText(f"Durasi: {dur_str} | Views: {views_str}")
        
        self.info_group.setVisible(True)
        self.download_btn.setEnabled(True)
        self.status_label.setText("Siap untuk download!")
        
        # Auto resize window jika perlu
        self.adjustSize()
        if self.height() < 680:
            self.resize(self.width(), 680)
    
    def start_download(self):
        if not self.video_info:
            QMessageBox.warning(self, "Error", "Fetch video info terlebih dahulu!")
            return
        
        url = self.url_input.text().strip()
        output_dir = self.output_input.text().strip() or "downloads"
        quality_value = self.quality_combo.currentData()
        is_video = self.video_radio.isChecked()
        
        # Prepare options
        options = {}
        
        is_playlist = self.video_info.get('_type') == 'playlist'
        if is_playlist:
            playlist_title = self.video_info.get('title', 'Playlist')
            safe_title = "".join(x for x in playlist_title if x.isalnum() or x in " -_").strip()
            options['outtmpl'] = os.path.join(output_dir, safe_title, '%(title)s [%(id)s]', '%(title)s [%(id)s].%(ext)s')
        else:
            options['outtmpl'] = os.path.join(output_dir, '%(title)s [%(id)s]', '%(title)s [%(id)s].%(ext)s')
        
        if is_video:
            options['format'] = quality_value
            options['merge_output_format'] = 'mp4'
        else:
            options['format'] = 'bestaudio/best'
            options['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': quality_value,
                'preferredquality': '192',
            }]
        
        # Update UI
        self.download_btn.setEnabled(False)
        self.fetch_btn.setEnabled(False)
        self.cancel_btn.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("Memulai download...")
        
        # Start download thread
        self.download_thread = DownloadThread(url, options)
        self.download_thread.progress.connect(self.on_progress)
        self.download_thread.finished.connect(self.on_download_finished)
        self.download_thread.start()
    
    def on_progress(self, percentage, status):
        self.progress_bar.setValue(percentage)
        self.status_label.setText(status)
    
    def on_download_finished(self, success, message):
        self.download_btn.setEnabled(True)
        self.fetch_btn.setEnabled(True)
        self.cancel_btn.setVisible(False)
        
        if success:
            self.progress_bar.setValue(100)
            self.status_label.setText("✅ Download selesai!")
            QMessageBox.information(self, "Sukses", f"Download selesai!\n\nFile tersimpan di folder '{self.output_input.text()}'")
        else:
            self.status_label.setText(f"❌ Error: {message[:50]}...")
            QMessageBox.critical(self, "Error", f"Download gagal:\n{message}")
    
    def cancel_download(self):
        if self.download_thread and self.download_thread.isRunning():
            self.download_thread.cancel()
            self.download_thread.terminate()
            self.download_btn.setEnabled(True)
            self.fetch_btn.setEnabled(True)
            self.cancel_btn.setVisible(False)
            self.status_label.setText("Download dibatalkan")
            self.progress_bar.setValue(0)


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
