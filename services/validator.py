from email_validator import validate_email, EmailNotValidError
import re

PHONE_REGEX = r"\+?\d[\d\s().-]{7,}"  # Puedes afinarlo más si es necesario

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
