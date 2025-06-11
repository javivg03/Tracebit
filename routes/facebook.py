from fastapi import APIRouter, Body
from pydantic import BaseModel
from services.logging_config import logger
from utils.flujo_scraping import flujo_scraping_multired
from utils.exportador_perfil import ejecutar_scraping_y_exportar

router_facebook = APIRouter(prefix="/facebook")

# ========== Pydantic Models ==========
class FacebookPerfilInput(BaseModel):
    username: str

# ========== Endpoints ==========
@router_facebook.post("/perfil")
async def facebook_scraper(data: FacebookPerfilInput = Body(...)):
    logger.info(f"📥 Endpoint recibido: Scraping de perfil Facebook para {data.username}")

    return await ejecutar_scraping_y_exportar(
        username=data.username,
        redes=["facebook", "instagram", "tiktok", "x"],
        flujo_scraping=flujo_scraping_multired,
    )
