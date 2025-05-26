import pandas as pd
from services.logging_config import logger

def exportar_resultados_a_excel(data_list: list[dict], nombre_archivo: str) -> str | None:
    try:
        ruta = f"exports/{nombre_archivo}.xlsx"
        df = pd.DataFrame(data_list)
        df.to_excel(ruta, index=False)
        logger.info(f"📁 Archivo exportado correctamente: {ruta}")
        return ruta
    except Exception as e:
        logger.warning(f"❌ Error al exportar a Excel '{nombre_archivo}': {e}")
        return None

def exportar_resultados_a_csv(data_list: list[dict], nombre_archivo: str) -> str | None:
    try:
        ruta = f"exports/{nombre_archivo}.csv"
        df = pd.DataFrame(data_list)
        df.to_csv(ruta, index=False)
        logger.info(f"📁 Archivo CSV exportado: {ruta}")
        return ruta
    except Exception as e:
        logger.warning(f"❌ Error al exportar a CSV '{nombre_archivo}': {e}")
        return None
