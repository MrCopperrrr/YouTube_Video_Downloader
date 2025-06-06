import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QFileDialog, QProgressBar,
    QMessageBox, QButtonGroup
)
from PyQt5.QtCore import Qt, QThread, QPoint
from PyQt5.QtGui import QIcon, QFontDatabase, QFont
from downloader import Downloader


def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

FFMPEG_PATH = resource_path("ffmpeg.exe")


class YouTubeDownloader(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YouTube Downloader")
        self.setGeometry(200, 200, 600, 380)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setStyleSheet(self.stylesheet())
        self.old_pos = None
        self.initUI()

    def initUI(self):
        self.title_bar = QWidget()
        self.title_bar.setObjectName("title_bar")
        self.title_bar.setFixedHeight(32)

        title_label = QLabel(" YouTube Downloader - by MrCopper")
        title_label.setStyleSheet("color: #484b6a; font-weight: bold; background: transparent;")
        title_label.setFixedHeight(32)

        self.min_btn = QPushButton()
        self.min_btn.setIcon(QIcon(resource_path("icon_minimize.svg")))
        self.min_btn.setFixedSize(30, 30)
        self.min_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
            }
            QPushButton:hover {
                background-color: #d2d3db;
            }
        """)
        self.min_btn.clicked.connect(self.showMinimized)

        self.close_btn = QPushButton()
        self.close_btn.setIcon(QIcon(resource_path("icon_close.svg")))
        self.close_btn.setFixedSize(30, 30)
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
            }
            QPushButton:hover {
                background-color: #ff4d4d;
            }
        """)
        self.close_btn.clicked.connect(self.close)

        title_layout = QHBoxLayout()
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        title_layout.addWidget(self.min_btn)
        title_layout.addWidget(self.close_btn)
        title_layout.setContentsMargins(5, 0, 5, 0)
        self.title_bar.setLayout(title_layout)

        self.url_label = QLabel("YouTube URL:")
        self.url_input = QLineEdit()

        self.format_label = QLabel("Format:")

        self.btn_video = QPushButton("Video (.mp4)")
        self.btn_audio = QPushButton("Audio Only (.m4a)")
        self.btn_video.setCheckable(True)
        self.btn_audio.setCheckable(True)
        self.btn_video.setChecked(True)

        self.format_group = QButtonGroup()
        self.format_group.addButton(self.btn_video)
        self.format_group.addButton(self.btn_audio)

        format_layout = QHBoxLayout()
        format_layout.addWidget(self.btn_video)
        format_layout.addWidget(self.btn_audio)

        self.resolution_label = QLabel("Resolution:")
        self.resolutions = ["1080p", "720p", "480p", "360p", "240p", "144p"]

        self.res_btns = []
        self.res_group = QButtonGroup()
        res_layout = QHBoxLayout()

        for res in self.resolutions:
            btn = QPushButton(res)
            btn.setCheckable(True)
            self.res_btns.append(btn)
            self.res_group.addButton(btn)
            res_layout.addWidget(btn)

        self.res_btns[0].setChecked(True)

        self.output_label = QLabel("Save to:")
        self.output_path = QLineEdit()
        self.output_path.setReadOnly(True)
        self.choose_folder_btn = QPushButton("Choose Folder")
        self.choose_folder_btn.setStyleSheet("font-weight: bold;")
        self.choose_folder_btn.clicked.connect(self.choose_folder)

        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(20)
        self.progress_bar.setMinimumWidth(200)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #484b6a;
                border-radius: 10px;
                background-color: #e4e5f1;
            }
            QProgressBar::chunk {
                border-radius: 10px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                            stop:0 hsla(277,79%,84%,1),
                                            stop:1 hsla(204,95%,77%,1));
            }
        """)

        progress_layout = QHBoxLayout()
        progress_layout.addWidget(self.progress_bar)
        progress_layout.setContentsMargins(0, 0, 0, 0)

        self.download_btn = QPushButton("Start Download")
        self.download_btn.clicked.connect(self.start_download)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.title_bar)

        body_layout = QVBoxLayout()
        body_layout.setContentsMargins(20, 10, 20, 20)

        body_layout.addWidget(self.url_label)
        body_layout.addWidget(self.url_input)

        body_layout.addWidget(self.format_label)
        body_layout.addLayout(format_layout)

        body_layout.addWidget(self.resolution_label)
        body_layout.addLayout(res_layout)

        body_layout.addWidget(self.output_label)
        output_layout = QHBoxLayout()
        output_layout.addWidget(self.output_path)
        output_layout.addWidget(self.choose_folder_btn)
        body_layout.addLayout(output_layout)

        body_layout.addWidget(self.download_btn)
        body_layout.addLayout(progress_layout)

        layout.addLayout(body_layout)
        self.setLayout(layout)

        self.btn_video.setStyleSheet("font-weight: bold;")
        self.btn_audio.setStyleSheet("font-weight: bold;")

        for btn in self.res_btns:
            btn.setStyleSheet("font-weight: bold;")

        self.download_btn.setStyleSheet("font-weight: bold;")

    def set_selected_resolution(self, selected_btn):
        for btn in self.resolution_buttons:
            btn.setChecked(False)
        selected_btn.setChecked(True)
        self.selected_resolution_btn = selected_btn

    def choose_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Choose folder to save")
        if folder:
            self.output_path.setText(folder)

    def start_download(self):
        url = self.url_input.text().strip()
        fmt = 'audio' if self.btn_audio.isChecked() else 'video'
        resolution = None
        for btn in self.res_btns:
            if btn.isChecked():
                resolution = btn.text()
                break
        output_path = self.output_path.text().strip()

        if not url or not output_path:
            QMessageBox.warning(self, "Error", "Please fill all required fields!")
            return

        self.thread = QThread()
        self.worker = Downloader(url, fmt, resolution, output_path)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.progress_changed.connect(self.progress_bar.setValue)
        self.worker.download_finished.connect(self.on_finished)
        self.worker.error_occurred.connect(self.on_error)
        self.worker.download_finished.connect(self.thread.quit)
        self.worker.download_finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.download_btn.setEnabled(False)
        self.progress_bar.setValue(0)
        self.thread.start()

    def on_finished(self, msg):
        QMessageBox.information(self, "Finish", msg)
        self.download_btn.setEnabled(True)
        self.progress_bar.setValue(100)

    def on_error(self, error_msg):
        QMessageBox.critical(self, "Error", error_msg)
        self.download_btn.setEnabled(True)
        self.progress_bar.setValue(0)

    def stylesheet(self):
        return """
        QWidget {
            background-color: #fafafa;
            font-family: Segoe UI;
            font-size: 18px;
        }

        QLabel {
            color: #484b6a;
            font-weight: 600;
        }

        QLineEdit, QComboBox {
            background-color: #ffffff;
            border: 1px solid #d2d3db;
            padding: 6px;
            border-radius: 4px;
        }

        /* --- Header với gradient --- */
        QWidget#title_bar {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 rgba(219, 180, 246, 255),
                stop:1 rgba(141, 208, 252, 255));
        }

        /* --- Nút bấm với gradient --- */
        QPushButton {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 rgba(219, 180, 246, 255),
                stop:1 rgba(141, 208, 252, 255));
            color: white;
            padding: 8px 16px;
            border: none;
            border-radius: 4px;
        }

        QPushButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 rgba(141, 208, 252, 255),
                stop:1 rgba(219, 180, 246, 255));
        }

        QRadioButton {
            color: #484b6a;
        }

        QProgressBar {
            height: 20px;
            border: 1px solid #d2d3db;
            border-radius: 5px;
            background-color: #e4e5f1;
            text-align: center;
        }

        QProgressBar::chunk {
            background-color: #484b6a;
            width: 10px;
            margin: 1px;
        }
        QPushButton {
            color: white;
            border: none;
            border-radius: 12px;
            padding: 8px 18px;
            background: qlineargradient(
                x1:0, y1:0, x2:1, y2:0,
                stop:0 hsla(277, 79%, 84%, 1),
                stop:1 hsla(204, 95%, 77%, 1)
            );
        }
        
        QPushButton:hover {
            background: qlineargradient(
                x1:0, y1:0, x2:1, y2:0,
                stop:0 hsla(277, 79%, 70%, 1),
                stop:1 hsla(204, 95%, 60%, 1)
            );
        }
        
        QPushButton:checked {
            background: qlineargradient(
                x1:0, y1:0, x2:1, y2:0,
                stop:0 hsla(204, 95%, 50%, 1),
                stop:1 hsla(277, 79%, 50%, 1)
            );
            font-weight: bold;
        }
        
        QPushButton:checked:hover {
            background: qlineargradient(
                x1:0, y1:0, x2:1, y2:0,
                stop:0 hsla(204, 95%, 40%, 1),
                stop:1 hsla(277, 79%, 40%, 1)
            );
        }

        """

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and event.y() < 40:
            self.old_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        if self.old_pos:
            delta = QPoint(event.globalPos() - self.old_pos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPos()

    def mouseReleaseEvent(self, event):
        self.old_pos = None



if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = YouTubeDownloader()
    window.show()
    sys.exit(app.exec_())