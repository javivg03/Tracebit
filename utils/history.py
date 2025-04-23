import csv
from datetime import datetime
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
