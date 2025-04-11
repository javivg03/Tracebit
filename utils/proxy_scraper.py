import requests

def fetch_proxies(proxy_type="http") -> list:
    """
    Descarga proxies desde proxyscrape.com (http, socks4, socks5)
    """
    url = f"https://api.proxyscrape.com/v2/?request=displayproxies&protocol={proxy_type}&timeout=3000&country=all&ssl=all&anonymity=all"

    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            proxy_list = response.text.strip().split("\n")
            proxy_list = [proxy.strip() for proxy in proxy_list if proxy.strip()]
            print(f"[Scraper] {len(proxy_list)} proxies descargados ({proxy_type.upper()})")
            return proxy_list
        else:
            print(f"[Scraper] Error al obtener proxies: {response.status_code}")
            return []
    except Exception as e:
        print(f"[Scraper] Error: {e}")
        return []

def save_to_txt(proxies: list, output_file="utils/raw_proxies.txt"):
    with open(output_file, "w", encoding="utf-8") as f:
        for proxy in proxies:
            f.write(proxy + "\n")
    print(f"[Scraper] Proxies guardados en '{output_file}'")

if __name__ == "__main__":
    # Opciones: http, socks4, socks5
    proxies = fetch_proxies(proxy_type="http")
    save_to_txt(proxies)
