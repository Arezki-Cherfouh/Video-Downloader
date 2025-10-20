# from pytube import YouTube
# from pytube.exceptions import RegexMatchError
# from urllib.error import HTTPError
# def progress_callback(stream, chunk, bytes_remaining):
#     total_size = stream.filesize
#     bytes_downloaded = total_size - bytes_remaining
#     percent = (bytes_downloaded / total_size) * 100
#     print(f"Downloaded: {percent:.2f}%", end="\r")
# while True:
#     try:
#         url = input("Enter YouTube video URL: ").strip()
#         yt = YouTube(url,on_progress_callback=progress_callback)
#         option= input("Choose your option (1 for video 2 for audio only | Default is 1): ")
#         if option=="1":
#             video =  yt.streams.get_highest_resolution()
#             video.download()
#             print(f"Downloaded: {yt.title}")
#         elif option=="2":
#             audio = yt.streams.get_audio_only()
#             audio.download()
#             print(f"Downloaded: {yt.title}")
#         else:
#             video =  yt.streams.get_highest_resolution()
#             video.download()
#             print(f"Downloaded: {yt.title}")
#     # except Exception:
#     #     pass
#     except KeyboardInterrupt:
#         print("\nExiting...")
#         break

import yt_dlp
while True:
    try:
        url = input("Enter YouTube URL: ").strip()
        option = input("Choose your option (1 for video, 2 for audio only | Default 1): ").strip() or "1"
        ydl_opts = {}
        if option == "2":
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': '%(title)s.%(ext)s',
                'progress_hooks': [lambda d: print(f"{d['_percent_str']} downloaded", end='\r') if d['status'] == 'downloading' else None]
            }
        else:
            ydl_opts = {
                'format': 'bestvideo+bestaudio/best',
                'outtmpl': '%(title)s.%(ext)s',
                'merge_output_format': 'mp4',
                'progress_hooks': [lambda d: print(f"{d['_percent_str']} downloaded", end='\r') if d['status'] == 'downloading' else None]
            }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception:
        pass
    except KeyboardInterrupt:
        print("\nExiting...")
        break
