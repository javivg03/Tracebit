from scraping.telegram import scrape_telegram

# Cambia este nombre por el del canal que quieras probar
canal = "chollometro"  # Ejemplo de canal real

datos = scrape_telegram(canal)

print("\n📦 DATOS EXTRAÍDOS:")
for clave, valor in datos.items():
    print(f"{clave}: {valor}")
