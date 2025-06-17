// Sistema de ordenamiento personalizado para las tablas
document.addEventListener('DOMContentLoaded', function() {
    const tablaAsistencias = document.getElementById('tablaAsistencias');
    if (tablaAsistencias) {
        // Función para activar el ordenamiento en la tabla
        function activarOrdenamiento() {
            const headers = tablaAsistencias.querySelectorAll('th.sortable');
            const tbody = tablaAsistencias.querySelector('tbody');
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
            
            // Ordenar por defecto por la primera columna (fecha) de forma descendente
            if (headers.length > 0) {
                const defaultHeader = headers[0];
                ordenarTablaPorColumna(0, false); // false para orden descendente
                actualizarIconosYClases(defaultHeader, false);
                defaultHeader.classList.remove('asc');
                defaultHeader.classList.add('desc');
            }
        }
        
        // Activar el ordenamiento
        activarOrdenamiento();
    }

    // Gráfico de asistencias por mes
    document.addEventListener('DOMContentLoaded', function() {
        const asistenciasChart = document.getElementById('asistenciasChart');
        if (asistenciasChart) {
            console.log('Inicializando gráfico de asistencias...');
            
            // Preparar datos para el gráfico (agrupar por mes)
            const asistenciasPorMes = {};
            const mesesDisponibles = new Set();
            
            // Obtener las fechas del DOM
            const fechasElements = document.querySelectorAll('.fecha-asistencia');
            const fechasProcesadas = Array.from(fechasElements).map(el => el.textContent.trim());
            
            console.log('Fechas procesadas:', fechasProcesadas);
            
            // Procesar las fechas en JavaScript puro
            fechasProcesadas.forEach(fechaStr => {
                const fecha = new Date(fechaStr);
                if (isNaN(fecha.getTime())) {
                    console.error('Fecha inválida:', fechaStr);
                    return;
                }
                const mes = fecha.getMonth() + 1; // Los meses van de 0 a 11
                const anio = fecha.getFullYear();
                const clave = `${anio}-${mes.toString().padStart(2, '0')}`;
                
                mesesDisponibles.add(clave);
                asistenciasPorMes[clave] = (asistenciasPorMes[clave] || 0) + 1;
            });

            // Ordenar los meses cronológicamente
            const mesesOrdenados = Array.from(mesesDisponibles).sort();
            
            // Formatear etiquetas para mostrar (ej: 'Ene 2023')
            const mesesFormateados = mesesOrdenados.map(mesAnio => {
                const [anio, mes] = mesAnio.split('-');
                const fecha = new Date(anio, mes - 1, 1);
                return fecha.toLocaleString('es-AR', { month: 'short', year: 'numeric' });
            });
            
            // Crear array de conteos en el orden correcto
            const conteos = mesesOrdenados.map(mesAnio => asistenciasPorMes[mesAnio] || 0);
            
            console.log('Datos del gráfico:', {meses: mesesFormateados, conteos});

            try {
                // Verificar que Chart esté disponible
                if (typeof Chart === 'undefined') {
                    console.error('Chart.js no está disponible');
                    return;
                }
                
                // Crear el gráfico
                const ctx = asistenciasChart.getContext('2d');
                new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels: mesesFormateados,
                        datasets: [{
                            label: 'Asistencias',
                            data: conteos,
                            backgroundColor: 'rgba(78, 115, 223, 0.8)',
                            borderColor: 'rgba(78, 115, 223, 1)',
                            borderWidth: 1
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {
                            y: {
                                beginAtZero: true,
                                ticks: {
                                    stepSize: 1,
                                    precision: 0
                                }
                            }
                        },
                        plugins: {
                            legend: {
                                display: false
                            }
                        }
                    }
                });
                console.log('Gráfico inicializado correctamente');
            } catch (error) {
                console.error('Error al inicializar el gráfico:', error);
            }
        }
    });
});
