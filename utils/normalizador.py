from typing import Optional, Dict, Any

def normalizar_datos_scraper(
    nombre: Optional[str],
    usuario: str,
    email: Optional[str],
    fuente_email: Optional[str],
    telefono: Optional[str],
    seguidores: Optional[int],
    seguidos: Optional[int],
    hashtags: Optional[list],
    origen: str,
    **extras: Any  # acepta cualquier otro campo adicional (como enlaces_web)
) -> Dict[str, Any]:
    """
    Devuelve un diccionario con la estructura unificada de datos del perfil.
    Admite campos adicionales como enlaces_web mediante kwargs.
    """
    datos = {
        "nombre": nombre or None,
        "usuario": usuario,
        "email": email or None,
        "fuente_email": fuente_email or None,
        "telefono": telefono or None,
        "seguidores": seguidores,
        "seguidos": seguidos,
        "hashtags": hashtags or [],
        "origen": origen
    }

    # Añadir campos adicionales (enlaces_web, etc.)
    datos.update(extras)

    return datos
