import csv
import os
import pandas as pd
from datetime import datetime, timedelta

# --- Configuración ---
HISTORY_FILE = "exports/historial.csv"
MODO_PRUEBAS = False  # ← Cambiar a False en producción

# --- Almacenamiento temporal en memoria para exportación bajo demanda ---
_resultados_memoria = {}


def guardar_resultado_temporal(tipo: str, username: str, resultado: dict | list[dict]):
    """
    Guarda un resultado en memoria temporal para exportación.
    tipo puede ser: 'perfil', 'seguidores', 'seguidos', 'tweets', etc.
    """
    if tipo and username and resultado:
        clave = f"{tipo}_{username}".lower()
        _resultados_memoria[clave] = resultado


def obtener_resultado_temporal(tipo: str, username: str) -> dict | list[dict] | None:
    """
    Recupera el resultado temporal guardado por tipo y username.
    """
    clave = f"{tipo}_{username}".lower()
    return _resultados_memoria.get(clave)


# --- Historial persistente en CSV/XLSX ---
def guardar_historial(plataforma: str, username: str, status: str, archivo: str = ""):
    """
    Guarda una línea en el historial CSV con fecha, plataforma, usuario, resultado y archivo generado.
    """
    existe = os.path.exists(HISTORY_FILE)

    with open(HISTORY_FILE, mode='a', newline='', encoding='utf-8') as archivo_csv:
        writer = csv.writer(archivo_csv)
        if not existe:
            writer.writerow(["fecha", "plataforma", "usuario", "resultado", "archivo"])
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            plataforma,
            username,
            status,
            archivo or ""
        ])

    try:
        df = pd.read_csv(HISTORY_FILE)
        df.to_excel("exports/historial.xlsx", index=False)
    except Exception as e:
        print(f"⚠️ Error generando historial.xlsx: {e}")


def generar_historial_excel():
    """
    Convierte el historial CSV a un archivo Excel para descarga.
    """
    try:
        if os.path.exists(HISTORY_FILE):
            df = pd.read_csv(HISTORY_FILE)
            df.to_excel("exports/historial.xlsx", index=False)
    except Exception as e:
        print(f"⚠️ Error generando historial.xlsx: {e}")


# --- Control de scrapings repetidos básicos ---
def fue_scrapeado_recentemente(username: str, plataforma: str, tipo: str = "Perfil", ventana_horas: int = 24) -> bool:
    """
    Comprueba si se ha hecho scraping del mismo usuario/plataforma/tipo en las últimas N horas.
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
                        if "sin datos útiles" not in resultado_fila:
                            return True
                except:
                    continue

    return False
