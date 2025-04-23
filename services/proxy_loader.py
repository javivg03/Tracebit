import json
from services.proxy_checker import check_proxy

def convert_txt_to_json(txt_path="services/raw_proxies.txt", json_path="services/proxies.json"):
    with open(txt_path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    proxies = ["http://" + line if not line.startswith("http") else line for line in lines]
    proxies_validos = []

    print(f"[Loader] Validando {len(proxies)} proxies...")

    for proxy in proxies:
        if check_proxy(proxy):
            proxies_validos.append(proxy)

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({"proxies": proxies_validos}, f, indent=4)

    print(f"[Loader] ✅ {len(proxies_validos)} proxies válidos guardados en '{json_path}'")
    print(f"[Loader] ❌ {len(proxies) - len(proxies_validos)} proxies descartados")

if __name__ == "__main__":
    convert_txt_to_json()
