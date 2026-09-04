import socket
import os
from google import genai
import asyncio
import edge_tts




client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
LIQUIDSOAP = os.getenv("LIQUIDSOAP_HOST", "liquidsoap")
CHEMIN_DE_SORTIE = os.getenv("CHEMIN_DE_SORTIE","/dj-audio/" )

def generate_text():
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents="""Tu es l'animateur d'une radio en ligne, chaleureux et concis.
Génère une seule phrase courte (15 mots maximum), en français,
pour faire une transition sympa entre deux morceaux de musique.
Pas de bonjour, pas de nom de radio, juste une phrase naturelle
et vivante, comme si tu parlais en direct."""
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
    audio = "dj.push.uri "+dj_audio+"\n"
    client_socket.send(audio.encode())
    response = client_socket.recv(1024).decode()

    client_socket.close()

if __name__ == "__main__":
    my_text = generate_text()
    my_audio = asyncio.run(generate_speech(my_text))
    send_to_liquidsoap(my_audio)