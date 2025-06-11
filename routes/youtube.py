from fastapi import APIRouter, Body
from pydantic import BaseModel
from services.logging_config import logger
from utils.flujo_scraping import flujo_scraping_multired
from utils.exportador_perfil import ejecutar_scraping_y_exportar

router_youtube = APIRouter(prefix="/youtube")

# ========== Pydantic Models ==========

class UserInput(BaseModel):
    username: str

# ========== Endpoints ==========

@router_youtube.post("/canal")
async def youtube_scraper(data: UserInput = Body(...)):
    logger.info(f"📥 Endpoint recibido: Scraping de perfil YouTube para {data.username}")

    return await ejecutar_scraping_y_exportar(
        username=data.username,
        redes=["youtube", "instagram", "facebook", "tiktok", "x"],
        flujo_scraping=flujo_scraping_multired,
    )
