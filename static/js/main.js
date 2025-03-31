async function scrapear() {
  const username = document.getElementById("username").value.trim();
  const plataforma = document.getElementById("plataforma").value;

  if (!username) return alert("Por favor ingresa un nombre de usuario o palabra clave");

  document.getElementById("resultado").innerHTML = "";
  document.getElementById("loader").style.display = "block";
  document.getElementById("descarga").style.display = "none";

  try {
    const res = await fetch(`/scrape/${plataforma}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username })
    });

    const json = await res.json();
    document.getElementById("loader").style.display = "none";

    if (!res.ok) {
      console.error("❌ Error recibido:", json);
      document.getElementById("resultado").innerHTML = `❌ ${json.error || "Error al scrapear."}`;
      return;
    }

    const data = json.data;
    const resultadoDiv = document.getElementById("resultado");

    if (!data) {
      resultadoDiv.innerHTML = "❌ No se pudieron obtener datos del perfil.";
      return;
    }

    if (Array.isArray(data)) {
      if (data.length === 0) {
        resultadoDiv.innerHTML = "<p>No se encontraron resultados.</p>";
        return;
      }

      let html = "";
      data.forEach(r => {
        html += `
          <div class="card mb-2">
            <div class="card-body">
              <h5 class="card-title">${r.title || r.titulo || "Resultado"}</h5>
              <p class="card-text">${r.snippet || r.resumen || ""}</p>
              <p><strong>Emails:</strong> ${(r.emails || [r.email] || []).join(", ") || "N/A"}</p>
              <p><strong>Teléfonos:</strong> ${(r.telefonos || []).join(", ") || "N/A"}</p>
              <a href="${r.link || r.url || "#"}" target="_blank" class="btn btn-outline-primary">Ver enlace</a>
            </div>
          </div>`;
      });

      resultadoDiv.innerHTML = html;
    } else {
      let html = `<div class="card p-3"><h5 class="card-title">${data.nombre || data.usuario || "Usuario"}</h5><ul class="list-group list-group-flush">`;

      for (const key in data) {
        if (Object.hasOwn(data, key)) {
          const valor = Array.isArray(data[key]) ? data[key].join(", ") : data[key];
          html += `<li class="list-group-item"><strong>${key.replace(/_/g, ' ')}:</strong> ${valor}</li>`;
        }
      }

      html += `</ul></div>`;
      resultadoDiv.innerHTML = html;
    }

    const link = document.getElementById("link-descarga");
    link.href = json.excel_path;
    link.download = json.excel_path.split("/").pop();
    document.getElementById("descarga").style.display = "block";

  } catch (err) {
    console.error("❌ Error inesperado:", err);
    document.getElementById("loader").style.display = "none";
    document.getElementById("resultado").innerHTML = "❌ Error inesperado al scrapear.";
  }
}

async function toggleHistorial() {
  const container = document.getElementById("historial-container");
  if (container.style.display === "none") {
    await verHistorial();
    container.style.display = "block";
  } else {
    container.style.display = "none";
  }
}

async function verHistorial() {
  const res = await fetch("/historial");
  const data = await res.json();
  const contenedor = document.getElementById("historial-container");
  contenedor.innerHTML = "";

  if (!data.historial || data.historial.length === 0) {
    contenedor.innerHTML = "<p>No hay historial aún.</p>";
    return;
  }

  const tabla = document.createElement("table");
  tabla.className = "table table-striped";

  const encabezados = Object.keys(data.historial[0]);
  const thead = document.createElement("thead");
  const filaHead = document.createElement("tr");
  encabezados.forEach(col => {
    const th = document.createElement("th");
    th.textContent = col;
    filaHead.appendChild(th);
  });
  thead.appendChild(filaHead);
  tabla.appendChild(thead);

  const tbody = document.createElement("tbody");
  data.historial.forEach(item => {
    const fila = document.createElement("tr");
    encabezados.forEach(col => {
      const td = document.createElement("td");
      td.textContent = item[col];
      fila.appendChild(td);
    });
    tbody.appendChild(fila);
  });

  tabla.appendChild(tbody);
  contenedor.appendChild(tabla);
}

async function borrarHistorial() {
  if (!confirm("¿Seguro que quieres borrar todo el historial?")) return;

  const res = await fetch("/historial", { method: "DELETE" });
  const data = await res.json();
  alert(data.message);
  document.getElementById("historial-container").style.display = "none";
}