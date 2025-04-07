from scraping.instagram.seguidores import scrape_followers_info

# 🧪 Configuración
perfil_objetivo = "sofig.oficial"
max_seguidores = 5

print(f"🔍 Iniciando test de extracción completa de seguidores para: {perfil_objetivo}\n")

# Llamamos a la nueva función completa
datos = scrape_followers_info(perfil_objetivo, max_seguidores=max_seguidores)

if datos:
    print(f"\n✅ Se han scrapeado {len(datos)} perfiles de seguidores correctamente.")
else:
    print("⚠️ No se pudo completar la extracción de seguidores.")
