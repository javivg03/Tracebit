import requests
from services.user_agents import random_user_agent

def probar_user_agent(username):
    url = f"https://www.instagram.com/{username}/"
    headers = {
        "User-Agent": random_user_agent()
    }

    response = requests.get(url, headers=headers)

    print("🔍 Status:", response.status_code)
    print("🔐 User-Agent usado:", headers["User-Agent"])
    print("📄 Contenido parcial:", response.text[:500])  # Solo los primeros 500 caracteres
