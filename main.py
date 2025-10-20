from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, StreamingResponse,FileResponse
import yt_dlp, base64, io, os, threading, queue, re
app = FastAPI()
@app.get("/favicon")
async def favicon():
    if os.path.exists("favicon.png"):
        print("Exists")
        return FileResponse("favicon.png")
    print("404")
    return {"error": "favicon not found"}
@app.get("/", response_class=HTMLResponse)
async def home():
    return HTMLResponse("""
    <html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Downloader • Qwerify</title><meta name="description" content="Download videos or audio instantly with Qwerify Downloader. Fast, simple, and built with a clean interface for maximum efficiency."><meta name="keywords" content="Qwerify, downloader, YouTube, video, audio, mp3, mp4, fast, simple, converter"><meta property="og:site_name" content="Qwerify"><meta property="og:title" content="Downloader • Qwerify"><meta property="og:description" content="Download videos or audio instantly with Qwerify Downloader. Fast, simple, and built with a clean interface for maximum efficiency."><link rel="icon" href="/favicon" type="image/x-icon"><style>
    body{background:#222;color:#eee;font-family:sans-serif;padding:40px;text-align:center;}
    input,select,button{padding:10px;border-radius:8px;margin-top:10px;font-size:1em;}
    video,audio{width:100%;max-width:800px;margin-top:20px;border-radius:12px;}
    .download,.df{background:rgb(52,231,52);transition:transform 0.1s;}
    .opt{background:red;}
    .bar{width:100%;max-width:800px;height:20px;background:#555;border-radius:10px;overflow:hidden;margin:20px auto;}
    .progress{width:0;height:100%;background:lime;transition:width 0.2s;}
    @media (min-width:1025px){.download:hover,.df:hover{transform:scale(1.03)}.download,.df{cursor:pointer;}.opt{cursor:pointer;}}
    .download:active,.df:active{transform:scale(0.9);}
    </style></head><body>
    <h2>Video Downloader</h2>
    <div style="display:grid;grid-template-columns:80% 1fr 1fr;column-gap:5px;margin:auto;">
    <input class="url" placeholder="YouTube URL">
    <select class="opt"><option value="1">Video</option><option value="2">Audio</option></select>
    <button class="download">Proceed</button></div>
    <div class="bar"><div class="progress"></div></div>
    <div class="result"></div>
    <script>
    const btn=document.querySelector('.download'),bar=document.querySelector('.progress')
    btn.onclick=async()=>{
        const url=document.querySelector('.url').value,opt=document.querySelector('.opt').value
        if(!url)return alert('Enter URL')
        bar.style.width='0%'
        const res=await fetch('/download',{method:'POST',body:new URLSearchParams({url,opt})})
        const reader=res.body.getReader(),decoder=new TextDecoder()
        let full=''
        while(true){
            const {done,value}=await reader.read()
            if(done)break
            const chunk=decoder.decode(value)
            full+=chunk
            const p=chunk.match(/PROGRESS:(\\d+)/)
            if(p)bar.style.width=p[1]+'%'
        }
        const parts=full.split('DATA:')
        if(parts[1])document.querySelector('.result').innerHTML=parts[1]
    }
    </script></body></html>
    """)
@app.post("/download")
async def download(url: str = Form(...), opt: str = Form(...)):
    q=queue.Queue()
    def hook(d):
        if d['status']=='downloading':
            raw=d.get('_percent_str','0%')
            clean=re.sub(r'\\x1b\\[[0-9;]*m','',raw).replace('%','').strip()
            try:p=int(float(clean))
            except:p=0
            q.put(f"PROGRESS:{p}\n")
    def worker():
        try:
            tmpfile='temp.mp4' if opt=='1' else 'temp.mp3'
            if os.path.exists(tmpfile):os.remove(tmpfile)
            ydl_opts={'format':'bestaudio/best' if opt=='2' else 'bestvideo+bestaudio/best','outtmpl':tmpfile,'merge_output_format':'mp4','quiet':True,'progress_hooks':[hook],'noprogress':True,'no_color':True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:info=ydl.extract_info(url,download=True)
            with open(tmpfile,'rb')as f:data=f.read()
            os.remove(tmpfile)
            encoded=base64.b64encode(data).decode()
            mime='audio/mpeg'if opt=='2'else'video/mp4'
            ext='mp3'if opt=='2'else'mp4'
            title=info.get('title','file').replace(' ','_')+f'.{ext}'
            tag=f'<audio controls src="data:{mime};base64,{encoded}"></audio>'if opt=='2'else f'<video controls src="data:{mime};base64,{encoded}"></video>'
            q.put(f"DATA:<div style='text-align:center'><p>Downloaded: {title}</p>{tag}<br><a href='data:{mime};base64,{encoded}' download='{title}'><button class=\"df\" style='margin-top:15px;padding:10px 20px;border:none;border-radius:8px;background:rgb(52,231,52);font-size:1em;'>Download File</button></a></div>")
        except Exception as e:q.put(f"DATA:<p>Error: {e}</p>")
        q.put(None)
    threading.Thread(target=worker,daemon=True).start()
    def stream():
        while True:
            msg=q.get()
            if msg is None:break
            yield msg
    return StreamingResponse(stream(),media_type='text/plain')
