import csv
import re
import os
import pandas as pd
from datetime import datetime, timedelta

# --- Configuración ---
HISTORY_FILE = "exports/historial.csv"
MODO_PRUEBAS = False  # ← Cambiar a True en desarrollo para ignorar control de duplicados

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
def guardar_historial(plataforma: str, username: str, status: str, archivo: str = "", tipo: str = ""):
    """
    Guarda una línea en el historial CSV con fecha, plataforma, tipo, usuario, resultado y archivo generado.
    """
    existe = os.path.exists(HISTORY_FILE)

    with open(HISTORY_FILE, mode='a', newline='', encoding='utf-8') as archivo_csv:
        writer = csv.writer(archivo_csv)
        if not existe:
            writer.writerow(["fecha", "plataforma", "tipo", "usuario", "resultado", "archivo"])
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            plataforma,
            tipo or "",
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


# --- Control de scrapings repetidos ---
def fue_scrapeado_recentemente(username: str, plataforma: str, tipo: str = "perfil", ventana_horas: int = 24, nueva_cantidad: int = None) -> bool:
    """
    Comprueba si se ha hecho scraping del mismo usuario/plataforma/tipo en las últimas N horas.
    Si se indica nueva_cantidad, solo se bloquea si ya se scrapeó esa cantidad o más.
    """
    if MODO_PRUEBAS or not os.path.exists(HISTORY_FILE):
        return False

    ahora = datetime.now()

    with open(HISTORY_FILE, mode='r', encoding='utf-8') as archivo:
        reader = csv.DictReader(archivo)

        for fila in reader:
            fecha_str = fila.get("fecha", "")
            plataforma_fila = fila.get("plataforma", "").lower()
            tipo_fila = fila.get("tipo", "").lower()
            usuario_fila = fila.get("usuario", "").lower()
            resultado_fila = fila.get("resultado", "").lower()

            if (
                username.lower() == usuario_fila and
                plataforma.lower() == plataforma_fila and
                tipo.lower() == tipo_fila
            ):
                try:
                    fecha = datetime.strptime(fecha_str, "%Y-%m-%d %H:%M:%S")
                    if ahora - fecha < timedelta(hours=ventana_horas):
                        if "sin datos útiles" in resultado_fila:
                            continue  # permite repetir si el scraping fue inútil

                        match = re.search(r"\((\d+)/(\d+)\s+útiles\)", resultado_fila)
                        if match:
                            total_anterior = int(match.group(2))
                            if nueva_cantidad is None or nueva_cantidad <= total_anterior:
                                return True
                        else:
                            return True  # bloqueamos por defecto si no sabemos
                except Exception:
                    continue

    return False
