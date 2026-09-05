import socket
import os
from google import genai
import asyncio
import edge_tts
import requests



client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
LIQUIDSOAP = os.getenv("LIQUIDSOAP_HOST", "liquidsoap")
CHEMIN_DE_SORTIE = os.getenv("CHEMIN_DE_SORTIE","/dj-audio/" )

def generate_text():
    weather = get_weather()
    meteo = interpreter_meteo(weather["weather_code"])
    temp = weather["temperature_2m"]
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=f"""Tu es l'animateur d'une radio en ligne, chaleureux et concis.
Génère une seule phrase courte (15 mots maximum), en français,
pour faire une transition sympa entre deux morceaux de musique.
Pas de bonjour, pas de nom de radio, juste une phrase naturelle
et vivante, comme si tu parlais en direct en énonçant la météo, le temps qu'il fait {meteo} et la température {temp}"""
    )
    return response.text

async def generate_speech(text, output_file=CHEMIN_DE_SORTIE+"output.mp3"):
    voice = "fr-FR-DeniseNeural"  # une voix française
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_file)
    return output_file

def send_to_liquidsoap(dj_audio):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    client_socket.connect((LIQUIDSOAP, 1234))
    audio = "dj.push "+dj_audio+"\n"
    client_socket.send(audio.encode())
    response = client_socket.recv(1024).decode()

    client_socket.close()

def get_weather():
    url = "https://api.open-meteo.com/v1/forecast?latitude=48.8566&longitude=2.3522&current=temperature_2m,weather_code"
    response = requests.get(url)
    data = response.json()
    return data["current"]

def interpreter_meteo(code):
    sign_code = {
         # Ciel et nuages
    0: "Ciel dégagé",
    1: "Plutôt dégagé",
    2: "Partiellement nuageux",
    3: "Couvert",
    
    # Brouillard
    45: "Brouillard",
    48: "Brouillard givrant",
    
    # Bruine
    51: "Bruine légère",
    53: "Bruine modérée",
    55: "Bruine dense",
    56: "Bruine verglaçante légère",
    57: "Bruine verglaçante dense",

    # Pluie
    61: "Pluie faible",
    63: "Pluie modérée",
    65: "Pluie forte",
    66: "Pluie verglaçante légère",
    67: "Pluie verglaçante forte",
    
    # Neige
    71: "Chutes de neige faible",
    73: "Chutes de neige modérée",
    75: "Chutes de neige forte",
    77: "Grains de neige",
    
    # Averses
    80: "Averses de pluie faibles",
    81: "Averses de pluie modérées",
    82: "Averses de pluie violentes",
    85: "Averses de neige faibles",
    86: "Averses de neige fortes",
    
    # Orages
    95: "Orage faible ou modéré",
    96: "Orage avec grêle légère",
    99: "Orage avec grêle forte"
    }
    return sign_code.get(code, "temps changeant")


if __name__ == "__main__":
    my_text = generate_text()
    my_audio = asyncio.run(generate_speech(my_text))
    send_to_liquidsoap(my_audio)