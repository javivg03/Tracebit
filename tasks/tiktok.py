from celery_app import celery_app
from scraping.tiktok.seguidores import scrape_followers_info_tiktok
import asyncio

@celery_app.task(name="scrape_followers_info_tiktok_task")
def scrape_followers_info_tiktok_task(username: str, max_seguidores: int = 10):
    print(f"🚀 [CELERY] Scrapeando seguidores de TikTok: {username}")
    return asyncio.run(scrape_followers_info_tiktok(username, max_seguidores))
