async function scrapear() {
  const username = document.getElementById("username").value.trim();
  const plataforma = document.getElementById("plataforma").value;

  if (!username) return alert("Por favor ingresa un nombre de usuario o palabra clave");

  document.getElementById("resultado").innerHTML = "";
  document.getElementById("loader").style.display = "block";
  document.getElementById("descarga").style.display = "none";

  console.log("📡 Enviando:", {
    plataforma,
    body: JSON.stringify({ username })
  });

  try {
    const res = await fetch(`/scrape/${plataforma}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ username })
    });

    document.getElementById("loader").style.display = "none";

    if (!res.ok) {
      const error = await res.json();
      document.getElementById("resultado").innerHTML = `❌ ${error.error || "Error al scrapear."}`;
      return;
    }

    const json = await res.json();
    const data = json.data;
    const resultadoDiv = document.getElementById("resultado");

    // Si es array (como en web scraping)
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
              <p class="card-text">${r.snippet || ""}</p>
              <p><strong>Email encontrado:</strong> ${r.email || "N/A"}</p>
              <a href="${r.link || r.url}" target="_blank" class="btn btn-outline-primary">Ver enlace</a>
            </div>
          </div>`;
      });

      resultadoDiv.innerHTML = html;
    } else {
      // Objeto único como en Instagram/Telegram/YouTube
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

    // Mostrar botón de descarga
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

  const res = await fetch("/historial", {
    method: "DELETE"
  });

  const data = await res.json();
  alert(data.message);
  document.getElementById("historial-container").style.display = "none";
}
