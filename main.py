from fastapi import FastAPI, UploadFile, File
from fastapi.staticfiles import StaticFiles
import subprocess
import uuid
import os
import shutil

app = FastAPI()

OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Servir arquivos públicos via /output/
app.mount("/output", StaticFiles(directory=OUTPUT_DIR), name="output")

@app.post("/compor")
async def compor_video(
    video: UploadFile = File(...),
    audio: UploadFile = File(...)
):
    id = str(uuid.uuid4())
    video_path = f"{OUTPUT_DIR}/{id}_video.mp4"
    audio_path = f"{OUTPUT_DIR}/{id}_audio.wav"
    final_path = f"{OUTPUT_DIR}/{id}_final.mp4"

    with open(video_path, "wb") as f:
        shutil.copyfileobj(video.file, f)

    with open(audio_path, "wb") as f:
        shutil.copyfileobj(audio.file, f)

    try:
        subprocess.run([
            "ffmpeg", "-i", video_path, "-i", audio_path,
            "-c:v", "copy", "-map", "0:v:0", "-map", "1:a:0",
            "-shortest", final_path, "-y"
        ], check=True)

        return {
            "status": "ok",
            "url": f"/output/{id}_final.mp4"
        }
    except subprocess.CalledProcessError as e:
        return {"status": "erro", "mensagem": str(e)}
