async function scrapear() {
  const username = document.getElementById("username").value.trim();
  const plataforma = document.getElementById("plataforma").value;
  const tipo = document.getElementById("tipo").value;
  const maxSeguidores = parseInt(document.getElementById("max_seguidores").value) || 3;

  if (!username) return alert("Por favor ingresa un nombre de usuario.");

  // Limpiar resultados anteriores
  document.getElementById("resultado").innerHTML = "";
  document.getElementById("descarga").style.display = "none";
  resetearBarraProgreso();

  if (tipo === "perfil") {
    document.getElementById("loader").style.display = "block";  // Mostrar spinner
    document.getElementById("barra-progreso-container").style.display = "none"; // Ocultar barra

    try {
      const res = await fetch(`/scrape/${plataforma}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username })
      });

      const json = await res.json();
      document.getElementById("loader").style.display = "none"; // Ocultar spinner

      if (!res.ok) {
        document.getElementById("resultado").innerHTML = `❌ ${json.error || "Error al scrapear."}`;
        return;
      }

      mostrarResultado(json.data);
      activarDescarga(json.excel_path);

    } catch (err) {
      console.error("❌ Error inesperado:", err);
      document.getElementById("loader").style.display = "none";
      document.getElementById("resultado").innerHTML = "❌ Error inesperado al scrapear.";
    }

  } else if (tipo === "seguidores") {
    document.getElementById("loader").style.display = "none"; // Ocultar spinner
    document.getElementById("barra-progreso-container").style.display = "block"; // Mostrar barra
    actualizarBarraProgreso(0, maxSeguidores); // Reiniciar barra a 0

    try {
      const tareaRes = await fetch(`/scrapear/seguidores-info/${username}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ max_seguidores: maxSeguidores })
      });

      const { tarea_id } = await tareaRes.json();
      esperarResultado(tarea_id, maxSeguidores);

    } catch (err) {
      console.error("❌ Error al lanzar tarea:", err);
      document.getElementById("resultado").innerHTML = "❌ Error al iniciar scraping de seguidores.";
    }
  }
}
document.addEventListener("DOMContentLoaded", () => {
  const tipoSelect = document.getElementById("tipo");
  const grupoMax = document.getElementById("grupo-max-seguidores");

  tipoSelect.addEventListener("change", () => {
    if (tipoSelect.value === "seguidores") {
      grupoMax.style.display = "block";
    } else {
      grupoMax.style.display = "none";
    }
  });
});

async function esperarResultado(tareaId, maxSeguidores) {
  let progreso = 0;
  const progresoInterval = setInterval(() => {
    if (progreso < maxSeguidores) {
      progreso++;
      actualizarBarraProgreso(progreso, maxSeguidores);
    }
  }, 2000); // Avanza cada 2 segundos (ajusta si hace falta)

  const check = async () => {
    try {
      const res = await fetch(`/resultado-tarea/${tareaId}`);

      if (!res.ok) {
        const text = await res.text();
        throw new Error(`❌ Error HTTP ${res.status}: ${text}`);
      }

      const json = await res.json();

      if (json.estado === "pendiente") {
        setTimeout(check, 2000); // volver a consultar
      } else {
        clearInterval(progresoInterval);
        actualizarBarraProgreso(maxSeguidores, maxSeguidores); // Completar barra

        if (json.estado === "error") {
          document.getElementById("resultado").innerHTML = `❌ ${json.mensaje || "Error en la tarea de scraping."}`;
        } else if (json.estado === "ok" || json.estado === "completado") {
          mostrarResultado(json.data);
          activarDescarga(json.excel_path);
        }
      }

    } catch (err) {
      clearInterval(progresoInterval);
      console.error("❌ Error al obtener resultado:", err);
      document.getElementById("resultado").innerHTML = "❌ Error inesperado al obtener el resultado.";
    }
  };

  check();
}

function actualizarBarraProgreso(actual, total) {
  const porcentaje = Math.min(100, Math.floor((actual / total) * 100));
  const barra = document.getElementById("barra-progreso");
  barra.style.width = `${porcentaje}%`;
  barra.textContent = `${porcentaje}%`;
}

function resetearBarraProgreso() {
  const barra = document.getElementById("barra-progreso");
  barra.style.width = "0%";
  barra.textContent = "0%";
  document.getElementById("barra-progreso-container").style.display = "none";
}

function mostrarResultado(data) {
  const resultadoDiv = document.getElementById("resultado");
  if (!data || data.length === 0) {
    resultadoDiv.innerHTML = "<p>No se encontraron resultados.</p>";
    return;
  }

  let html = "";
  (Array.isArray(data) ? data : [data]).forEach(r => {
    html += `<div class="card p-3 mb-2"><h5>${r.nombre || r.usuario}</h5><ul class="list-group list-group-flush">`;
    for (const key in r) {
      if (Object.hasOwn(r, key)) {
        const valor = Array.isArray(r[key]) ? r[key].join(", ") : r[key];
        html += `<li class="list-group-item"><strong>${key.replace(/_/g, ' ')}:</strong> ${valor}</li>`;
      }
    }
    html += "</ul></div>";
  });

  resultadoDiv.innerHTML = html;
}

function activarDescarga(path) {
  const link = document.getElementById("link-descarga");
  link.href = path;
  link.download = path.split("/").pop();
  document.getElementById("descarga").style.display = "block";
}
