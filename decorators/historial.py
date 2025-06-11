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
                    n = len(resultado.get("data", []))
                    mensaje = f"✅ {tipo.capitalize()} extraídos ({n} resultados)"
                elif isinstance(resultado, dict):
                    mensaje = resultado.get("mensaje", f"⚠️ {tipo.capitalize()}: sin datos")
                else:
                    mensaje = f"⚠️ {tipo.capitalize()}: sin datos"

                guardar_historial(plataforma, username, mensaje, archivo)
                return resultado

            except Exception as e:
                logger.error(f"❌ Excepción en tarea {func.__name__} para {username}: {e}")
                guardar_historial(plataforma, username, f"❌ Error en {tipo}: {str(e)}")
                raise e

        return wrapper
    return decorador


def registrar_historial_async(plataforma: str = "multired", tipo: str = "perfil"):
    """
    Decorador para registrar automáticamente el historial en funciones async como flujo_scraping_multired.
    Registra:
    - Si se han encontrado datos (email o teléfono)
    - El origen del resultado
    - Si se ha usado búsqueda cruzada
    - Resultado fallido o vacío
    """
    def decorador(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            username = kwargs.get("username") or (args[0] if args else "desconocido")
            try:
                resultado = await func(*args, **kwargs)

                if not isinstance(resultado, dict):
                    guardar_historial(plataforma, username, f"❌ {tipo.capitalize()}: resultado inválido")
                    return resultado

                archivo = resultado.get("archivo", "")
                origen = resultado.get("origen", "desconocido")
                email = resultado.get("email")
                telefono = resultado.get("telefono")

                if email or telefono:
                    if "búsqueda cruzada" in origen:
                        guardar_historial(plataforma, username, f"📡 Contacto encontrado vía {origen}", archivo)
                    else:
                        guardar_historial(plataforma, username, f"✅ Contacto encontrado ({origen})", archivo)
                else:
                    if "búsqueda cruzada" in origen:
                        guardar_historial(plataforma, username, f"❌ Sin datos útiles (ni en búsqueda cruzada)", archivo)
                    else:
                        guardar_historial(plataforma, username, f"⚠️ Sin datos útiles en scraping multired", archivo)

                return resultado

            except Exception as e:
                logger.error(f"❌ Excepción en función async {func.__name__} para {username}: {e}")
                guardar_historial(plataforma, username, f"❌ Error en {tipo}: {str(e)}")
                raise e

        return wrapper
    return decorador
