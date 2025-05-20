from fastapi import APIRouter, Body
from pydantic import BaseModel

from scraping.telegram.canal import obtener_datos_canal_telegram
from services.logging_config import logger
from utils.scraping_handler import procesar_scraping

router_telegram = APIRouter(prefix="/telegram")

# ========== Pydantic Models ==========
class UserInput(BaseModel):
    username: str
    habilitar_busqueda_web: bool = False

# ========== Endpoints ==========
@router_telegram.post("/canal")
async def telegram_scraper(data: UserInput = Body(...)):
    return await procesar_scraping(
        data.username,
        "telegram",
        obtener_datos_canal_telegram,
        habilitar_busqueda_web=data.habilitar_busqueda_web
    )
