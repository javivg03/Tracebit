from fastapi import APIRouter, Body
from pydantic import BaseModel

from tasks.x import scrape_tweets_info_x_task
from services.logging_config import logger
from utils.flujo_scraping import flujo_scraping_multired

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

    resultado = await flujo_scraping_multired(
        username=data.username,
        redes=["x", "instagram"],
        habilitar_busqueda_web=data.habilitar_busqueda_web
    )

    return resultado

@router_x.post("/tweets")
def lanzar_scraping_tweets_x(data: UserInput = Body(...), req: TweetsRequest = Body(...)):
    tarea = scrape_tweets_info_x_task.delay(data.username, req.max_tweets)
    logger.info(f"📥 Tarea Celery lanzada: scrape_tweets_x para {data.username} (máx {req.max_tweets})")
    return {"mensaje": "Scraping de tweets relevantes en curso", "tarea_id": tarea.id}
