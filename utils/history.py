import csv
from datetime import datetime, timedelta
import os

HISTORY_FILE = "exports/historial.csv"

def guardar_historial(plataforma, username, status):
    existe = os.path.exists(HISTORY_FILE)
    with open(HISTORY_FILE, mode='a', newline='', encoding='utf-8') as archivo:
        writer = csv.writer(archivo)
        if not existe:
            writer.writerow(["fecha", "plataforma", "usuario", "resultado"])
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            plataforma,
            username,
            status
        ])


MODO_PRUEBAS = True  # ← Poner en False en producción
def fue_scrapeado_recentemente(username: str, plataforma: str, tipo: str = "Perfil", ventana_horas: int = 24,
                               requiere_cruzada: bool = False) -> bool:
    """
    Devuelve True si ya se ha hecho scraping del mismo usuario/plataforma/tipo en las últimas N horas.

    - Si MODO_PRUEBAS está activado, siempre devuelve False.
    - Si requiere_cruzada=True, solo bloquea si ya se hizo scraping con búsqueda cruzada.
    - Si requiere_cruzada=False, solo bloquea si ya se hizo scraping con cruzada también (scraping sin cruzada nunca bloquea a uno con cruzada).
    - Ignora entradas con "Sin datos útiles" salvo si incluyen "búsqueda cruzada".
    """
    if MODO_PRUEBAS or not os.path.exists(HISTORY_FILE):
        return False

    ahora = datetime.now()

    with open(HISTORY_FILE, mode='r', encoding='utf-8') as archivo:
        reader = csv.DictReader(archivo)

        for fila in reader:
            fecha_str = fila["fecha"]
            plataforma_fila = fila["plataforma"].lower()
            usuario_fila = fila["usuario"].lower()
            resultado_fila = fila["resultado"].lower()

            if username.lower() == usuario_fila and tipo.lower() in plataforma_fila and plataforma.lower() in plataforma_fila:
                try:
                    fecha = datetime.strptime(fecha_str, "%Y-%m-%d %H:%M:%S")
                    if ahora - fecha < timedelta(hours=ventana_horas):
                        incluye_cruzada = "búsqueda cruzada" in resultado_fila or "cruzada" in resultado_fila
                        sin_datos = "sin datos útiles" in resultado_fila

                        if requiere_cruzada:
                            if incluye_cruzada:
                                return True  # ya se hizo cruzada
                            else:
                                continue  # no se hizo cruzada antes, así que permitimos
                        else:
                            if incluye_cruzada:
                                return True  # se hizo cruzada antes, bloquear también sin cruzada
                            elif sin_datos:
                                continue  # fue intento fallido sin datos → ignorar
                            else:
                                return True  # se hizo scraping simple con datos útiles
                except:
                    continue

    return False
