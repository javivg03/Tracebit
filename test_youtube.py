from scraping.youtube import scrape_youtube

canal = "TheWildProject"  # Puedes probar con cualquier nombre de canal
datos = scrape_youtube(canal)

print("\n📦 DATOS EXTRAÍDOS:")
for key, value in datos.items():
    print(f"{key}: {value}")
