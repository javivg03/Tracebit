import json
import os
from services.logging_config import logger

def convertir_txt_a_json(txt_path="services/raw_proxies.txt", json_path="services/proxies.json"):
    proxies = []

    with open(txt_path, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split(":")
            if len(parts) == 4:
                ip, port, user, password = parts
                proxies.append({
                    "ip": ip,
                    "port": port,
                    "username": user,
                    "password": password,
                    "plataformas_bloqueadas": []
                })
            else:
                logger.warning(f"[ProxyLoader] Formato inválido en línea: {line.strip()}")

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(proxies, f, indent=4)

    logger.info(f"[ProxyLoader] ✅ {len(proxies)} proxies formateados y guardados en '{json_path}'")

def cargar_proxies(json_path="services/proxies.json") -> list:
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            proxies = json.load(f)
            logger.info(f"[ProxyLoader] 🔌 {len(proxies)} proxies cargados desde '{json_path}'")
            return proxies
    except Exception as e:
        logger.error(f"[ProxyLoader] ❌ Error al cargar proxies: {e}")
        return []

import json

def guardar_proxies_formateados(lista_proxies: list[str], modo: str = "replace") -> None:
    """
    Guarda los proxies en formato JSON. Si modo='append', añade sin duplicar.
    Formato esperado: ip:port:user:pass
    """
    proxies_json = []
    for linea in lista_proxies:
        partes = linea.strip().split(":")
        if len(partes) != 4:
            continue
        proxy = {
            "ip": partes[0],
            "port": partes[1],
            "username": partes[2],
            "password": partes[3],
            "plataformas_bloqueadas": []
        }
        proxies_json.append(proxy)

    archivo = "services/proxies.json"

    if modo == "append" and os.path.exists(archivo):
        try:
            with open(archivo, "r", encoding="utf-8") as f:
                existentes = json.load(f)
            # Evitar duplicados exactos
            proxies_json = [p for p in proxies_json if p not in existentes]
            proxies_json = existentes + proxies_json
        except:
            pass  # si falla la lectura, continúa con los nuevos

    with open(archivo, "w", encoding="utf-8") as f:
        json.dump(proxies_json, f, indent=2)

if __name__ == "__main__":
    convertir_txt_a_json()
