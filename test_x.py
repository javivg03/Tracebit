from scraping.x import scrape_x  # Asegúrate de que el archivo se llame x.py

# Reemplaza con un usuario real para probar
username = "javivg_3"  # Puedes cambiarlo por cualquier perfil público

datos = scrape_x(username)

print("\n📦 DATOS EXTRAÍDOS:")
for clave, valor in datos.items():
    print(f"{clave}: {valor}")
