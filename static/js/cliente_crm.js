document.addEventListener("DOMContentLoaded", function () {
    console.log("✅ Script cliente_crm.js cargado y DOM listo");

    // Buscar el div donde mostrar la actividad
    const actividadDiv = document.getElementById("actividad-crm");

    if (!actividadDiv) {
        console.error("❌ No se encontró el div #actividad-crm");
        return;
    } else {
        console.log("✅ Div #actividad-crm encontrado");
    }

    // Revisar que la URL esté definida
    if (typeof CRM_INTERACCIONES_URL === "undefined") {
        console.error("❌ CRM_INTERACCIONES_URL no está definida");
        actividadDiv.innerHTML = "<p>Error: URL de CRM no definida.</p>";
        return;
    }

    console.log("🌐 Intentando hacer fetch a:", CRM_INTERACCIONES_URL);

    fetch(CRM_INTERACCIONES_URL)
        .then(response => {
            console.log("📦 Respuesta recibida del servidor:", response);
            if (!response.ok) {
                throw new Error(`Error en la respuesta del servidor: ${response.status} ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            console.log("📄 Datos JSON recibidos:", data);

            // Limpiar mensaje de carga
            actividadDiv.innerHTML = "";

            if (!data.interacciones || data.interacciones.length === 0) {
                console.log("ℹ️ No hay interacciones para mostrar");
                actividadDiv.innerHTML = "<p>No hay actividad reciente.</p>";
                return;
            }

            // Recorrer interacciones y agregarlas al div
            data.interacciones.forEach(item => {
                console.log("➡️ Procesando interacción:", item);

                const div = document.createElement("div");
                div.classList.add("border-b", "border-gray-300", "py-2");

                div.innerHTML = `
                    <strong>${item.tipo}</strong><br>
                    ${item.nota}<br>
                    <small>${item.fecha}</small>
                    <span class="ml-2 text-purple-600 font-semibold">${item.estado}</span>
                `;

                actividadDiv.appendChild(div);
            });
        })
        .catch(error => {
            console.error("❌ Error cargando actividad CRM:", error);
            actividadDiv.innerHTML = "<p>Error al cargar la actividad.</p>";
        });
});
