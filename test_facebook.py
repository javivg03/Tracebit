from scraping.facebook import scrape_facebook

username = "Juan López"  # Puedes cambiarlo por otro perfil público

datos = scrape_facebook(username)

print("\n📦 DATOS EXTRAÍDOS:")
for clave, valor in datos.items():
    print(f"{clave}: {valor}")
