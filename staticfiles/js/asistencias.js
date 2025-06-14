// Inicializar DataTable para las asistencias
document.addEventListener('DOMContentLoaded', function() {
    const tablaAsistencias = document.getElementById('tablaAsistencias');
    if (tablaAsistencias) {
        $('#tablaAsistencias').DataTable({
            order: [[0, 'desc']], // Ordenar por la primera columna (fecha) de forma descendente
            language: {
                url: '//cdn.datatables.net/plug-ins/1.13.4/i18n/es-ES.json',
                search: 'Buscar:',
                paginate: {
                    first: 'Primero',
                    last: 'Último',
                    next: 'Siguiente',
                    previous: 'Anterior'
                },
                lengthMenu: 'Mostrar _MENU_ registros por página',
                info: 'Mostrando _START_ a _END_ de _TOTAL_ registros',
                infoEmpty: 'No hay registros disponibles',
                infoFiltered: '(filtrado de _MAX_ registros en total)'
            },
            pageLength: 10,
            responsive: true,
            stateSave: true, // Guardar el estado de ordenación, búsqueda y paginación
            columnDefs: [
                { type: 'date', targets: 0 } // Especificar que la primera columna contiene fechas para ordenación correcta
            ]
        });
    }

    // Gráfico de asistencias por mes
    if (document.getElementById('asistenciasChart')) {
        console.log('Inicializando gráfico de asistencias...');
        
        // Preparar datos para el gráfico (agrupar por mes)
        const asistenciasPorMes = {};
        const mesesDisponibles = new Set();
        
        // Obtener las fechas del DOM
        const fechasElements = document.querySelectorAll('.fecha-asistencia');
        const fechasProcesadas = Array.from(fechasElements).map(el => el.textContent.trim());
        
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

        // Crear el gráfico
        const ctx = document.getElementById('asistenciasChart').getContext('2d');
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
    }
});
