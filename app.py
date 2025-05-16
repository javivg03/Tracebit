from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from routes.instagram import router_instagram
from routes.tiktok import router_tiktok
from routes.telegram import router_telegram
from routes.youtube import router_youtube
from routes.x import router_x
from routes.facebook import router_facebook
from routes.web import router_web

from routes.resultados import router_resultados

# ========== FASTAPI APP SETUP ==========
app = FastAPI(
    title="FCT Scraper API",
    description="API para scraping de redes sociales y web pública.",
    version="1.0.0"
)

app.mount("/static", StaticFiles(directory="static"), name="static")

# ========== HTML RAÍZ ==========
@app.get("/", response_class=FileResponse)
def root():
    return "static/index.html"

# ========== INCLUIMOS ROUTERS ==========
app.include_router(router_instagram)
app.include_router(router_tiktok)
app.include_router(router_telegram)
app.include_router(router_youtube)
app.include_router(router_x)
app.include_router(router_facebook)
app.include_router(router_web)
app.include_router(router_resultados)

