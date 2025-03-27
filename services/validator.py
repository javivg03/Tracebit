from email_validator import validate_email, EmailNotValidError

def validar_email(email: str):
    """
    Valida un email. Devuelve el email normalizado si es válido, o None si no lo es.
    """
    try:
        resultado = validate_email(email, check_deliverability=False)  # No hacemos consulta DNS por ahora
        return resultado.email
    except EmailNotValidError:
        return None
