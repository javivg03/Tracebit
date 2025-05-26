from fastapi import APIRouter, Body
from pydantic import BaseModel
from services.logging_config import logger
from utils.flujo_scraping import flujo_scraping_multired

router_youtube = APIRouter(prefix="/youtube")

# ========== Pydantic Models ==========
class UserInput(BaseModel):
    username: str
    habilitar_busqueda_web: bool = False

# ========== Endpoints ==========
@router_youtube.post("/canal")
async def youtube_scraper(data: UserInput = Body(...)):
    logger.info(f"📥 Endpoint recibido: Scraping de perfil YouTube para {data.username}")
    return await flujo_scraping_multired(
        username=data.username,
        redes=["youtube", "instagram"],
        habilitar_busqueda_web=data.habilitar_busqueda_web
    )
