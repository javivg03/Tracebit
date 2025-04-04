import asyncio
from scraping.tiktok import scrape_tiktok

async def main():
    entrada = "joanpradells"  # Cambia por otro usuario si quieres
    datos = await scrape_tiktok(entrada)

    print("\n📦 DATOS EXTRAÍDOS DE TIKTOK:")
    for key, value in datos.items():
        print(f"{key}: {value}")

if __name__ == "__main__":
    asyncio.run(main())
