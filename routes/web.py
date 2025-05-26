from fastapi import APIRouter, Body
from pydantic import BaseModel
from scraping.web.web_scraper import buscar_por_nombre, buscar_por_palabra_clave
from services.logging_config import logger

router_web = APIRouter(prefix="/web")

# Modelos
class WebPerfilInput(BaseModel):
    username: str
    nombre_completo: str | None = None

class WebPalabraClaveInput(BaseModel):
    query: str
    max_resultados: int = 5

# Endpoints

@router_web.post("/perfil")
async def web_scraper_perfil(data: WebPerfilInput = Body(...)):
    logger.info(f"📥 Endpoint recibido: Búsqueda web por username → {data.username}")
    resultado = buscar_por_nombre(data.username, data.nombre_completo)
    return {
        "estado": "ok",
        "data": resultado,
        "excel_path": None,
        "csv_path": None
    }


@router_web.post("/buscar")
async def web_scraper_busqueda(data: WebPalabraClaveInput = Body(...)):
    logger.info(f"📥 Endpoint recibido: Búsqueda web por palabra clave → {data.query}")
    resultados = buscar_por_palabra_clave(data.query, data.max_resultados)
    return {
        "estado": "ok",
        "data": resultados,
        "excel_path": None,
        "csv_path": None
    }
