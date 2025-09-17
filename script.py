import os
import subprocess
from yt_dlp import YoutubeDL
from urllib.parse import urlparse, parse_qs

DOWNLOAD_PATH = os.path.join(os.path.expanduser("~"), "Downloads", "Скачанные видео")

FFMPEG_PATH = os.path.join(os.path.dirname(__file__), "ffmpeg.exe")
FFMPEG_EXISTS = os.path.isfile(FFMPEG_PATH)

def clean_youtube_url(url):
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    if 'v' in query:
        return f"https://www.youtube.com/watch?v={query['v'][0]}"
    return url

def download_video(url):
    os.makedirs(DOWNLOAD_PATH, exist_ok=True)
    url = clean_youtube_url(url)

    ydl_opts = {
        'outtmpl': os.path.join(DOWNLOAD_PATH, '%(title)s.%(ext)s'),
        'noplaylist': True,
        'quiet': False,
    }

    if FFMPEG_EXISTS:
        ydl_opts['ffmpeg_location'] = FFMPEG_PATH

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        formats = info.get('formats', [])

        best_video = None
        best_audio = None
        max_height = 0
        for f in formats:
            if f.get('vcodec') != 'none' and f.get('height', 0) > max_height:
                best_video = f['format_id']
                max_height = f['height']
            if f.get('acodec') != 'none':
                best_audio = f['format_id']

        if best_video and best_audio and FFMPEG_EXISTS:
            format_str = f"{best_video}+{best_audio}"
        else:
            format_str = 'best'

        ydl.params['format'] = format_str

        info_dict = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info_dict)

    if os.name == "nt":
        subprocess.Popen(f'explorer /select,"{filename}"')
    elif os.name == "posix":
        subprocess.Popen(["xdg-open", DOWNLOAD_PATH])

if __name__ == "__main__":
    while True:
        video_url = input("🎥 Вставьте ссылку на YouTube (или Enter для выхода): ").strip()
        if not video_url:
            break
        download_video(video_url)
        print("✅ Видео загружено!\n")
