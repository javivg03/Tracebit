import instaloader
import re
from services.busqueda_cruzada import buscar_email
from services.validator import validar_email, validar_telefono

EMAIL_REGEX = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
PHONE_REGEX = r"\+?\d[\d\s().-]{7,}"

def extraer_datos_relevantes(username):
    # Inicializar Instaloader
    insta_loader = instaloader.Instaloader()

    # Intentar cargar la sesión guardada
    try:
        insta_loader.load_session_from_file("pruebasrc1")  # Cambia esto por tu usuario si es otro
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
    bio = profile.biography
    seguidores = profile.followers
    seguidos = profile.followees
    hashtags = re.findall(r"#(\w+)", bio)

    # Buscar email en la bio
    email = None
    email_fuente = None
    matches_email = re.findall(EMAIL_REGEX, bio)
    for e in matches_email:
        if validar_email(e):
            email = e
            email_fuente = "bio"
            break

    # Buscar teléfono en bio
    telefono = None
    matches_tel = re.findall(PHONE_REGEX, bio)
    for tel in matches_tel:
        if validar_telefono(tel):
            telefono = tel
            break

    # Búsqueda cruzada si no hay email
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
