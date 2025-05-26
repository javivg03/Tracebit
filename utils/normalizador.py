from typing import Optional, Dict, Any

def normalizar_datos_scraper(
    nombre: Optional[str],
    usuario: str,
    email: Optional[str],
    telefono: Optional[str],
    origen: str,
    **extras: Any
) -> Dict[str, Any]:
    """
    Devuelve un diccionario con la estructura unificada de datos del perfil.
    Por ahora solo usa los campos clave. Se pueden añadir más con extras.
    """
    datos = {
        "nombre": nombre or None,
        "usuario": usuario,
        "email": email or None,
        "telefono": telefono or None,
        "origen": origen
    }

    datos.update(extras)
    return datos


def construir_origen(plataforma: str, email: Optional[str], telefono: Optional[str]) -> str:
    return plataforma if email or telefono else "no_email"
