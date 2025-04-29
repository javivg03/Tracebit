# routes/x.py
from fastapi import APIRouter, Body
from pydantic import BaseModel

from scraping.x.perfil import obtener_datos_perfil_x
from utils.scraping_handler import procesar_scraping
from services.logging_config import logger

router_x = APIRouter(prefix="/x")

# ========== Pydantic Models ==========
class UserInput(BaseModel):
    username: str

# ========== Endpoints ==========
@router_x.post("/perfil")
async def x_scraper(data: UserInput = Body(...)):
    logger.info(f"📥 Endpoint recibido: Scraping de perfil X para {data.username}")
    return await procesar_scraping(data.username, "x", obtener_datos_perfil_x)
