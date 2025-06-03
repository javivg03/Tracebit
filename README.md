# 🔎 Tracebit – Scraping Multiplataforma de Perfiles Públicos

Tracebit es una herramienta web profesional para la extracción automatizada de datos públicos desde redes sociales y otras plataformas online. Está diseñada para facilitar tareas de captación, análisis y marketing mediante un sistema multired inteligente, que permite extraer información de contacto, seguidores o actividad pública de forma organizada y exportable.

> Proyecto desarrollado como parte del Grado de Desarrollo de Aplicaciones Web (DAW), con aplicación directa en entornos reales de empresa.

---

## 🚀 Tecnologías utilizadas

- 🐍 Python 3.11  
- ⚡ FastAPI  
- 🧠 Playwright async (scraping avanzado con proxies)  
- 🎯 HTML, CSS y JavaScript (frontend funcional)  
- 🔄 Celery + Redis (scraping masivo en segundo plano)  
- 🐳 Docker y Docker Compose  
- 📄 Pandas (exportación Excel/CSV)

---

## 🛠️ Requisitos previos

1. Tener [Docker Desktop](https://www.docker.com/products/docker-desktop/) instalado  
2. Tener `git` instalado  
3. Usar terminal moderna (PowerShell, WSL o Bash)  
4. Opcional: Añadir proxies en `services/proxies.json` si deseas scraping masivo sin bloqueos

---

## 📦 Instalación rápida

```bash
git clone https://github.com/TU-USUARIO/Tracebit.git
cd Tracebit
docker-compose up --build
```

➡️ Abre [http://localhost:8000](http://localhost:8000) en tu navegador

---

## ✨ Cómo funciona

1. Selecciona la plataforma (Instagram, TikTok, YouTube, etc.)
2. Selecciona el tipo de scraping:
   - Perfil individual (async, rápido)
   - Seguidores / seguidos / tweets (masivo, requiere tiempo)
3. Introduce el nombre de usuario (o nombre real)
4. Elige si deseas activar la búsqueda cruzada web (opcional)
5. Pulsa **Buscar**
6. Visualiza los resultados y exporta a Excel o CSV
7. Revisa el historial, repite o elimina búsquedas anteriores

---

## 🧪 Scrapers disponibles

| Plataforma   | Estado       | Perfil individual | Seguidores / Seguidos / Tweets |
|--------------|--------------|-------------------|---------------------------------|
| Instagram    | ✅ Funciona   | ✅ Sí              | ✅ Sí (Celery)                  |
| TikTok       | ✅ Funciona   | ✅ Sí              | ✅ Sí (Celery)                  |
| X (Twitter)  | ✅ Funciona   | ✅ Sí              | ✅ Tweets recientes (Celery)   |
| YouTube      | ✅ Funciona   | ✅ Sí              | ❌ No aplica                   |
| Facebook     | ✅ Funciona   | ✅ Sí              | 🔜 En desarrollo               |
| Telegram     | ✅ Funciona   | ✅ Solo canales    | ❌ No aplica                   |

> ❌ Web scraping general (DuckDuckGo/Bing) está desactivado actualmente por bloqueos y rendimiento.

---

## 📤 Exportación de resultados

- Resultados estructurados en `exports/`
- Formatos disponibles: `.xlsx`, `.csv`
- Accesibles desde la interfaz o por URL directa `/download/...`
- Compatible con CRM, hojas de cálculo o tratamiento externo

---

## 📜 Historial y control

- Guardado automático de todas las búsquedas
- Visualización cronológica
- Permite repetir, exportar o eliminar entradas
- Evita scrapear duplicados en un mismo día

---

## ⚙️ Automatización avanzada

- Flujo multired: si no se encuentra dato en una red, pasa a la siguiente
- Validación automática de emails y teléfonos (formato, duplicados, spam)
- Scraping masivo en segundo plano con Celery + Redis
- Proxies rotativos gestionados desde `services/proxy_pool.py`

---

## 🧩 Mejoras futuras previstas

- Automatización de exportaciones periódicas (ej: envío a Google Sheets)
- Panel de administración para historial, tareas y configuración
- Integración con herramientas como n8n, Zapier o CRMs

---

## 🧑‍💻 Autor

- **Javier Villaseñor García**
  - Técnico Superior en Desarrollo de Aplicaciones Web
  - Especializado en ciberseguridad, protección de datos, scraping y automatización
  - Perfil híbrido legal–técnico orientado a soluciones reales

---

## ⚖️ Licencia

Este proyecto está licenciado bajo una **licencia personalizada de uso no comercial**.

Puedes utilizar, modificar y redistribuir este software con fines personales, educativos o académicos, pero se prohíbe el uso comercial sin autorización expresa.

Consulta el archivo [LICENSE.txt](./LICENSE.txt) para ver los términos completos.

---

## 📌 Aviso legal

Tracebit se ha desarrollado con fines educativos, y solo extrae información pública disponible en perfiles abiertos.  
El uso indebido de esta herramienta queda bajo la responsabilidad del usuario.  
Se recomienda respetar las políticas de uso de cada plataforma y la legislación vigente sobre protección de datos.

---

## 📎 Recursos

- Documentación técnica completa en `/docs/`
- Capturas, ejemplos y código fuente incluidos en el repositorio
- Compatible con despliegue en VPS, Hostinger, Contabo, etc.

---

¡Gracias por revisar este proyecto!  
Puedes contactarme o revisar mi perfil para más información sobre cómo aplicar Tracebit en contextos reales.