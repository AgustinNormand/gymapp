// Módulo para habilitar reordenamiento (drag & drop) de columnas en tablas
// Funciona en tablas Bootstrap / HTML estándar. No tiene dependencias externas.
// Autor: Cascade AI – 2025-06-17
// 
// Uso: Asigna la clase "draggable-cols" a la tabla o a un elemento contenedor. Todas
// las celdas <th> del thead se harán arrastrables. El usuario puede arrastrar un
// encabezado y soltarlo en otra posición. El script moverá tanto el encabezado como
// las celdas correspondientes de cada fila del tbody para que la tabla siga siendo
// coherente.
//
// Para la vista de Registrar Asistencia, la tabla posee la clase "table-ejercicios",
// que ya se marca como .table. Añadimos la clase "draggable-cols" en runtime para no
// tocar las plantillas.
(function () {
  "use strict";

  /**
   * Añade soporte de drag&drop a una tabla.
   * @param {HTMLTableElement} tabla
   */
  // --- Persistencia ---------------------------------------------------------
  function storageKey(tabla) {
    return (
      'colOrder_' +
      (tabla.id || window.location.pathname + '_' + Array.from(document.querySelectorAll('table')).indexOf(tabla))
    );
  }
  function snapshot(tabla) {
    return Array.from(tabla.querySelectorAll('thead th')).map((th) => Number(th.dataset.originIdx));
  }
  function saveOrder(tabla) {
    try {
      localStorage.setItem(storageKey(tabla), JSON.stringify(snapshot(tabla)));
    } catch {}
  }
  function restoreOrder(tabla) {
    let saved;
    try {
      saved = JSON.parse(localStorage.getItem(storageKey(tabla)) || 'null');
    } catch {
      saved = null;
    }
    if (!Array.isArray(saved)) return;
    saved.forEach((orig, target) => {
      const current = Array.from(tabla.querySelectorAll('thead th')).findIndex(
        (th) => Number(th.dataset.originIdx) === orig
      );
      if (current !== -1 && current !== target) moverColumna(tabla, current, target);
    });
  }
  // -----------------------------------------------------------------------
  function habilitarDragEnTabla(tabla) {
    const headers = tabla.querySelectorAll("thead th");
    headers.forEach((th, index) => {
      // Guardar índice original una sola vez
      if (!th.dataset.originIdx) th.dataset.originIdx = index;
      th.draggable = true;
  

      th.addEventListener("dragstart", (e) => {
        e.dataTransfer.effectAllowed = 'move';
        e.dataTransfer.setData('text/plain', th.cellIndex.toString());
        th.classList.add("dragging-col");
      });

      th.addEventListener("dragover", (e) => {
        e.preventDefault(); // Necesario para permitir drop
        e.dataTransfer.dropEffect = "move";
        th.classList.add("dragover-col");
      });

      th.addEventListener("dragleave", () => {
        th.classList.remove("dragover-col");
      });

      th.addEventListener("drop", (e) => {
        e.preventDefault();
        const fromIndex = parseInt(e.dataTransfer.getData('text/plain'), 10);
        const toIndex = th.cellIndex;
        th.classList.remove("dragover-col");
        moverColumna(tabla, fromIndex, toIndex);
        // Actualizar dataset indices tras reordenar
        
        saveOrder(tabla);
      });

      th.addEventListener("dragend", () => {
        th.classList.remove("dragging-col");
        tabla.querySelectorAll("thead th").forEach((h) => h.classList.remove("dragover-col"));
      });
    });
  }

  /**
   * Mueve una columna completa desde una posición a otra.
   * @param {HTMLTableElement} tabla
   * @param {number} fromIndex
   * @param {number} toIndex
   */
  function moverColumna(tabla, fromIndex, toIndex) {
    if (fromIndex === toIndex) return;

    const moverEnFila = (fila) => {
      const celdas = fila.children;
      if (toIndex < fromIndex) {
        fila.insertBefore(celdas[fromIndex], celdas[toIndex]);
      } else {
        fila.insertBefore(celdas[fromIndex], celdas[toIndex + 1]);
      }
    };

    // Mover encabezado
    moverEnFila(tabla.tHead.rows[0]);
    // Mover cada fila del cuerpo
    tabla.tBodies.forEach
      ? tabla.tBodies.forEach((tbody) => {
          Array.from(tbody.rows).forEach(moverEnFila);
        })
      : Array.from(tabla.tBodies).forEach((tbody) => {
          Array.from(tbody.rows).forEach(moverEnFila);
        });
  }

  // Añadimos estilos básicos para feedback visual
  const style = document.createElement("style");
  style.textContent = `
    th.dragging-col {
      opacity: 0.4;
    }
    th.dragover-col {
      outline: 2px dashed #0d6efd;
    }
  `;
  document.head.appendChild(style);

  // Auto-inicialización cuando el DOM está listo
  document.addEventListener("DOMContentLoaded", () => {
    // Asegurar que tabla-ejercicios pueda reordenar columnas
    document.querySelectorAll("table.table-ejercicios").forEach((tabla) => {
      tabla.classList.add("draggable-cols");
    });
    document.querySelectorAll('table.draggable-cols').forEach((t) => {
      habilitarDragEnTabla(t);
      restoreOrder(t);
    });
  });
})();
