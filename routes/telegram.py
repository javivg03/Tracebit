from fastapi import APIRouter, Body
from pydantic import BaseModel
from services.logging_config import logger
from utils.flujo_scraping import flujo_scraping_multired
from utils.exportador_perfil import ejecutar_scraping_y_exportar

router_telegram = APIRouter(prefix="/telegram")

# ========== Pydantic Models ==========
class UserInput(BaseModel):
    username: str

# ========== Endpoints ==========
@router_telegram.post("/canal")
async def telegram_scraper(data: UserInput = Body(...)):
    logger.info(f"📥 Endpoint recibido: Scraping de canal Telegram para {data.username}")

    return await ejecutar_scraping_y_exportar(
        username=data.username,
        redes=["telegram", "instagram", "facebook", "tiktok", "x"],
        flujo_scraping=flujo_scraping_multired,
    )
