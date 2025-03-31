from email_validator import validate_email, EmailNotValidError
import re

EMAIL_REGEX = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
PHONE_REGEX = r"\+?\d[\d\s().-]{7,}"

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
    Valida un número de teléfono básico. Si es válido, lo devuelve limpio. Si no, devuelve None.
    """
    numero = numero.strip()
    if len(numero) >= 8 and re.match(PHONE_REGEX, numero):
        return numero
    return None

def extraer_emails(texto: str):
    """
    Extrae todos los emails válidos desde un texto.
    """
    encontrados = re.findall(EMAIL_REGEX, texto)
    return [e for e in encontrados if validar_email(e)]

def extraer_telefonos(texto: str):
    """
    Extrae todos los teléfonos válidos desde un texto.
    """
    encontrados = re.findall(PHONE_REGEX, texto)
    return [t for t in encontrados if validar_telefono(t)]
