import instaloader
from services.busqueda_cruzada import buscar_email
from services.validator import extraer_emails, extraer_telefonos

def extraer_datos_relevantes(username):
    # Inicializar Instaloader
    insta_loader = instaloader.Instaloader()

    try:
        insta_loader.load_session_from_file("pruebasrc1")
        print("✅ Sesión cargada correctamente.")
    except Exception as e:
        print(f"⚠️ No se pudo cargar la sesión: {e}")

    # Obtener perfil
    try:
        profile = instaloader.Profile.from_username(insta_loader.context, username)
    except Exception as e:
        print(f"❌ Error al obtener el perfil de Instagram: {e}")
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

    # Extraer datos visibles
    nombre = profile.full_name
    bio = profile.biography or ""
    seguidores = profile.followers
    seguidos = profile.followees
    hashtags = [tag.strip("#") for tag in bio.split() if tag.startswith("#")]

    # 📩 Email y ☎️ Teléfono desde la bio
    emails = extraer_emails(bio)
    email = emails[0] if emails else None
    email_fuente = "bio" if email else None

    telefonos = extraer_telefonos(bio)
    telefono = telefonos[0] if telefonos else None

    # 🔁 Búsqueda cruzada si no hay email en bio
    if not email:
        resultado_busqueda = buscar_email(username, nombre)
        email = resultado_busqueda["email"]
        email_fuente = resultado_busqueda["url_fuente"]
        origen = resultado_busqueda["origen"]
    else:
        origen = "bio"

    return {
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
