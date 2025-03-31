from scraping.tiktok import scrape_tiktok

entrada = "joanpradells"  # o cualquier nombre real
datos = scrape_tiktok(entrada)

print("\n📦 DATOS EXTRAÍDOS DE TIKTOK:")
for key, value in datos.items():
    print(f"{key}: {value}")
