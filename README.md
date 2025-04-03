
# 📊 FCT Scraper – Extracción de Datos Públicos de Redes Sociales

Proyecto de scraping multiplataforma desarrollado con fines educativos y de captación de leads desde redes sociales como Instagram, YouTube, TikTok, Facebook, X (Twitter), Telegram, etc.

---

## 🚀 Tecnologías utilizadas

- 🐍 Python 3.11  
- 🐳 Docker + Docker Compose  
- ⚡ FastAPI  
- 🧠 Playwright (scraping avanzado)  
- 📦 Instaloader (Instagram)  
- 🎯 HTML + JS (frontend)  
- 📄 Excel/CSV para exportación de resultados  

---

## 🛠️ Requisitos previos

1. Tener [Docker Desktop](https://www.docker.com/products/docker-desktop/) instalado y funcionando  
2. Tener `git` instalado  
3. En sistemas Windows, usar **terminal de PowerShell o WSL** (no CMD)  
4. Recomendado: Cuenta secundaria de Instagram (para scraping masivo con sesión)  

---

## 📦 Instrucciones de instalación

### 1. Clona el repositorio

```bash
git clone https://github.com/TU-USUARIO/fct_scraper_backend.git
cd fct_scraper_backend
```

### 2. Levanta la aplicación con Docker

```bash
docker-compose up --build
```

⏳ Espera unos segundos y visita:  
➡️ [http://localhost:8000](http://localhost:8000)

---

## 🔐 Iniciar sesión en Instagram (solo una vez)

Desde tu máquina host (fuera del contenedor), abre terminal y ejecuta:

```bash
instaloader --login=tu_usuario_instagram
```

🔑 Introduce la contraseña cuando lo pida.  
✅ Se guardará una sesión en tu equipo en:

- **Windows:** `C:\Users\TU_USUARIO\AppData\Local\Instaloader\`  
- **Linux/macOS:** `~/.config/instaloader/`  

🔁 Si quieres reutilizarla dentro de Docker, copia el archivo `session-tu_usuario_instagram` a la carpeta del proyecto.

---

## ✨ Cómo funciona

1. Selecciona una plataforma (Instagram, YouTube, TikTok...)  
2. Escribe el nombre de usuario o palabra clave  
3. Haz clic en “Buscar”  
4. Se mostrará la información extraída  
5. Puedes descargarla en Excel  
6. Puedes ver el historial de búsquedas y eliminar entradas

---

## 🧪 Scrapers actuales disponibles

| Plataforma   | Estado       | Scraping básico | Scraping masivo         |
|--------------|--------------|------------------|--------------------------|
| Instagram    | ✅ Funciona   | ✅ Sí             | 🔜 En desarrollo          |
| YouTube      | ✅ Funciona   | ✅ Sí             | ❌ No aplica              |
| TikTok       | ✅ Funciona   | ✅ Sí             | 🔜 En desarrollo          |
| Facebook     | ✅ Funciona   | ✅ Sí             | 🔜 En desarrollo          |
| X (Twitter)  | ✅ Funciona   | ✅ Sí             | 🔜 En desarrollo          |
| Telegram     | ✅ Funciona   | ✅ Sí             | ❌ Solo canales           |
| Web (Duck)   | ✅ Funciona   | ✅ Sí             | ❌ Limitado por ratelimit |

---

## ⚠️ Notas importantes

- No se scrapea contenido privado ni se infringe ninguna política.  
- Solo se extraen datos públicamente visibles, como emails en bios o enlaces de contacto.  
- Algunas plataformas aplican limitaciones (CAPTCHAs, rate limit...).  
- Usa siempre cuentas de prueba si vas a hacer scraping masivo.  

---

## 🧹 Cosas ignoradas en Git

El archivo `.gitignore` incluye:

```bash
__pycache__/
*.session
.env
/exports/*.xlsx
/exports/*.csv
```

Si quieres mantener sesiones, colócalas en el proyecto y **NO las subas a Git**.

---

## 🧩 Futuras fases (en desarrollo)

- Scraping masivo de seguidores/seguidos   
- Tareas asíncronas con Celery + Redis  
- Rotación de proxies  
- Interfaz mejorada con Beezer  
- Exportación directa a CRM o Google Sheets  

---

## ✍️ Autor

- 👨‍💻 **Javier V.G.** – Desarrollador principal  

---

## ✅ Licencia

Proyecto educativo y experimental. No utilizar con fines comerciales sin permiso.
