// Módulo de ordenamiento de tablas reutilizable
// Author: Cascade AI – 2025-06-17
// Aplica ordenamiento asc/desc haciendo clic en <th class="sortable"> dentro de cualquier
// tabla que posea la clase "tabla-gymapp".
//
// Uso: bastará con que cada tabla incluya las clases
//      class="table table-striped table-hover tabla-gymapp"
// y marque como ordenables los encabezados añadiendo "sortable" y opcionalmente un span
// con la clase "sort-icon" para mostrar la flecha.

(function () {
  /**
   * Inicializa el ordenamiento en todas las tablas que coincidan con el selector.
   * @param {string} selector - Selector CSS de las tablas a procesar.
   */
  function activarOrdenamiento(selector = '.tabla-gymapp') {
    const tablas = document.querySelectorAll(selector);
    tablas.forEach((tabla) => prepararTabla(tabla));
  }

  /**
   * Configura eventos de clic sobre los <th sortable> de la tabla dada.
   * @param {HTMLTableElement} tabla
   */
  function prepararTabla(tabla) {
    const headers = tabla.querySelectorAll('th.sortable');
    const tbody = tabla.querySelector('tbody');
    if (!headers.length || !tbody) return; // nada que hacer

    headers.forEach((header, index) => {
      header.dataset.col = index;
      header.addEventListener('click', () => {
        const current = header.dataset.order || 'desc'; // default desc
        const asc = current === 'desc';
        header.dataset.order = asc ? 'asc' : 'desc';
        ordenarTabla(tbody, index, asc);
        actualizarIconosYClases(headers, header, asc);
      });
    });

    // Orden inicial: primera columna desc
    ordenarTabla(tbody, 0, false);
    actualizarIconosYClases(headers, headers[0], false);
  }

  /**
   * Ordena las filas de tbody según la columna indicada.
   * @param {HTMLElement} tbody
   * @param {number} colIndex
   * @param {boolean} asc - true=ascendente
   */
  function ordenarTabla(tbody, colIndex, asc) {
    const filas = Array.from(tbody.querySelectorAll('tr'));
    const filasOrdenadas = filas.sort((a, b) => {
      let aText = a.children[colIndex].textContent.trim();
      let bText = b.children[colIndex].textContent.trim();

      // Si existe badge, usar su texto
      const aBadge = a.children[colIndex].querySelector('.badge');
      const bBadge = b.children[colIndex].querySelector('.badge');
      if (aBadge) aText = aBadge.textContent.trim();
      if (bBadge) bText = bBadge.textContent.trim();

      const aNum = parseFloat(aText.replace(',', '.'));
      const bNum = parseFloat(bText.replace(',', '.'));
      const ambosNumeros = !isNaN(aNum) && !isNaN(bNum);
      if (ambosNumeros) {
        return asc ? aNum - bNum : bNum - aNum;
      } else {
        return asc ? aText.localeCompare(bText) : bText.localeCompare(aText);
      }
    });
    filasOrdenadas.forEach((fila) => tbody.appendChild(fila));
  }

  /**
   * Actualiza clases e iconos en encabezados.
   */
  function actualizarIconosYClases(headers, clicked, asc) {
    headers.forEach((h) => {
      h.classList.remove('asc', 'desc');
      const icon = h.querySelector('.sort-icon');
      if (icon) icon.textContent = '⇅';
    });
    clicked.classList.add(asc ? 'asc' : 'desc');
    const icon = clicked.querySelector('.sort-icon');
    if (icon) icon.textContent = asc ? '▲' : '▼';
  }

  // Auto-init al cargar
  document.addEventListener('DOMContentLoaded', () => {
    // Asegurar que todas las tablas de Bootstrap tengan la clase estandarizada
    document.querySelectorAll('table.table').forEach((t) => t.classList.add('tabla-gymapp'));
    activarOrdenamiento();
  });
})();
