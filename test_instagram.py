from scraping.instagram.perfil import obtener_datos_perfil_instagram_con_fallback

if __name__ == "__main__":
    username = "jordiwild8"  # Cambia esto por el perfil que quieras probar
    resultado = obtener_datos_perfil_instagram_con_fallback(username)
    print("🔎 Resultado:", resultado)
