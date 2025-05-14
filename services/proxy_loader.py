import json
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

if __name__ == "__main__":
    convertir_txt_a_json()
