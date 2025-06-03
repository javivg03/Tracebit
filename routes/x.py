from fastapi import APIRouter, Body
from pydantic import BaseModel
from services.logging_config import logger
from utils.flujo_scraping import flujo_scraping_multired
from utils.exportador_perfil import ejecutar_scraping_y_exportar
from tasks.x import scrape_tweets_info_x_task

router_x = APIRouter(prefix="/x")

# ========== Pydantic Models ==========

class UserInput(BaseModel):
    username: str
    habilitar_busqueda_web: bool = False

class TweetsRequest(BaseModel):
    max_tweets: int = 10

# ========== Endpoints ==========

@router_x.post("/perfil")
async def x_scraper(data: UserInput = Body(...)):
    logger.info(f"📥 Endpoint recibido: Scraping de perfil X para {data.username}")

    return await ejecutar_scraping_y_exportar(
        username=data.username,
        redes=["x", "instagram"],
        flujo_scraping=flujo_scraping_multired,
        habilitar_busqueda_web=data.habilitar_busqueda_web
    )

@router_x.post("/tweets")
def lanzar_scraping_tweets_x(data: UserInput = Body(...), req: TweetsRequest = Body(...)):
    tarea = scrape_tweets_info_x_task.delay(data.username, req.max_tweets)
    logger.info(f"📥 Tarea Celery lanzada: scrape_tweets_x para {data.username} (máx {req.max_tweets})")
    return {"mensaje": "Scraping de tweets relevantes en curso", "tarea_id": tarea.id}
