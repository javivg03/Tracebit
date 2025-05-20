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


def fue_scrapeado_recentemente(username: str, plataforma: str, tipo: str = "Perfil", ventana_horas: int=0.001) -> bool:
    """
    Devuelve True si ya se ha hecho scraping del mismo usuario/plataforma/tipo en las últimas N horas.
    """
    if not os.path.exists(HISTORY_FILE):
        return False

    with open(HISTORY_FILE, mode='r', encoding='utf-8') as archivo:
        reader = csv.DictReader(archivo)
        ahora = datetime.now()

        for fila in reader:
            fecha_str = fila["fecha"]
            plataforma_fila = fila["plataforma"].lower()
            usuario_fila = fila["usuario"].lower()

            if username.lower() == usuario_fila and tipo.lower() in plataforma_fila and plataforma.lower() in plataforma_fila:
                try:
                    fecha = datetime.strptime(fecha_str, "%Y-%m-%d %H:%M:%S")
                    if ahora - fecha < timedelta(hours=ventana_horas):
                        return True
                except:
                    continue

    return False
