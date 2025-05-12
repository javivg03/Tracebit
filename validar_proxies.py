from services.proxy_loader import convertir_txt_a_json
from services.proxy_pool import ProxyPool
from services.logging_config import logger

if __name__ == "__main__":
    logger.info("🔄 Iniciando preparación de proxies...")

    # Paso 1: Convertir raw_proxies.txt a proxies.json
    convertir_txt_a_json()

    # Paso 2: Validar proxies y guardar solo los válidos
    pool = ProxyPool(validar_al_cargar=True)

    # Paso 3: Mostrar resumen
    total_validos = len(pool.proxies)
    logger.info(f"✅ Proceso completo. Proxies válidos listos: {total_validos}")
