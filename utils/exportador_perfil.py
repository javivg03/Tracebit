from exports.exporter import exportar_resultados_a_excel, exportar_resultados_a_csv
from services.logging_config import logger
from utils.history import guardar_historial, fue_scrapeado_recentemente
from typing import Callable
from fastapi.responses import JSONResponse

async def ejecutar_scraping_y_exportar(
    username: str,
    redes: list[str],
    flujo_scraping: Callable,
) -> dict:
    # ✅ Comprobar duplicado ANTES de lanzar scraping
    if fue_scrapeado_recentemente(username=username, plataforma="multired", tipo="perfil"):
        logger.warning(f"🚫 Perfil {username} ya fue scrapeado recientemente.")
        return JSONResponse(
            status_code=400,
            content={
                "estado": "duplicado",
                "mensaje": "Este perfil ya fue scrapeado hace menos de 24h."
            }
        )
    resultado = await flujo_scraping(username=username, redes=redes)

    if not resultado:
        logger.warning(f"❌ No se encontraron datos válidos para {username}")
        guardar_historial(
            plataforma="multired",
            username=username,
            status="sin datos útiles",
            archivo="",
            tipo="perfil"
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
            archivo="",
            tipo="perfil"
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
        archivo=f"{nombre_archivo}.xlsx",
        tipo="perfil"
    )

    return {
        **resultado,
        "excel_path": f"/descargar/{nombre_archivo}.xlsx",
        "csv_path": f"/descargar/{nombre_archivo}.csv"
    }
