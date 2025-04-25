import json
import random
from typing import List, Optional
from services.proxy_checker import check_proxy
from services.logging_config import logger

PROXY_FILE = "services/proxies.json"


class ProxyPool:
    def __init__(self, proxy_file: str = PROXY_FILE, validar_al_cargar: bool = False):
        self.proxy_file = proxy_file
        self.proxies: List[str] = []
        self.load_proxies()

        if validar_al_cargar:
            self.validate_all()

    def load_proxies(self):
        try:
            with open(self.proxy_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.proxies = data.get("proxies", [])
        except (FileNotFoundError, json.JSONDecodeError):
            self.proxies = []

    def save_proxies(self):
        with open(self.proxy_file, "w", encoding="utf-8") as f:
            json.dump({"proxies": self.proxies}, f, indent=4)

    def validate_all(self):
        """Valida todos los proxies usando proxy_checker y guarda solo los válidos."""
        logger.info("[ProxyPool] Validando proxies...")
        valid_proxies = [p for p in self.proxies if check_proxy(p)]
        self.proxies = valid_proxies
        self.save_proxies()
        logger.info(f"[ProxyPool] Proxies válidos: {len(valid_proxies)}")

    def get_random_proxy(self) -> Optional[str]:
        if not self.proxies:
            return None
        return random.choice(self.proxies)

    def remove_proxy(self, proxy: str):
        if proxy in self.proxies:
            self.proxies.remove(proxy)
            self.save_proxies()
            logger.info(f"[ProxyPool] Proxy eliminado: {proxy}")

    def add_proxies(self, new_proxies: List[str]):
        """Agrega nuevos proxies, evitando duplicados, y los guarda."""
        for p in new_proxies:
            if p not in self.proxies:
                self.proxies.append(p)
        self.save_proxies()
