from fastapi import APIRouter
from pydantic import BaseModel
from services.logging_config import logger
from utils.flujo_scraping import flujo_scraping_multired
from utils.exportador_perfil import ejecutar_scraping_y_exportar
from tasks.instagram import scrape_followers_info_task, scrape_followees_info_task
from utils.history import fue_scrapeado_recentemente
from fastapi.responses import JSONResponse

router_instagram = APIRouter(prefix="/instagram")

# ========== Pydantic Models ==========

class InstagramPerfilInput(BaseModel):
    username: str

class SeguidoresInput(BaseModel):
    username: str
    max_seguidores: int = 10

class SeguidosInput(BaseModel):
    username: str
    max_seguidos: int = 10

# ========== Endpoints ==========

@router_instagram.post("/perfil")
async def instagram_scraper(data: InstagramPerfilInput):
    logger.info(f"📥 Endpoint recibido: Scraping de perfil Instagram para {data.username}")

    return await ejecutar_scraping_y_exportar(
        username=data.username,
        redes=["instagram", "tiktok", "facebook", "x"],
        flujo_scraping=flujo_scraping_multired,
    )

@router_instagram.post("/seguidores")
def lanzar_scraping_info_seguidores(data: SeguidoresInput):
    if fue_scrapeado_recentemente(data.username, "instagram", tipo="seguidores", nueva_cantidad=data.max_seguidores):
        logger.warning(f"🚫 Ya se scrapearon {data.max_seguidores} o menos seguidores de {data.username} recientemente.")
        return JSONResponse(
            status_code=400,
            content={
                "estado": "duplicado",
                "mensaje": "Este scraping ya fue realizado con esa cantidad o menor en las últimas 24h. La cantidad debe ser mayor."
            }
        )
    tarea = scrape_followers_info_task.delay(data.username, data.max_seguidores)
    logger.info(f"📨 Petición recibida para scrapear seguidores de {data.username}")
    return {"mensaje": "Scraping completo de seguidores en curso", "tarea_id": tarea.id}

@router_instagram.post("/seguidos")
def lanzar_scraping_info_seguidos(data: SeguidosInput):
    if fue_scrapeado_recentemente(data.username, "instagram", tipo="seguidos", nueva_cantidad=data.max_seguidos):
        logger.warning(f"🚫 Ya se scrapearon {data.max_seguidos} o menos seguidos de {data.username} recientemente.")
        return JSONResponse(
            status_code=400,
            content={
                "estado": "duplicado",
                "mensaje": "Este scraping ya fue realizado con esa cantidad o menor en las últimas 24h. La cantidad debe ser mayor."
            }
        )
    tarea = scrape_followees_info_task.delay(data.username, data.max_seguidos)
    logger.info(f"📨 Petición recibida para scrapear seguidos de {data.username}")
    return {"mensaje": "Scraping completo de seguidos en curso", "tarea_id": tarea.id}