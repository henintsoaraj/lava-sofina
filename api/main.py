from fastapi import FastAPI
import requests
import os
from urllib.parse import urljoin
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
ICECAST_URL = os.getenv("ICECAST_URL")
stats_json = urljoin(ICECAST_URL, "/status-json.xsl")



@app.get("/now-playing")
def now_playing():
    response = requests.get(stats_json)
    data = response.json()

    source = data["icestats"]["source"]
    title = source.get("title", "Aucun titre")
    listener = source.get("listeners", 0)
    return {
        "title": title,
        "listener": listener
    }
