import re
import phonenumbers
from email_validator import validate_email, EmailNotValidError
from phonenumbers.phonenumberutil import NumberParseException

EMAIL_REGEX = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"

def extraer_emails(texto: str) -> list:
    return re.findall(EMAIL_REGEX, texto)


def validar_email(email: str) -> bool:
    try:
        validate_email(email)
        return True
    except EmailNotValidError:
        return False


def extraer_emails_validos(texto: str) -> list[str]:
    return [e for e in extraer_emails(texto) if validar_email(e)]


def extraer_telefonos(texto: str, region_default: str = "ES") -> list:
    telefonos_validos = []

    for match in phonenumbers.PhoneNumberMatcher(texto, region_default):
        numero = match.number
        try:
            if phonenumbers.is_possible_number(numero) and phonenumbers.is_valid_number(numero):
                telefono_formateado = phonenumbers.format_number(numero, phonenumbers.PhoneNumberFormat.E164)
                telefonos_validos.append(telefono_formateado)
        except NumberParseException:
            continue

    return telefonos_validos


def detectar_enlaces_sociales(texto: str) -> dict:
    """
    Detecta enlaces a perfiles de otras redes sociales en un texto
    y extrae el nombre de usuario o identificador si es posible.
    """
    plataformas = {}

    # Instagram
    match = re.search(r"instagram\.com/([a-zA-Z0-9_.]+)", texto)
    if match:
        plataformas["instagram"] = match.group(1)

    # TikTok
    match = re.search(r"tiktok\.com/@([a-zA-Z0-9_.]+)", texto)
    if match:
        plataformas["tiktok"] = match.group(1)

    # YouTube
    match = re.search(r"youtube\.com/(?:@([a-zA-Z0-9_.]+)|channel/([a-zA-Z0-9_-]+))", texto)
    if match:
        plataformas["youtube"] = match.group(1) or match.group(2)

    # Facebook
    match = re.search(r"facebook\.com/([a-zA-Z0-9_.]+)", texto)
    if match and match.group(1) not in ["profile.php", "pages"]:
        plataformas["facebook"] = match.group(1)

    # Twitter (X)
    match = re.search(r"(?:x|twitter)\.com/([a-zA-Z0-9_]+)", texto)
    if match:
        plataformas["x"] = match.group(1)

    # Telegram
    match = re.search(r"(?:t\.me|telegram\.me)/([a-zA-Z0-9_]+)", texto)
    if match:
        plataformas["telegram"] = match.group(1)

    # Linktree
    match = re.search(r"linktr\.ee/([a-zA-Z0-9_.-]+)", texto)
    if match:
        plataformas["linktree"] = match.group(1)

    # Beacons
    match = re.search(r"beacons\.ai/([a-zA-Z0-9_.-]+)", texto)
    if match:
        plataformas["beacons"] = match.group(1)

    return plataformas

def extraer_dominios(texto: str) -> list:
    """
    Extrae URLs o rutas que parezcan dominios web o enlaces relevantes de la bio.
    Ignora redes sociales ya scrapeadas.
    """
    url_regex = r"(https?://)?(www\.)?([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})(/[^\s]*)?"

    matches = re.findall(url_regex, texto)
    dominios = set()

    blacklist = [
        "instagram.com", "www.instagram.com",
        "tiktok.com", "www.tiktok.com",
        "x.com", "twitter.com", "facebook.com", "youtube.com"
    ]

    for match in matches:
        dominio_completo = f"{match[2]}{match[3]}" if match[3] else match[2]
        if not any(b in dominio_completo for b in blacklist):
            dominios.add(dominio_completo.lower())

    return list(dominios)
