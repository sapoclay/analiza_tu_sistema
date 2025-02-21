# Analiza Tu Sistema

Este proyecto es una aplicación de interfaz gráfica desarrollada en Python con Tkinter para analizar la información del sistema operativo, hardware, memoria, red y procesos en tiempo real.

## Características

- Muestra información detallada sobre el sistema operativo y hardware.

- Monitoriza el uso de CPU, memoria y discos.

- Obtiene detalles de la red y los procesos en ejecución.

- Visualiza información con una interfaz intuitiva y moderna.

- Soporta actualización en tiempo real del consumo de CPU.

## Requisitos

Este proyecto requiere Python 3 y las siguientes bibliotecas:

- tkinter (incluido en la instalación de Python)

- psutil

- cpuinfo

- platform

- socket

- os

- datetime

- webbrowser

Para sistemas Windows, se recomienda instalar wmi si se desea obtener información avanzada del hardware.

Todas estas dependencias se instalarán de forma automática al ejecutar el programa correctamente.

# Instalación y ejecución

Clona este repositorio:

```
git clone https://github.com/tu_usuario/analiza_tu_sistema.git
cd analiza_tu_sistema
```

Una vez que tengamos el programa en nuestro sistema, basta con escribir en la terminal:

En linux:
```
python3 run_app.py
```

En Windows:
```
python.exe run_app.py
```

## Uso

![ATS](https://github.com/user-attachments/assets/84e711eb-ed53-4129-b491-ab2472806bfe)

Al ejecutar la aplicación, se mostrará una ventana con varias pestañas, cada una proporcionando información detallada sobre un aspecto del sistema:

🖥️ Sistema: Detalles del sistema operativo y hardware.

⚡ CPU: Información sobre el procesador y su uso en tiempo real.

💾 Memoria: Estado de la memoria RAM y memoria de intercambio (swap).

💽 Discos: Estado de almacenamiento y actividad de disco.

🌐 Red: Direcciones IP, uso de datos y adaptadores de red.

📋 Procesos: Lista de procesos en ejecución con sus detalles.

📖 Info: Documentación y créditos.

## Contribución

Si deseas mejorar esta aplicación, puedes hacer un fork del repositorio y enviar un pull request con tus cambios.

## Licencia

Este proyecto está licenciado bajo la MIT License.
