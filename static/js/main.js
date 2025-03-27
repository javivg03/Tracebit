async function scrapear() {
  const username = document.getElementById("username").value;
  const plataforma = document.getElementById("plataforma").value;

  if (!username) return alert("Por favor ingresa un nombre de usuario o canal");

  document.getElementById("resultado").innerHTML = "";
  document.getElementById("loader").style.display = "block";
  document.getElementById("descarga").style.display = "none";

  const res = await fetch(`/scrape/${plataforma}?username=${username}`, {
    method: "POST"
  });

  document.getElementById("loader").style.display = "none"; // 🔁 Apagar spinner aquí también

  if (!res.ok) {
    document.getElementById("resultado").innerHTML = "❌ Error al scrapear.";
    return;
  }

  const json = await res.json();
  const data = json.data;
  const resultadoDiv = document.getElementById("resultado");

  let html = `<div class="card p-3"><h5 class="card-title">${data.nombre_completo || data.nombre || "Usuario"}</h5><ul class="list-group list-group-flush">`;
  for (const [key, value] of Object.entries(data)) {
    html += `<li class="list-group-item"><strong>${key.replace(/_/g, ' ')}:</strong> ${value}</li>`;
  }
  html += `</ul></div>`;
  resultadoDiv.innerHTML = html;

  const link = document.getElementById("link-descarga");
  link.href = json.excel_path;
  link.download = json.excel_path.split("/").pop();
  document.getElementById("descarga").style.display = "block";
}
async function buscarGoogle() {
  const q = document.getElementById("busqueda").value;
  const res = await fetch(`/buscar_google?query=${encodeURIComponent(q)}`);
  const data = await res.json();

  const div = document.getElementById("resultados-google");
  div.innerHTML = "";

  if (!data.resultados || data.resultados.length === 0) {
    div.innerHTML = "<p class='text-danger'>No se encontraron resultados.</p>";
    return;
  }

  data.resultados.forEach(r => {
    div.innerHTML += `
      <div class="card mb-2">
        <div class="card-body">
          <h5 class="card-title">${r.title}</h5>
          <p class="card-text">${r.snippet}</p>
          <a href="${r.link}" target="_blank" class="btn btn-outline-primary">Ver enlace</a>
        </div>
      </div>`;
  });
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
