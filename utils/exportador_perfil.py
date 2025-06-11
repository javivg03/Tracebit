from exports.exporter import exportar_resultados_a_excel, exportar_resultados_a_csv
from services.logging_config import logger
from utils.history import guardar_historial
from typing import Callable

async def ejecutar_scraping_y_exportar(
    username: str,
    redes: list[str],
    flujo_scraping: Callable,
) -> dict:
    """
    Ejecuta un scraping de perfil multired + genera archivos Excel y CSV de forma automática.

    Args:
        username (str): El nombre de usuario a scrapear.
        redes (list[str]): Lista de redes por las que pasará el flujo multired.
        flujo_scraping (Callable): La función de scraping multired (como flujo_scraping_multired).

    Returns:
        dict: Resultado del scraping extendido con 'excel_path' y 'csv_path'.
    """
    resultado = await flujo_scraping(
        username=username,
        redes=redes,
    )

    if not resultado:
        logger.warning(f"❌ No se encontraron datos válidos para {username}")
        guardar_historial(
            plataforma="multired",
            username=username,
            status="sin datos útiles",
            archivo=""
        )
        return {"error": "No se encontró ningún dato válido."}

    nombre_archivo = f"perfil_{username}"
    excel_path = exportar_resultados_a_excel([resultado], nombre_archivo)
    csv_path = exportar_resultados_a_csv([resultado], nombre_archivo)

    if not excel_path or not csv_path:
        logger.warning(f"⚠️ No se generaron correctamente los archivos para {username}")
        guardar_historial(
            plataforma="multired",
            username=username,
            status="error en exportación",
            archivo=""
        )
        return {
            **resultado,
            "excel_path": None,
            "csv_path": None
        }

    guardar_historial(
        plataforma="multired",
        username=username,
        status="perfil extraído correctamente",
        archivo=f"{nombre_archivo}.xlsx"
    )

    return {
        **resultado,
        "excel_path": f"/descargar/{nombre_archivo}.xlsx",
        "csv_path": f"/descargar/{nombre_archivo}.csv"
    }
