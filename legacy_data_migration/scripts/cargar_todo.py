import os
import subprocess

# Donde está cargar_todo.py
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))

SCRIPTS = [
    "cargar_socios.py",
    "cargar_ejercicios.py",
    "cargar_modalidades.py",
    "cargar_observaciones.py",
    "cargar_pesos.py",
]

def run_script(script_name):
    script_path = os.path.join(SCRIPTS_DIR, script_name)
    print(f"\n🚀 Ejecutando {script_name}...")
    try:
        subprocess.run(
            ["python", script_path],
            check=True,
            cwd=SCRIPTS_DIR,
            env={**os.environ, "PYTHONPATH": "/app"},  # 👈 este es el cambio clave
        )
    except subprocess.CalledProcessError as e:
        print(f"❌ Error ejecutando {script_name}")
        print(e)
        exit(1)

if __name__ == "__main__":
    print("📋 Iniciando carga completa de datos...\n")
    for script in SCRIPTS:
        run_script(script)
    print("\n✅ Todos los datos fueron cargados correctamente.")
