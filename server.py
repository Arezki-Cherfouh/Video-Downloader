# from fastapi import FastAPI, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel
# import yt_dlp
# import asyncio
# from typing import Optional

# app = FastAPI()

# # Enable CORS for frontend
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# class DownloadRequest(BaseModel):
#     url: str
#     opt: str  # "1" for video, "2" for audio

# class DownloadResponse(BaseModel):
#     title: str
#     download_url: str
#     thumbnail: Optional[str] = None
#     duration: Optional[int] = None
#     filesize: Optional[str] = None

# @app.get("/")
# def read_root():
#     return {"message": "Video Downloader API - Use POST /download to get video/audio URLs"}

# @app.post("/download", response_model=DownloadResponse)
# async def get_download_url(request: DownloadRequest):
#     try:
#         url = request.url
#         opt = request.opt
        
#         if not url:
#             raise HTTPException(status_code=400, detail="URL is required")
        
#         # Configure yt-dlp options - extract info only, no download
#         ydl_opts = {
#             'quiet': True,
#             'no_warnings': True,
#             'skip_download': True,  # Don't download, just get info
#         }
        
#         # Select format based on option
#         if opt == "2":  # Audio
#             ydl_opts['format'] = 'bestaudio/best'
#         else:  # Video
#             ydl_opts['format'] = 'best'
        
#         # Extract video information
#         with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#             info = await asyncio.to_thread(ydl.extract_info, url, download=False)
            
#             title = info.get('title', 'Unknown')
#             thumbnail = info.get('thumbnail')
#             duration = info.get('duration')
            
#             # Get direct download URL
#             if opt == "2":  # Audio
#                 # Find best audio format
#                 formats = info.get('formats', [])
#                 audio_formats = [f for f in formats if f.get('acodec') != 'none' and f.get('vcodec') == 'none']
#                 if audio_formats:
#                     best_audio = max(audio_formats, key=lambda x: x.get('abr', 0) or 0)
#                     download_url = best_audio.get('url')
#                     filesize = best_audio.get('filesize_approx') or best_audio.get('filesize')
#                 else:
#                     download_url = info.get('url')
#                     filesize = info.get('filesize_approx') or info.get('filesize')
#             else:  # Video
#                 download_url = info.get('url')
#                 filesize = info.get('filesize_approx') or info.get('filesize')
            
#             # Format filesize
#             filesize_str = None
#             if filesize:
#                 if filesize > 1024 * 1024 * 1024:
#                     filesize_str = f"{filesize / (1024**3):.2f} GB"
#                 elif filesize > 1024 * 1024:
#                     filesize_str = f"{filesize / (1024**2):.2f} MB"
#                 else:
#                     filesize_str = f"{filesize / 1024:.2f} KB"
            
#             return DownloadResponse(
#                 title=title,
#                 download_url=download_url,
#                 thumbnail=thumbnail,
#                 duration=duration,
#                 filesize=filesize_str
#             )
            
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error processing URL: {str(e)}")

# @app.get("/health")
# def health_check():
#     return {"status": "healthy"}

# # if __name__ == "__main__":
# #     import uvicorn
# #     # Install: pip install fastapi uvicorn yt-dlp
# #     uvicorn.run(app, host="0.0.0.0", port=8000)
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import yt_dlp
import asyncio
from typing import Optional

app = FastAPI()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class DownloadRequest(BaseModel):
    url: str
    opt: str  # "1" for video, "2" for audio

class DownloadResponse(BaseModel):
    title: str
    download_url: str
    thumbnail: Optional[str] = None
    duration: Optional[int] = None
    filesize: Optional[str] = None
    format_note: Optional[str] = None

@app.get("/")
def read_root():
    return {"message": "Video Downloader API - Use POST /download to get video/audio URLs"}

@app.post("/download", response_model=DownloadResponse)
async def get_download_url(request: DownloadRequest):
    try:
        url = request.url
        opt = request.opt
        
        if not url:
            raise HTTPException(status_code=400, detail="URL is required")
        
        # Configure yt-dlp options
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,
        }
        
        # Select format - prioritize MP4 and non-streaming formats
        if opt == "2":  # Audio
            ydl_opts['format'] = 'bestaudio[ext=m4a]/bestaudio[ext=mp3]/bestaudio'
        else:  # Video
            # Prioritize MP4 format and avoid HLS streams
            ydl_opts['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
        
        # Extract video information
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = await asyncio.to_thread(ydl.extract_info, url, download=False)
            
            title = info.get('title', 'Unknown')
            thumbnail = info.get('thumbnail')
            duration = info.get('duration')
            
            # Get the best format that's not HLS/m3u8
            formats = info.get('formats', [])
            
            if opt == "2":  # Audio
                # Filter audio-only formats, exclude m3u8
                audio_formats = [
                    f for f in formats 
                    if f.get('acodec') != 'none' 
                    and f.get('vcodec') == 'none'
                    and not f.get('url', '').endswith('.m3u8')
                    and f.get('protocol') not in ['m3u8', 'm3u8_native']
                ]
                
                if audio_formats:
                    # Sort by audio bitrate
                    best_format = max(audio_formats, key=lambda x: x.get('abr', 0) or 0)
                else:
                    # Fallback to any audio format
                    best_format = None
                    for f in formats:
                        if f.get('acodec') != 'none' and not f.get('url', '').endswith('.m3u8'):
                            best_format = f
                            break
                    
                    if not best_format:
                        raise HTTPException(status_code=400, detail="No suitable audio format found")
                
                download_url = best_format.get('url')
                filesize = best_format.get('filesize') or best_format.get('filesize_approx')
                format_note = best_format.get('format_note', 'audio')
                
            else:  # Video
                # Filter MP4 video formats, exclude m3u8
                video_formats = [
                    f for f in formats 
                    if f.get('vcodec') != 'none'
                    and f.get('ext') == 'mp4'
                    and not f.get('url', '').endswith('.m3u8')
                    and f.get('protocol') not in ['m3u8', 'm3u8_native', 'http_dash_segments']
                ]
                
                if video_formats:
                    # Get format with both video and audio, or best video
                    combined_formats = [f for f in video_formats if f.get('acodec') != 'none']
                    if combined_formats:
                        best_format = max(combined_formats, key=lambda x: x.get('height', 0) or 0)
                    else:
                        best_format = max(video_formats, key=lambda x: x.get('height', 0) or 0)
                else:
                    # Fallback to requested_formats if available
                    if info.get('requested_formats'):
                        # Get the video part of combined format
                        video_part = info['requested_formats'][0]
                        if not video_part.get('url', '').endswith('.m3u8'):
                            best_format = video_part
                        else:
                            raise HTTPException(status_code=400, detail="Only streaming formats available")
                    else:
                        raise HTTPException(status_code=400, detail="No suitable video format found")
                
                download_url = best_format.get('url')
                filesize = best_format.get('filesize') or best_format.get('filesize_approx')
                format_note = f"{best_format.get('height', '?')}p"
            
            # Format filesize
            filesize_str = None
            if filesize:
                if filesize > 1024 * 1024 * 1024:
                    filesize_str = f"{filesize / (1024**3):.2f} GB"
                elif filesize > 1024 * 1024:
                    filesize_str = f"{filesize / (1024**2):.2f} MB"
                else:
                    filesize_str = f"{filesize / 1024:.2f} KB"
            
            return DownloadResponse(
                title=title,
                download_url=download_url,
                thumbnail=thumbnail,
                duration=duration,
                filesize=filesize_str,
                format_note=format_note
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing URL: {str(e)}")

@app.get("/health")
def health_check():
    return {"status": "healthy"}

# if __name__ == "__main__":
#     import uvicorn
#     # Install: pip install fastapi uvicorn yt-dlp
#     uvicorn.run(app, host="0.0.0.0", port=8000)