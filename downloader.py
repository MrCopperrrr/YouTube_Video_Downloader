import os
import subprocess
from pytubefix import YouTube
from PyQt5.QtCore import QObject, pyqtSignal


class Downloader(QObject):
    progress_changed = pyqtSignal(int)
    download_finished = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, url, fmt, resolution, output_path):
        super().__init__()
        self.url = url
        self.fmt = fmt
        self.resolution = resolution
        self.output_path = output_path

    def run(self):
        try:
            yt = YouTube(self.url, on_progress_callback=self.progress_hook)

            if self.fmt == 'video':
                video_stream = yt.streams.filter(
                    progressive=False,
                    file_extension='mp4',
                    res=self.resolution
                ).order_by('resolution').desc().first()

                if not video_stream:
                    video_stream = yt.streams.filter(
                        progressive=True,
                        file_extension='mp4'
                    ).order_by('resolution').desc().first()

                audio_stream = yt.streams.filter(
                    only_audio=True,
                    file_extension='mp4'
                ).order_by('abr').desc().first()

                if video_stream is None or audio_stream is None:
                    raise Exception("Cannot find video or audio.")

                video_path = os.path.join(self.output_path, "video_temp.mp4")
                audio_path = os.path.join(self.output_path, "audio_temp.mp4")
                output_filename = self.sanitize_filename(yt.title) + ".mp4"
                output_file = os.path.join(self.output_path, output_filename)

                video_stream.download(output_path=self.output_path, filename="video_temp.mp4")
                audio_stream.download(output_path=self.output_path, filename="audio_temp.mp4")

                cmd = [
                    "ffmpeg", "-y",
                    "-i", video_path,
                    "-i", audio_path,
                    "-c:v", "copy",
                    "-c:a", "aac",
                    output_file
                ]

                result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                if result.returncode != 0:
                    self.error_occurred.emit(f"Fail merging video and audio:\n{result.stderr}")
                    return

                os.remove(video_path)
                os.remove(audio_path)

                self.download_finished.emit(f"Finished download video: {output_file}")

            elif self.fmt == 'audio':
                audio_stream = yt.streams.filter(
                    only_audio=True,
                    file_extension='mp4'
                ).order_by('abr').desc().first()

                if audio_stream is None:
                    raise Exception("Cannot find audio stream.")

                output_filename = self.sanitize_filename(yt.title) + ".m4a"
                output_file = os.path.join(self.output_path, output_filename)
                audio_stream.download(output_path=self.output_path, filename=output_filename)

                self.download_finished.emit(f"Finished download audio: {output_file}")

        except Exception as e:
            self.error_occurred.emit(str(e))

    def progress_hook(self, stream, chunk, bytes_remaining):
        total_size = stream.filesize
        bytes_downloaded = total_size - bytes_remaining
        progress_percent = int(bytes_downloaded / total_size * 100)
        self.progress_changed.emit(progress_percent)

    def sanitize_filename(self, s):
        invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
        for ch in invalid_chars:
            s = s.replace(ch, '')
        return s.strip()
