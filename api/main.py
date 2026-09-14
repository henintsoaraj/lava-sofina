from fastapi import FastAPI, File, UploadFile, HTTPException, status, Form
import requests
import os
from urllib.parse import urljoin
from fastapi.middleware.cors import CORSMiddleware
import shutil
from pathlib import Path


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
ICECAST_URL = os.getenv("ICECAST_URL")
UPLOAD_PASSWORD = os.getenv("UPLOAD_PASSWORD")
stats_json = urljoin(ICECAST_URL, "/status-json.xsl")
# Dossier où les fichiers importés seront enregistrés
UPLOAD_DIR = Path("/music")
MIME_INTERDITS = ["image/png", "image/jpeg", "text/plain", "application/pdf", "video/mp4"]


@app.get("/now-playing")
def now_playing():
    response = requests.get(stats_json)
    data = response.json()

    source = data["icestats"].get("source", {})
    title = source.get("title", "Aucun titre")
    listener = source.get("listeners", 0)
    return {
        "title": title,
        "listener": listener
    }

@app.post("/upload/")
async def importer_fichier(file: UploadFile = File(...), password: str = Form(...)):
    if password != UPLOAD_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Mot de passe incorrect."
        )
    extension_valide = file.filename.lower().endswith(".mp3")
    mime_suspect = file.content_type in MIME_INTERDITS

    if not extension_valide or mime_suspect:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le fichier doit obligatoirement être au format MP3."
        )
    # 1. Définir le chemin de destination avec le nom d'origine du fichier
    destination = UPLOAD_DIR / file.filename
    
    # 2. Ouvrir le fichier de destination et y copier le contenu du fichier reçu
    with open(destination, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    return {
        "message": "Fichier importé avec succès !",
        "nom_fichier": file.filename,
        "type_contenu": file.content_type
    }
