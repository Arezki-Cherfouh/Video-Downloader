# import tkinter as tk
# from tkinter import filedialog
# from pytube import YouTube
# mn=tk.Tk()
# mn.title('Youtube video downloader')
# mn.geometry('900x200')
# hl=tk.Label(mn,text="Url :")
# hl.place(x=20,y=20)
# h=tk.Entry(mn,width="90")
# h.place(x=60,y=20)
# hl=tk.Label(mn,text="Option (1:Video 2:Audio):")
# hl.place(x=20,y=50)
# w=tk.Entry(mn)
# w.place(x=220,y=50)
# def work():
#     try:
#         url = h.get().strip()
#         yt = YouTube(url)
#         option= w.get()
#         download_path = filedialog.askdirectory(title="Select Download Folder")
#         if option=="1":
#             video = yt.streams.get_highest_resolution()
#             video.download(output_path=download_path)
#             print(f"Downloaded: {yt.title}")
#         elif option=="2":
#             audio = yt.streams.get_audio_only()
#             audio.download(output_path=download_path)
#             print(f"Downloaded: {yt.title}")
#         else:
#             video = yt.streams.get_highest_resolution()
#             video.download(output_path=download_path)
#             print(f"Downloaded: {yt.title}")
#     except ValueError:
#         return
# b=tk.Button(mn,text="Proceed",command=lambda:work(),cursor="hand2")
# b.place(x=700,y=125)
# mn.mainloop()
import tkinter as tk
from tkinter import filedialog
import yt_dlp
import pygame
import os
pygame.init()
pygame.mixer.init()
pygame.mixer.music.load(os.path.join(os.path.dirname(__file__), "finish.mp3"))
mn = tk.Tk()
mn.title('Youtube video downloader')
mn.geometry('900x200')

hl = tk.Label(mn, text="Url :")
hl.place(x=20, y=20)
h = tk.Entry(mn, width="90")
h.place(x=60, y=20)

hl2 = tk.Label(mn, text="Option (1:Video 2:Audio):")
hl2.place(x=20, y=50)
w = tk.Entry(mn)
w.place(x=220, y=50)
progress_label = tk.Label(mn, text="", anchor='w')
progress_label.place(x=20, y=90, width=860)
def progress_hook(d):
    if d['status'] == 'downloading':
        percent = d.get('downloaded_bytes', 0) / d.get('total_bytes', 1) * 100
        speed = d.get('speed', 0)
        if speed:
            if speed > 1024**2:
                speed_str = f"{speed/1024**2:.2f} MiB/s"
            elif speed > 1024:
                speed_str = f"{speed/1024:.2f} KiB/s"
            else:
                speed_str = f"{speed:.2f} B/s"
        else:
            speed_str = "N/A"
        eta = d.get('eta')
        if eta:
            minutes, seconds = divmod(eta, 60)
            eta_str = f"{minutes:02d}:{seconds:02d}"
        else:
            eta_str = "N/A"
        progress_label.config(text=f"Downloading: {percent:.1f}% at {speed_str}, ETA {eta_str}")
    elif d['status'] == 'finished':
        progress_label.config(text="Merging and finishing download...")
    mn.update()
def work():
    url = h.get().strip()
    option = w.get().strip()
    progress_label.config(text="")
    if not url:
        progress_label.config(text="Please enter a URL")
        return

    download_path = filedialog.askdirectory(title="Select Download Folder")
    if not download_path:
        progress_label.config(text="Please select a download folder")
        return
    progress_label.config(text="Downloading...")
    mn.update()
    ydl_opts = {}

    if option == "2":
        progress_label.config(text="Downloading Audio...")
        mn.update()
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f'{download_path}/%(title)s.%(ext)s',
            'progress_hooks': [progress_hook]
        }
    else:
        progress_label.config(text="Downloading Video...")
        mn.update()
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'outtmpl': f'{download_path}/%(title)s.%(ext)s',
            'merge_output_format': 'mp4',
            'progress_hooks': [progress_hook]
        }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        progress_label.config(text="Download finished!")
        pygame.mixer.music.play()
    except Exception as e:
        print("Error:", e)
b = tk.Button(mn, text="Proceed", command=lambda:work(), cursor="hand2")
b.place(x=700, y=125)
mn.mainloop()
