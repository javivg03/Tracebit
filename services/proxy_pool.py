import json
import random
from typing import List, Optional, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed
from services.proxy_checker import check_proxy
from services.logging_config import logger

PROXY_FILE = "services/proxies.json"

class ProxyPool:
    def __init__(self, proxy_file: str = PROXY_FILE, validar_al_cargar: bool = False, max_threads: int = 20):
        self.proxy_file = proxy_file
        self.max_threads = max_threads
        self.proxies: List[Dict] = []  # Ahora cada proxy es un diccionario
        self.load_proxies()

        if validar_al_cargar:
            self.validate_all()

    def load_proxies(self):
        try:
            with open(self.proxy_file, "r", encoding="utf-8") as f:
                self.proxies = json.load(f)  # ya no usamos .get("proxies")
                logger.info(f"[ProxyPool] {len(self.proxies)} proxies cargados desde '{self.proxy_file}'")
        except (FileNotFoundError, json.JSONDecodeError):
            logger.warning("[ProxyPool] Archivo de proxies no encontrado o corrupto.")
            self.proxies = []

    def save_proxies(self):
        with open(self.proxy_file, "w", encoding="utf-8") as f:
            json.dump(self.proxies, f, indent=4)

    def validate_all(self):
        logger.info("[ProxyPool] Validando proxies en paralelo...")
        valid_proxies = []

        with ThreadPoolExecutor(max_workers=self.max_threads) as executor:
            future_to_proxy = {executor.submit(check_proxy, proxy): proxy for proxy in self.proxies}
            for future in as_completed(future_to_proxy):
                proxy = future_to_proxy[future]
                try:
                    if future.result():
                        valid_proxies.append(proxy)
                except Exception as e:
                    logger.error(f"[ProxyPool] Error validando proxy {proxy}: {e}")

        self.proxies = valid_proxies
        self.save_proxies()
        logger.info(f"[ProxyPool] ✅ Proxies válidos: {len(valid_proxies)}")

    def get_random_proxy(self) -> Optional[Dict]:
        if not self.proxies:
            logger.warning("[ProxyPool] No hay proxies disponibles. Intentando recargar...")
            self.load_proxies()
            if not self.proxies:
                logger.error("[ProxyPool] No hay proxies disponibles tras recarga.")
                return None
        return random.choice(self.proxies)

    def remove_proxy(self, proxy: Dict):
        if proxy in self.proxies:
            self.proxies.remove(proxy)
            self.save_proxies()
            logger.info(f"[ProxyPool] Proxy eliminado: {proxy['ip']}:{proxy['port']}")

    def add_proxies(self, new_proxies: List[Dict]):
        count_before = len(self.proxies)
        for p in new_proxies:
            if p not in self.proxies:
                self.proxies.insert(0, p)
        count_after = len(self.proxies)
        logger.info(f"[ProxyPool] Añadidos {count_after - count_before} nuevos proxies.")
        self.save_proxies()
