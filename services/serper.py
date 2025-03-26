import os
import requests
from dotenv import load_dotenv

load_dotenv()  # Cargar variables del .env

API_KEY = os.getenv("SERPER_API_KEY")
URL = "https://google.serper.dev/search"

def buscar_en_google(query):
    if not API_KEY:
        raise Exception("⚠️ No se encontró la clave SERPER_API_KEY en el .env")

    headers = {
        "X-API-KEY": API_KEY,
        "Content-Type": "application/json"
    }
    payload = { "q": query }

    response = requests.post(URL, headers=headers, json=payload)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error {response.status_code}: {response.text}")
