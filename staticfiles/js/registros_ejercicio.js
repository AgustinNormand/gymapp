document.addEventListener('DOMContentLoaded', function() {
    console.log('Inicializando gráfico de registros de ejercicio...');
    
    try {
        // Obtener los datos del DOM
        const registrosEjercicio = [];
        const registrosElements = document.querySelectorAll('.registro-ejercicio');
        
        registrosElements.forEach(registro => {
            registrosEjercicio.push({
                fecha: registro.dataset.fecha,
                peso: parseFloat(registro.dataset.peso)
            });
        });
        
        // Si solo hay un registro, lo duplicamos para poder mostrar el gráfico
        if (registrosEjercicio.length === 1) {
            const unicoRegistro = registrosEjercicio[0];
            registrosEjercicio.push({
                fecha: unicoRegistro.fecha,
                peso: unicoRegistro.peso
            });
        }
        
        // Ordenar por fecha
        registrosEjercicio.sort((a, b) => {
            const fechaA = a.fecha.split('/').reverse().join('-');
            const fechaB = b.fecha.split('/').reverse().join('-');
            return new Date(fechaA) - new Date(fechaB);
        });
        
        // Preparar datos para el gráfico
        const fechas = registrosEjercicio.map(registro => registro.fecha);
        const pesos = registrosEjercicio.map(registro => registro.peso);
        
        // Crear el gráfico
        const ctx = document.getElementById('pesoChart').getContext('2d');
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: fechas,
                datasets: [{
                    label: 'Peso (kg)',
                    data: pesos,
                    borderColor: 'rgb(75, 192, 192)',
                    tension: 0.1,
                    fill: false
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: false,
                        title: {
                            display: true,
                            text: 'Peso (kg)'
                        },
                        ticks: {
                            callback: function(value) {
                                return value + ' kg';
                            }
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Fecha'
                        },
                        ticks: {
                            maxRotation: 45,
                            minRotation: 45
                        }
                    }
                },
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return 'Peso: ' + context.parsed.y + ' kg';
                            }
                        }
                    }
                }
            }
        });
        
        console.log('Gráfico de registros de ejercicio creado exitosamente');
        
    } catch (error) {
        console.error('Error al crear el gráfico de registros de ejercicio:', error);
    }
});
