import re
from email_validator import validate_email, EmailNotValidError

EMAIL_REGEX = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
PHONE_REGEX = r"\+?[0-9\s().-]{7,}"

def validar_email(email: str):
    """
    Valida un email. Devuelve el email normalizado si es válido, o None si no lo es.
    """
    try:
        resultado = validate_email(email, check_deliverability=False)
        return resultado.normalized
    except EmailNotValidError:
        return None

def validar_telefono(numero: str):
    """
    Valida un número de teléfono básico. Si es válido, lo devuelve limpio; si no, devuelve None.
    """
    numero = numero.strip()
    if len(numero) >= 8 and re.match(PHONE_REGEX, numero):
        return numero
    return None

def extraer_emails(texto: str):
    """
    Extrae todos los emails válidos desde un texto, eliminando duplicados.
    """
    encontrados = re.findall(EMAIL_REGEX, texto, re.IGNORECASE)
    validos = set()
    for e in encontrados:
        ve = validar_email(e)
        if ve:
            validos.add(ve)
    return list(validos)

def extraer_telefonos(texto: str):
    """
    Extrae todos los teléfonos válidos desde un texto, eliminando duplicados.
    """
    encontrados = re.findall(PHONE_REGEX, texto)
    validos = set()
    for t in encontrados:
        vt = validar_telefono(t)
        if vt:
            validos.add(vt)
    return list(validos)
