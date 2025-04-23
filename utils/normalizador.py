from typing import Optional, Dict

def normalizar_datos_scraper(
    nombre: Optional[str],
    usuario: str,
    email: Optional[str],
    fuente_email: Optional[str],
    telefono: Optional[str],
    seguidores: Optional[int],
    seguidos: Optional[int],
    hashtags: Optional[list],
    origen: str
) -> Dict[str, Optional[str]]:
    """
    Devuelve un diccionario con la estructura unificada de datos del perfil.
    """
    return {
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
