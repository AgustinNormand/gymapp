// Sistema de ordenamiento personalizado para la tabla de socios
document.addEventListener('DOMContentLoaded', function() {
    const tablaSocios = document.getElementById('tablaSocios');
    if (tablaSocios) {
        // Función para activar el ordenamiento en la tabla
        function activarOrdenamiento() {
            const headers = tablaSocios.querySelectorAll('th.sortable');
            const tbody = tablaSocios.querySelector('tbody');
            const filas = Array.from(tbody.querySelectorAll('tr'));
            
            // Función para ordenar la tabla por columna
            function ordenarTablaPorColumna(colIndex, asc = true) {
                const filasOrdenadas = filas.sort((a, b) => {
                    // Extraer el texto de la celda correspondiente
                    let aText = a.children[colIndex].textContent.trim();
                    let bText = b.children[colIndex].textContent.trim();
                    
                    // Si hay un badge (span), extraer solo el número
                    const aBadge = a.children[colIndex].querySelector('.badge');
                    const bBadge = b.children[colIndex].querySelector('.badge');
                    
                    if (aBadge) aText = aBadge.textContent.trim();
                    if (bBadge) bText = bBadge.textContent.trim();
                    
                    // Intentar convertir a números si es posible
                    const aNum = parseFloat(aText.replace(',', '.'));
                    const bNum = parseFloat(bText.replace(',', '.'));
                    const ambosNumeros = !isNaN(aNum) && !isNaN(bNum);
                    
                    if (ambosNumeros) {
                        return asc ? aNum - bNum : bNum - aNum;
                    } else {
                        return asc
                            ? aText.localeCompare(bText)
                            : bText.localeCompare(aText);
                    }
                });
                
                // Reordenar las filas en el DOM
                filasOrdenadas.forEach(fila => tbody.appendChild(fila));
            }
            
            // Función para actualizar los iconos y clases de ordenamiento
            function actualizarIconosYClases(clickedHeader, asc) {
                headers.forEach(h => {
                    h.classList.remove('asc', 'desc');
                    const icon = h.querySelector('.sort-icon');
                    if (icon) icon.textContent = '⇅';
                });
                
                clickedHeader.classList.add(asc ? 'asc' : 'desc');
                const icon = clickedHeader.querySelector('.sort-icon');
                if (icon) icon.textContent = asc ? '▲' : '▼';
            }
            
            // Asignar eventos a los encabezados para ordenar
            headers.forEach(header => {
                header.addEventListener('click', () => {
                    const colIndex = parseInt(header.dataset.col);
                    const isCurrentlyAsc = header.classList.contains('asc');
                    const asc = !isCurrentlyAsc;
                    
                    ordenarTablaPorColumna(colIndex, asc);
                    actualizarIconosYClases(header, asc);
                });
            });
            
            // Ordenar por defecto por la primera columna (nombre) de forma ascendente
            if (headers.length > 0) {
                const defaultHeader = headers[0];
                ordenarTablaPorColumna(0, true); // true para orden ascendente
                actualizarIconosYClases(defaultHeader, true);
                defaultHeader.classList.remove('desc');
                defaultHeader.classList.add('asc');
            }
        }
        
        // Activar el ordenamiento
        activarOrdenamiento();
    }
});
