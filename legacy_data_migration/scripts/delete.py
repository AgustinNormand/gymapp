import pandas as pd
import pprint

def generar_diccionario_socios_y_pesos(ruta_csv, ruta_output):
    # Leer el CSV
    df = pd.read_csv(ruta_csv)

    # Renombrar columnas
    df.columns = ['NOMBRE', 'OBSERVACION', 'SUMO', 'ELEVACIONES', 'CUADRICEPS', 'SENTADILLAS', 
                  'REMO 1BB', 'REMO POLEA', 'TRICEPS POLEA', 'DORSALES', 'PECHO']

    # Dropear la primer fila si es cabecera repetida
    df = df.drop(index=0)

    socios_y_pesos = []

    for idx, row in df.iterrows():
        socio = str(row['NOMBRE']).strip()
        if pd.isna(socio) or socio == '':
            continue

        ejercicios = {}
        for ejercicio in ['SUMO', 'ELEVACIONES', 'CUADRICEPS', 'SENTADILLAS', 
                          'REMO 1BB', 'REMO POLEA', 'TRICEPS POLEA', 'DORSALES', 'PECHO']:
            valor = row[ejercicio]
            if pd.isna(valor) or valor == "-":
                ejercicios[ejercicio] = None
            else:
                ejercicios[ejercicio] = str(valor).strip()

        socios_y_pesos.append((socio, ejercicios))

    # Formatear con pprint
    socios_y_pesos_formateado = pprint.pformat(socios_y_pesos, width=120)

    # Escribir al archivo
    with open(ruta_output, 'w', encoding='utf-8') as f:
        f.write('SOCIOS_Y_PESOS = ')
        f.write(socios_y_pesos_formateado)

    print(f"✔️ Diccionario generado exitosamente en {ruta_output}")

# --- USO ---
generar_diccionario_socios_y_pesos('/Users/agustin/Downloads/PLANIFICACION FUNCIONAL - ALUMNOS.csv', 'output_socios_y_pesos.py')

