from fastapi import APIRouter, Body
from pydantic import BaseModel
from services.logging_config import logger
from utils.flujo_scraping import flujo_scraping_multired

router_facebook = APIRouter(prefix="/facebook")

# ========== Pydantic Models ==========
class FacebookPerfilInput(BaseModel):
    username: str
    habilitar_busqueda_web: bool = False

# ========== Endpoints ==========
@router_facebook.post("/perfil")
async def facebook_scraper(data: FacebookPerfilInput = Body(...)):
    logger.info(f"📥 Endpoint recibido: Scraping de perfil Facebook para {data.username}")

    resultado = await flujo_scraping_multired(
        username=data.username,
        redes=["facebook", "instagram"],
        habilitar_busqueda_web=data.habilitar_busqueda_web
    )

    return resultado
