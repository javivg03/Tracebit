from scraping.instagram import extraer_datos_relevantes

# Reemplaza con un perfil público real para probar
username = "jbsettineri"  # Ejemplo, puedes cambiarlo por otro

datos = extraer_datos_relevantes(username)

print("\n📦 DATOS EXTRAÍDOS:")
for clave, valor in datos.items():
    print(f"{clave}: {valor}")
