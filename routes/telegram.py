from fastapi import APIRouter, Body
from pydantic import BaseModel
from services.logging_config import logger
from utils.flujo_scraping import flujo_scraping_multired

router_telegram = APIRouter(prefix="/telegram")


# ========== Pydantic Models ==========
class UserInput(BaseModel):
    username: str
    habilitar_busqueda_web: bool = False


# ========== Endpoints ==========
@router_telegram.post("/canal")
async def telegram_scraper(data: UserInput = Body(...)):
    logger.info(f"📥 Endpoint recibido: Scraping de canal Telegram para {data.username}")

    resultado = await flujo_scraping_multired(
        username=data.username,
        redes=["telegram", "instagram"],
        habilitar_busqueda_web=data.habilitar_busqueda_web
    )

    return resultado
