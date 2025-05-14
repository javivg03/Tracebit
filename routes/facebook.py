from fastapi import APIRouter, Body
from pydantic import BaseModel

from scraping.facebook.perfil import obtener_datos_perfil_facebook
from services.logging_config import logger
from utils.scraping_handler import procesar_scraping

router_facebook = APIRouter(prefix="/facebook")

# ========== Pydantic Models ==========
class FacebookPerfilInput(BaseModel):
    username: str
    habilitar_busqueda_web: bool = False

# ========== Endpoints ==========
@router_facebook.post("/perfil")
async def facebook_scraper(data: FacebookPerfilInput = Body(...)):
    logger.info(f"📥 Endpoint recibido: Scraping de perfil Facebook para {data.username}")
    return await procesar_scraping(
        data.username,
        "facebook",
        obtener_datos_perfil_facebook,
        habilitar_busqueda_web=data.habilitar_busqueda_web
    )
