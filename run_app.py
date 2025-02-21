import os
import subprocess
import sys

def crear_entorno_virtual():
    print("Creando entorno virtual...")
    subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)

def activar_entorno_virtual():
    if os.name == "nt":  # Windows
        activate_script = os.path.join("venv", "Scripts", "activate.bat")
    else:  # Linux/Unix/Mac
        activate_script = os.path.join("venv", "bin", "activate")
    print(f"Activando entorno virtual: {activate_script}")
    return activate_script

def instalar_dependencias():
    print("Instalando dependencias desde requirements.txt...")
    pip_path = os.path.join("venv", "Scripts", "pip") if os.name == "nt" else os.path.join("venv", "bin", "pip")
    if not os.path.exists("requirements.txt"):
        print("Error: No se encontró el archivo requirements.txt")
        sys.exit(1)
    subprocess.run([pip_path, "install", "-r", "requirements.txt"], check=True)

def ejecutar_main():
    print("Ejecutando main.py...")
    python_path = os.path.join("venv", "Scripts", "python") if os.name == "nt" else os.path.join("venv", "bin", "python")
    project_root = os.path.abspath(".")  # Directorio raíz del proyecto
    env = {**os.environ, "PYTHONPATH": project_root}  # PYTHONPATH al entorno
    subprocess.run(
        [python_path, "main.py"],
        check=True,
        env=env
    )

if __name__ == "__main__":
    # Verificar si el entorno virtual ya existe
    if not os.path.exists("venv"):
        crear_entorno_virtual()
    
    # Activar entorno virtual (opcional, pero útil para confirmación visual en entornos manuales)
    activar_entorno_virtual()

    # Instalar dependencias
    instalar_dependencias()
    
    # Ejecutar la aplicación
    ejecutar_main()