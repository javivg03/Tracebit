from functools import wraps
from utils.history import guardar_historial
from services.logging_config import logger

def registrar_historial(plataforma: str, tipo: str):
    """
    Decorador para tareas Celery síncronas (seguidores, tweets...).
    Registra si la tarea tuvo éxito, fallo o excepción.
    """
    def decorador(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            username = kwargs.get("username") or (args[0] if args else "desconocido")
            try:
                resultado = func(*args, **kwargs)

                archivo = resultado.get("archivo", "") if isinstance(resultado, dict) else ""

                if isinstance(resultado, dict) and resultado.get("estado") == "ok":
                    total = resultado.get("total_scrapeados", len(resultado.get("data", [])))
                    utiles = len(resultado.get("data", []))
                    mensaje = f"✅ {tipo.capitalize()} extraídos ({utiles}/{total} útiles)"
                elif isinstance(resultado, dict):
                    mensaje = resultado.get("mensaje", f"⚠️ {tipo.capitalize()}: sin datos")
                else:
                    mensaje = f"⚠️ {tipo.capitalize()}: sin datos"

                guardar_historial(plataforma, username, mensaje, archivo, tipo=tipo)
                return resultado

            except Exception as e:
                logger.error(f"❌ Excepción en tarea {func.__name__} para {username}: {e}")
                guardar_historial(plataforma, username, f"❌ Error en {tipo}: {str(e)}", tipo=tipo)
                raise e

        return wrapper
    return decorador


def registrar_historial_async(plataforma: str = "multired", tipo: str = "perfil"):
    def decorador(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            username = kwargs.get("username") or (args[0] if args else "desconocido")
            try:
                resultado = await func(*args, **kwargs)

                if not isinstance(resultado, dict):
                    guardar_historial(plataforma, username, f"❌ {tipo.capitalize()}: resultado inválido", tipo=tipo)
                    return resultado

                archivo = resultado.get("archivo", "")
                email = resultado.get("email")
                telefono = resultado.get("telefono")

                if email or telefono:
                    guardar_historial(plataforma, username, f"✅ Contacto encontrado", archivo, tipo)
                else:
                    guardar_historial(plataforma, username, f"⚠️ Sin datos útiles en scraping multired", archivo, tipo)

                return resultado

            except Exception as e:
                logger.error(f"❌ Excepción en función async {func.__name__} para {username}: {e}")
                guardar_historial(plataforma, username, f"❌ Error en {tipo}: {str(e)}", tipo=tipo)
                raise e

        return wrapper
    return decorador


