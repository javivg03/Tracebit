from scraping.web import buscar_por_keyword

# Puedes cambiar el término por cualquier otro tema/sector/ubicación
termino = "abogado sevilla"
resultados = buscar_por_keyword(termino)

print("\n📦 RESULTADOS DE BÚSQUEDA POR PALABRA CLAVE:\n")

if not resultados:
    print("❌ No se encontraron resultados útiles.")
else:
    for i, resultado in enumerate(resultados, start=1):
        print(f"🔹 Resultado #{i}")
        print(f"   🔗 Título: {resultado['titulo']}")
        print(f"   🌐 Link: {resultado['link']}")
        print(f"   📝 Resumen: {resultado['resumen']}")
        print(f"   📩 Emails: {', '.join(resultado['emails']) if resultado['emails'] else 'Ninguno'}")
        print(f"   📞 Teléfonos: {', '.join(resultado['telefonos']) if resultado['telefonos'] else 'Ninguno'}")
        print("-" * 50)
