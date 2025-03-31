from scraping.instagram import extraer_datos_relevantes
from scraping.telegram import scrape_telegram
from scraping.youtube import scrape_youtube
from scraping.tiktok import scrape_tiktok
from scraping.facebook import scrape_facebook
from scraping.x import scrape_x
from scraping.web import buscar_por_keyword

# Lista de pruebas por plataforma
pruebas = [
    ("Instagram", "ibaillanos", extraer_datos_relevantes),
    ("Telegram", "spremium", scrape_telegram),
    ("YouTube", "TheWildProject", scrape_youtube),
    ("TikTok", "joanpradells", scrape_tiktok),
    ("Facebook", "themustoftheworld", scrape_facebook),
    ("X", "elonmusk", scrape_x),
    ("Web", "entrenador personal sevilla", buscar_por_keyword)
]

print("\n📦 INICIANDO TEST DE TODOS LOS SCRAPERS\n")

for nombre, input_value, funcion in pruebas:
    print(f"\n🔍 Plataforma: {nombre}")
    print(f"👤 Entrada: {input_value}")

    try:
        resultado = funcion(input_value)
        if resultado:
            print("✅ Resultado:")
            if isinstance(resultado, list):  # Web devuelve lista
                for i, item in enumerate(resultado[:3], start=1):
                    print(f"  🔹 Resultado {i}:")
                    for k, v in item.items():
                        print(f"     {k}: {v}")
            else:
                for k, v in resultado.items():
                    print(f"  {k}: {v}")
        else:
            print("⚠️ No se obtuvo resultado.")

    except Exception as e:
        print(f"❌ Error en scraping de {nombre}: {str(e)}")

print("\n✅ Test finalizado.\n")
