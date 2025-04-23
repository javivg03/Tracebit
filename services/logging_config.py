import logging

# Configuración básica
logging.basicConfig(
    level=logging.INFO,  # Cambia a DEBUG para más detalle
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.StreamHandler(),  # Muestra en consola
        logging.FileHandler("logs/app.log", encoding="utf-8")  # Guarda en archivo
    ]
)

logger = logging.getLogger("fct_scraper")
