from exports.exporter import exportar_resultados_a_excel, exportar_resultados_a_csv
from services.logging_config import logger
from typing import Callable

async def ejecutar_scraping_y_exportar(
    username: str,
    redes: list[str],
    flujo_scraping: Callable,
    habilitar_busqueda_web: bool = False
) -> dict:
    """
    Ejecuta un scraping de perfil multired + genera archivos Excel y CSV de forma automática.

    Args:
        username (str): El nombre de usuario a scrapear.
        redes (list[str]): Lista de redes por las que pasará el flujo multired.
        flujo_scraping (Callable): La función de scraping multired (como flujo_scraping_multired).
        habilitar_busqueda_web (bool): Si se activa o no la búsqueda cruzada web.

    Returns:
        dict: Resultado del scraping extendido con 'excel_path' y 'csv_path'.
    """
    resultado = await flujo_scraping(
        username=username,
        redes=redes,
        habilitar_busqueda_web=habilitar_busqueda_web
    )

    if not resultado:
        logger.warning(f"❌ No se encontraron datos válidos para {username}")
        return {"error": "No se encontró ningún dato válido."}

    nombre_archivo = f"perfil_{username}"
    excel_path = exportar_resultados_a_excel([resultado], nombre_archivo)
    csv_path = exportar_resultados_a_csv([resultado], nombre_archivo)

    if not excel_path or not csv_path:
        logger.warning(f"⚠️ No se generaron correctamente los archivos para {username}")

    return {
        **resultado,
        "excel_path": f"/download/{nombre_archivo}.xlsx" if excel_path else None,
        "csv_path": f"/download/{nombre_archivo}.csv" if csv_path else None
    }
