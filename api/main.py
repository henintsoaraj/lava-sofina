from fastapi import FastAPI
import requests
import os
from urllib.parse import urljoin

app = FastAPI()
ICECAST_URL = os.getenv("ICECAST_URL")
stats_json = urljoin(ICECAST_URL, "/status-json.xsl")

@app.get("/now-playing")
def now_playing():
    response = requests.get(stats_json)
    data = response.json()

    source = data["icestats"]["source"]
    title = source["title"]
    listener = source["listeners"]
    return {
        "title": title,
        "listener": listener
    }
