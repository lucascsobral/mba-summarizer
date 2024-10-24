import yt_dlp

# Function to download video
def download_video(url):
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
            }],
            'outtmpl': '../data/audio/video.%(ext)s',  # File name with the original extension
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return True
    except Exception as e:
        print(f"Erro ao baixar o vídeo: {e}")
        return False




