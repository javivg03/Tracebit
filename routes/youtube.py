from fastapi import APIRouter, Body
from pydantic import BaseModel

from scraping.youtube.canal import obtener_datos_perfil_youtube
from services.logging_config import logger
from utils.scraping_handler import procesar_scraping

router_youtube = APIRouter(prefix="/youtube")

# ========== Pydantic Models ==========
class UserInput(BaseModel):
    username: str

# ========== Endpoints ==========
@router_youtube.post("/canal")
async def youtube_scraper(data: UserInput = Body(...)):
    logger.info(f"🚀 Endpoint recibido: Scraping de canal YouTube para {data.username}")
    return await procesar_scraping(data.username, "youtube", obtener_datos_perfil_youtube)
