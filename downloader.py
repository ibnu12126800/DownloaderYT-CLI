import yt_dlp
import os

class YouTubeHandler:
    def __init__(self):
        self.ydl_opts = {
            'quiet': True,
            'no_warnings': True,
        }

    def get_video_info(self, url):
        """Mengambil metadata video tanpa download."""
        with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
            try:
                info = ydl.extract_info(url, download=False)
                return info, None
            except Exception as e:
                return None, str(e)

    def download(self, url, options, progress_hook=None):
        """Melakukan download dengan opsi tertentu."""
        # Struktur folder: downloads/Judul Video [ID]/
        # File: downloads/Judul Video [ID]/Judul Video [ID].ext
        base_opts = {
            'writethumbnail': True,
            'writeinfojson': True,
            'outtmpl': os.path.join('downloads', '%(title)s [%(id)s]', '%(title)s [%(id)s].%(ext)s'),
            'quiet': True,
            'no_warnings': True,
            'ignoreerrors': True,
        }
        
        # Merge options user (seperti format) dengan base options
        final_opts = {**base_opts, **options}
        
        if progress_hook:
            final_opts['progress_hooks'] = [progress_hook]

        with yt_dlp.YoutubeDL(final_opts) as ydl:
            try:
                ydl.download([url])
                return True, "Download selesai."
            except Exception as e:
                return False, str(e)
