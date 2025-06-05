import os
import json
from fastapi import APIRouter, Request
from pydantic import BaseModel
from services.proxy_loader import guardar_proxies_formateados
from fastapi.responses import JSONResponse

router_proxies = APIRouter(prefix="/proxies")

class ProxiesInput(BaseModel):
    proxies: list[str]
    modo: str = "replace"  # puede ser "replace" o "append"

@router_proxies.post("/subir_proxies")
def subir_proxies(input: ProxiesInput):
    if not input.proxies:
        return JSONResponse(status_code=400, content={"error": "No se recibió ninguna línea de proxy"})

    try:
        guardar_proxies_formateados(input.proxies, modo=input.modo)
        return {"mensaje": f"Proxies cargados correctamente en modo '{input.modo}'."}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Error al procesar proxies: {e}"})


@router_proxies.get("/contar")
def contar_proxies():
    ruta = "services/proxies.json"
    if not os.path.exists(ruta):
        return {"total": 0}

    try:
        with open(ruta, "r", encoding="utf-8") as f:
            proxies = json.load(f)
            return {"total": len(proxies)}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Error al contar proxies: {e}"})

