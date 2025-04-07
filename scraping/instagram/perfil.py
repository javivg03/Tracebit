from services.validator import extraer_emails, extraer_telefonos
from services import busqueda_cruzada, history
from exports.exporter import export_to_excel
import instaloader


def scrapear_perfil_instagram(username: str):
    print(f"🚀 Iniciando scraping del perfil: {username}")
    insta_loader = instaloader.Instaloader()

    try:
        insta_loader.load_session_from_file("pruebasrc1")
        print("✅ Sesión de Instagram cargada")
    except Exception as e:
        print(f"⚠️ No se pudo cargar la sesión: {e}")

    try:
        profile = instaloader.Profile.from_username(insta_loader.context, username)
    except Exception as e:
        print(f"❌ Error al obtener el perfil: {e}")
        history.guardar_historial("Instagram", username, "Fallido")
        return {
            "nombre": None,
            "usuario": username,
            "email": None,
            "fuente_email": None,
            "telefono": None,
            "seguidores": None,
            "seguidos": None,
            "hashtags": [],
            "origen": "error"
        }

    nombre = profile.full_name
    bio = profile.biography or ""
    seguidores = profile.followers
    seguidos = profile.followees
    hashtags = [tag.strip("#") for tag in bio.split() if tag.startswith("#")]

    emails = extraer_emails(bio)
    email = emails[0] if emails else None
    email_fuente = "bio" if email else None

    telefonos = extraer_telefonos(bio)
    telefono = telefonos[0] if telefonos else None

    origen = "bio" if email else "no_email"

    datos = {
        "nombre": nombre,
        "usuario": username,
        "email": email,
        "fuente_email": email_fuente,
        "telefono": telefono,
        "seguidores": seguidores,
        "seguidos": seguidos,
        "hashtags": hashtags,
        "origen": origen
    }

    # 🔍 Si no hay email → búsqueda cruzada
    if not email:
        resultado_cruzado = busqueda_cruzada.buscar_contacto(username, nombre)
        if resultado_cruzado and (resultado_cruzado.get("email") or resultado_cruzado.get("telefono")):
            datos.update({
                "email": resultado_cruzado.get("email"),
                "telefono": resultado_cruzado.get("telefono"),
                "fuente_email": resultado_cruzado.get("url_fuente"),
                "origen": f"{datos.get('origen', 'no_email')} + búsqueda cruzada ({resultado_cruzado.get('origen')})"
            })

    # 📁 Exportar a Excel
    filename = f"exports/instagram_{username}.xlsx"
    export_to_excel([datos], filename)

    # 📝 Guardar historial
    history.guardar_historial("Instagram", username, "Éxito")

    print(f"✅ Scraping completado para: {username}")
    return datos
