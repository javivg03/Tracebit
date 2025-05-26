let tareaActivaId = null; // Guardamos la tarea en curso para poder cancelarla si el usuario pulsa "Cancelar"

async function scrapear() {
  const username = document.getElementById("username").value.trim();
  const plataforma = document.getElementById("plataforma").value;
  const tipo = document.getElementById("tipo").value;
  const maxSeguidores = parseInt(document.getElementById("max_seguidores").value) || 3;

  if (!username) return alert("Por favor ingresa un nombre de usuario.");

  document.getElementById("resultado").innerHTML = "";
  document.getElementById("resultado").style.display = "none";
  document.getElementById("descarga").style.display = "none";
  document.getElementById("boton-cancelar").style.display = "none";
  resetearBarraProgreso();

  const endpointMap = {
    instagram: {
      perfil: "/instagram/perfil",
      seguidores: "/instagram/seguidores",
      seguidos: "/instagram/seguidos"
    },
    tiktok: {
      perfil: "/tiktok/perfil",
      seguidores: "/tiktok/seguidores",
      seguidos: "/tiktok/seguidos"
    },
    x: {
      perfil: "/x/perfil",
      tweets: "/x/tweets"
    },
    youtube: {
      canal: "/youtube/canal"
    },
    telegram: {
      canal: "/telegram/canal"
    },
    facebook: {
      perfil: "/facebook/perfil"
    },
    web: {
      perfil: "/web/perfil",
      buscar: "/web/buscar"
    }
  };

  const endpoint = endpointMap[plataforma]?.[tipo];
  if (!endpoint) {
    alert("Tipo de scraping no disponible para esta plataforma.");
    return;
  }

  // Scraping directo (perfil o canal)
  if (["perfil", "canal", "buscar"].includes(tipo)) {
    document.getElementById("loader").style.display = "block";
    document.getElementById("barra-progreso-container").style.display = "none";

    const habilitarBusquedaWeb = document.getElementById("habilitar_busqueda_web")?.checked || false;

    const body = tipo === "buscar"
      ? { query: username } // el campo de búsqueda libre
      : {
          username,
          habilitar_busqueda_web: document.getElementById("habilitar_busqueda_web")?.checked || false
        };

    try {
      const res = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body)
      });

      const json = await res.json();
      document.getElementById("loader").style.display = "none";

      if (!res.ok) {
        document.getElementById("resultado").innerHTML = `❌ ${json.error || "Error al scrapear."}`;
        return;
      }

      mostrarResultado(json);
      activarDescarga(json.excel_path, json.csv_path);

    } catch (err) {
      console.error("❌ Error inesperado:", err);
      document.getElementById("loader").style.display = "none";
      document.getElementById("resultado").innerHTML = "❌ Error inesperado al scrapear.";
    }

  // Scraping de tareas (seguidores, seguidos, tweets)
  } else if (["seguidores", "seguidos", "tweets"].includes(tipo)) {
    document.getElementById("loader").style.display = "none";
    document.getElementById("barra-progreso-container").style.display = "block";
    actualizarBarraProgreso(0, maxSeguidores);

    try {
      const payload = { username };

      if (tipo === "seguidores") payload.max_seguidores = maxSeguidores;
      if (tipo === "seguidos") payload.max_seguidos = maxSeguidores;
      if (tipo === "tweets") payload.max_tweets = maxSeguidores;

      const tareaRes = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      const { tarea_id } = await tareaRes.json();
      if (!tarea_id) throw new Error("Tarea no iniciada");

      tareaActivaId = tarea_id;
      document.getElementById("boton-cancelar").style.display = "inline-block";
      esperarResultado(tarea_id, maxSeguidores);

    } catch (err) {
      console.error("❌ Error al lanzar tarea:", err);
      document.getElementById("resultado").innerHTML = `❌ Error al iniciar scraping de ${tipo}.`;
    }
  }
}

// Cancelar tarea Celery activa
async function cancelarScraping() {
  if (!tareaActivaId) return;

  try {
    const res = await fetch(`/cancelar-tarea/${tareaActivaId}`, { method: "POST" });
    const json = await res.json();
    document.getElementById("boton-cancelar").style.display = "none";
    document.getElementById("barra-progreso-container").style.display = "none";
    document.getElementById("resultado").innerHTML = `⏹ ${json.mensaje || "Scraping cancelado"}`;
  } catch (err) {
    console.error("❌ Error al cancelar tarea:", err);
    document.getElementById("resultado").innerHTML = "❌ No se pudo cancelar la tarea.";
  }

  tareaActivaId = null;
}

// Espera el resultado de una tarea Celery
async function esperarResultado(tareaId, maxSeguidores) {
  let progreso = 0;
  const progresoInterval = setInterval(() => {
    if (progreso < maxSeguidores) {
      progreso++;
      actualizarBarraProgreso(progreso, maxSeguidores);
    }
  }, 2000);

  const check = async () => {
    try {
      const res = await fetch(`/resultado-tarea/${tareaId}`);
      if (!res.ok) throw new Error(`❌ Error HTTP ${res.status}`);
      const json = await res.json();

      if (json.estado === "pendiente") {
        setTimeout(check, 2000);
      } else {
        clearInterval(progresoInterval);
        document.getElementById("barra-progreso-container").style.display = "none";
        document.getElementById("boton-cancelar").style.display = "none";
        tareaActivaId = null;

        if (json.estado === "error") {
          document.getElementById("resultado").innerHTML = `❌ ${json.mensaje || "Error en la tarea de scraping."}`;
        } else {
          mostrarResultado(json.data);
          activarDescarga(json.excel_path, json.csv_path);
        }
      }

    } catch (err) {
      clearInterval(progresoInterval);
      document.getElementById("boton-cancelar").style.display = "none";
      console.error("❌ Error al obtener resultado:", err);
      document.getElementById("resultado").innerHTML = "❌ Error inesperado al obtener el resultado.";
    }
  };

  check();
}

// Muestra resultados en pantalla formateados
function mostrarResultado(data) {
  const resultadoDiv = document.getElementById("resultado");

  // Unificar: si es solo un objeto, convertirlo a array
  const lista = Array.isArray(data) ? data : (data ? [data] : []);

  if (lista.length === 0) {
    resultadoDiv.innerHTML = "<p>No se encontraron resultados.</p>";
    resultadoDiv.style.display = "block";
    return;
  }

  let tabla = "<table class='table table-striped table-bordered table-sm'>";
  tabla += "<thead><tr><th>👤 Usuario</th><th>📛 Nombre</th><th>📧 Email</th><th>📞 Teléfono</th><th>📌 Fuente</th></tr></thead><tbody>";

  lista.forEach(r => {
    tabla += "<tr>";
    tabla += `<td>${r.usuario || "-"}</td>`;
    tabla += `<td>${r.nombre || "-"}</td>`;
    tabla += `<td>${r.email || "-"}</td>`;
    tabla += `<td>${r.telefono || "-"}</td>`;
    tabla += `<td>${r.origen || "-"}</td>`;
    tabla += "</tr>";
  });

  tabla += "</tbody></table>";
  resultadoDiv.style.display = "block";
  resultadoDiv.innerHTML = tabla;
}

// Activa botones de descarga de Excel y/o CSV (con validación)
function activarDescarga(excelPath, csvPath = null) {
  const descargaDiv = document.getElementById("descarga");
  const excelLink = document.getElementById("link-descarga-excel");
  const csvLink = document.getElementById("link-descarga-csv");

  // Validar que los elementos existen en el DOM
  if (!descargaDiv || !excelLink || !csvLink) {
    console.warn("⚠️ Elementos de descarga no encontrados en el DOM.");
    return;
  }

  let mostrarDescarga = false;

  if (excelPath) {
    excelLink.href = excelPath;
    excelLink.download = excelPath.split("/").pop();
    excelLink.style.display = "inline-block";
    mostrarDescarga = true;
  } else {
    excelLink.style.display = "none";
  }

  if (csvPath) {
    csvLink.href = csvPath;
    csvLink.download = csvPath.split("/").pop();
    csvLink.style.display = "inline-block";
    mostrarDescarga = true;
  } else {
    csvLink.style.display = "none";
  }

  descargaDiv.style.display = mostrarDescarga ? "block" : "none";
}


// Actualiza visualmente la barra de progreso
function actualizarBarraProgreso(actual, total) {
  const porcentaje = Math.min(100, Math.floor((actual / total) * 100));
  const barra = document.getElementById("barra-progreso");
  barra.style.width = `${porcentaje}%`;
  barra.textContent = `${porcentaje}%`;
}

// Resetea la barra de progreso
function resetearBarraProgreso() {
  const barra = document.getElementById("barra-progreso");
  barra.style.width = "0%";
  barra.textContent = "0%";
  document.getElementById("barra-progreso-container").style.display = "none";
}

// Muestra u oculta opciones según tipo
function mostrarOpciones() {
  const tipo = document.getElementById("tipo").value;
  const plataforma = document.getElementById("plataforma").value;
  const mostrarCheckbox = (tipo === "perfil" || tipo === "canal") && plataforma !== "web";
  document.getElementById("opcion-busqueda-cruzada").style.display = mostrarCheckbox ? "block" : "none";
}

// Configura los selectores al cargar la página
document.addEventListener("DOMContentLoaded", () => {
  const plataformaSelect = document.getElementById("plataforma");
  const tipoSelect = document.getElementById("tipo");
  const grupoMax = document.getElementById("grupo-max-seguidores");
  const labelMax = document.getElementById("label-max");

  const tiposPorPlataforma = {
    instagram: ["perfil", "seguidores", "seguidos"],
    tiktok: ["perfil", "seguidores", "seguidos"],
    x: ["perfil", "tweets"],
    youtube: ["canal"],
    telegram: ["canal"],
    facebook: ["perfil"],
    web: ["perfil", "buscar"]
  };

  const etiquetasTipo = {
    perfil: "Perfil",
    seguidores: "Seguidores",
    seguidos: "Seguidos",
    tweets: "Tweets",
    canal: "Canal",
    buscar: "Palabra Clave"
  };

  plataformaSelect.addEventListener("change", () => {
    const plataforma = plataformaSelect.value;
    const tiposDisponibles = tiposPorPlataforma[plataforma] || [];

    tipoSelect.innerHTML = "";
    tiposDisponibles.forEach(tipo => {
      const option = document.createElement("option");
      option.value = tipo;
      option.textContent = etiquetasTipo[tipo] || tipo;
      tipoSelect.appendChild(option);
    });

    tipoSelect.dispatchEvent(new Event("change"));
    mostrarOpciones();
  });

  tipoSelect.addEventListener("change", () => {
    const tipo = tipoSelect.value;
    if (["seguidores", "seguidos", "tweets"].includes(tipo)) {
      grupoMax.style.display = "block";
      labelMax.textContent =
        tipo === "tweets" ? "Nº máximo de tweets a scrapear:" :
        tipo === "seguidores" ? "Nº máximo de seguidores a scrapear:" :
        "Nº máximo de seguidos a scrapear:";
    } else {
      grupoMax.style.display = "none";
    }
    mostrarOpciones();
  });

  plataformaSelect.dispatchEvent(new Event("change"));
});


// Mostrar / ocultar historial al hacer clic
async function toggleHistorial() {
    const contenedor = document.getElementById("historial-container");
    if (contenedor.style.display === "none") {
        try {
            const respuesta = await fetch("/historial");
            if (!respuesta.ok) throw new Error("Error al cargar historial");
            const historial = await respuesta.json();
            contenedor.innerHTML = generarTablaHistorial(historial);
            contenedor.style.display = "block";
        } catch (error) {
            contenedor.innerHTML = "<p>Error al cargar el historial.</p>";
            contenedor.style.display = "block";
        }
    } else {
        contenedor.style.display = "none";
    }
}

// Genera la tabla HTML con los datos del historial
function generarTablaHistorial(historial) {
    if (historial.length === 0) {
        return "<p>No hay registros de historial.</p>";
    }

    let tabla = "<table class='table table-bordered table-sm'><thead><tr><th>📅 Fecha</th><th>📱 Plataforma</th><th>👤 Usuario</th><th>✅ Resultado</th></tr></thead><tbody>";
    historial.forEach(registro => {
        tabla += `<tr>
            <td>${registro.fecha}</td>
            <td>${registro.plataforma}</td>
            <td>${registro.usuario}</td>
            <td>${registro.resultado}</td>
        </tr>`;
    });
    tabla += "</tbody></table>";
    return tabla;
}

async function borrarHistorial() {
    if (!confirm("¿Estás seguro de que quieres borrar el historial?")) return;
    const respuesta = await fetch("/historial", { method: "DELETE" });
    if (respuesta.ok) {
        alert("Historial borrado correctamente.");
        document.getElementById("historial-container").innerHTML = "";
    } else {
        alert("Error al borrar el historial.");
    }
}
