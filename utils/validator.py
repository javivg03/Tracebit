import re
import phonenumbers
from email_validator import validate_email, EmailNotValidError
from phonenumbers.phonenumberutil import NumberParseException

# Regex para extraer emails
EMAIL_REGEX = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"

def extraer_emails(texto: str) -> list:
    """
    Extrae todos los emails que coincidan con el patrón general.
    """
    return re.findall(EMAIL_REGEX, texto)


def extraer_telefonos(texto: str, region_default: str = "ES") -> list:
    """
    Extrae teléfonos válidos desde texto usando la librería 'phonenumbers'.
    Retorna en formato internacional E.164 (+34...).
    """
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


def validar_email(email: str) -> bool:
    """
    Valida que un email sea sintácticamente correcto y estructurado.
    """
    try:
        validate_email(email)
        return True
    except EmailNotValidError:
        return False
