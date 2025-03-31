from scraping.facebook import scrape_facebook

username = "themustoftheworld"  # Puedes cambiarlo por otro perfil público

datos = scrape_facebook(username)

print("\n📦 DATOS EXTRAÍDOS:")
for clave, valor in datos.items():
    print(f"{clave}: {valor}")
