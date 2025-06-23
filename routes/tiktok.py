from fastapi import APIRouter
from pydantic import BaseModel
from services.logging_config import logger
from utils.flujo_scraping import flujo_scraping_multired
from utils.exportador_perfil import ejecutar_scraping_y_exportar
from tasks.tiktok import scrape_followers_info_tiktok_task, scrape_followees_info_tiktok_task
from fastapi.responses import JSONResponse
from utils.history import fue_scrapeado_recentemente


router_tiktok = APIRouter(prefix="/tiktok")

# ========== Pydantic Models ==========

class PerfilInput(BaseModel):
    username: str

class SeguidoresInput(BaseModel):
    username: str
    max_seguidores: int = 10

class SeguidosInput(BaseModel):
    username: str
    max_seguidos: int = 10

# ========== Endpoints ==========

@router_tiktok.post("/perfil")
async def tiktok_scraper(data: PerfilInput):
    logger.info(f"📥 Endpoint recibido: Scraping de perfil TikTok para {data.username}")

    return await ejecutar_scraping_y_exportar(
        username=data.username,
        redes=["tiktok", "instagram", "facebook", "x"],
        flujo_scraping=flujo_scraping_multired,
    )

@router_tiktok.post("/seguidores")
def lanzar_scraping_info_seguidores_tiktok(data: SeguidoresInput):
    if fue_scrapeado_recentemente(data.username, "tiktok", tipo="seguidores", nueva_cantidad=data.max_seguidores):
        logger.warning(f"🚫 Ya se scrapearon {data.max_seguidores} o menos seguidores de TikTok para {data.username} recientemente.")
        return JSONResponse(
            status_code=400,
            content={
                "estado": "duplicado",
                "mensaje": f"Este scraping ya fue realizado con esa cantidad o menor en las últimas 24h. La cantidad debe ser mayor."
            }
        )

    tarea = scrape_followers_info_tiktok_task.delay(data.username, data.max_seguidores)
    logger.info(f"📨 Petición recibida para scrapear seguidores de TikTok de {data.username}")
    return {"mensaje": "Scraping completo de seguidores de TikTok en curso", "tarea_id": tarea.id}


@router_tiktok.post("/seguidos")
def lanzar_scraping_info_seguidos_tiktok(data: SeguidosInput):
    if fue_scrapeado_recentemente(data.username, "tiktok", tipo="seguidos", nueva_cantidad=data.max_seguidos):
        logger.warning(f"🚫 Ya se scrapearon {data.max_seguidos} o menos seguidos de TikTok para {data.username} recientemente.")
        return JSONResponse(
            status_code=400,
            content={
                "estado": "duplicado",
                "mensaje": f"Este scraping ya fue realizado con esa cantidad o menor en las últimas 24h. La cantidad debe ser mayor."
            }
        )

    tarea = scrape_followees_info_tiktok_task.delay(data.username, data.max_seguidos)
    logger.info(f"📨 Petición recibida para scrapear seguidos de TikTok de {data.username}")
    return {"mensaje": "Scraping completo de seguidos de TikTok en curso", "tarea_id": tarea.id}

