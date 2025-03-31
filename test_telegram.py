from scraping.telegram import scrape_telegram

canal = "spremium"

datos = scrape_telegram(canal)

print("\n📦 DATOS EXTRAÍDOS:")
for clave, valor in datos.items():
    print(f"{clave}: {valor}")
