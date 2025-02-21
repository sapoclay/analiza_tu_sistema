import tkinter as tk
from tkinter import ttk
import psutil
import platform
import cpuinfo
import socket
import os
from datetime import datetime
import webbrowser

class SystemInfoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Analiza Tu Sistema")
        self.root.geometry("800x600")
        self.style = ttk.Style()
        self.style.theme_use("clam") # Tema seleccionado
        if platform.system() == "Windows":
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(1) # Para evitar problemas de escalado en pantallas de alta resolución
        self.create_ui() # Crear la interfaz de usuario
        self.get_system_info() # Obtener información del sistema
        
    # Método para crear la interfaz de usuario
    def create_ui(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
         # Configurar peso de fila y columna en la raíz
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.style.configure("green.Horizontal.TProgressbar", foreground='green', background='green')
        self.style.map("green.Horizontal.TProgressbar", 
                   foreground=[('active', 'green')], 
                   background=[('active', 'green')])
        # Diccionario de pestañas
        self.tabs = {
            "🖥️ Sistema": self.create_system_tab,
            "⚡ CPU": self.create_cpu_tab,
            "💾 Memoria": self.create_memory_tab,
            "💽 Discos": self.create_disk_tab,
            "🌐 Red": self.create_network_tab,
            "📋 Procesos": self.create_process_tab,
            "📖 Info": self.create_info_tab 
        }
        # Crear pestañas
        for tab_name, tab_method in self.tabs.items():
            frame = ttk.Frame(self.notebook)
            self.notebook.add(frame, text=tab_name)
            tab_method(frame)
    
    # Método para crear un frame con scroll
    def create_scrollable_frame(self, parent):
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)
        
        canvas = tk.Canvas(parent, highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        
        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        scroll_frame = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw", tags="scroll_frame")
        
        # Configurar para expansión automática del ancho
        scroll_frame.bind("<Configure>", lambda e: canvas.configure(
            scrollregion=canvas.bbox("all"),
            width=e.width  # Forzar ancho igual al canvas
        ))
        
        # Asegurar que el frame interno se expanda en altura si hay espacio
        canvas.bind("<Configure>", lambda e: canvas.itemconfigure(
            "scroll_frame", 
            width=e.width,
            height=max(e.height, scroll_frame.winfo_reqheight())
        ))
        
        canvas.configure(yscrollcommand=scrollbar.set)
        return scroll_frame
    
    # Método para crear pestaña de información del sistema
    def create_system_tab(self, parent):
        frame = self.create_scrollable_frame(parent)
        self.add_section(frame, "Información del Sistema Operativo", [
            ("Sistema", platform.system()),
            ("Versión", platform.version()),
            ("Edición", self.get_pc_manufacturer()),
            ("Arquitectura", f"{platform.machine()} ({platform.architecture()[0]})"),
            ("Hostname", socket.gethostname()),
            ("Usuario", os.getlogin()),
            ("Hora de inicio", datetime.fromtimestamp(psutil.boot_time()).strftime("%d-%m-%Y %H:%M:%S"))
        ])
        
        self.add_section(frame, "Hardware", [
            ("Fabricante", self.get_pc_manufacturer()),
            ("Modelo del equipo", self.get_pc_model()),
            ("Placa base", self.get_motherboard_info()),
            ("Memoria Total", self.format_size(psutil.virtual_memory().total)),
            ("Módulos RAM", self.get_ram_type()),
            ("GPU", self.get_gpu_info()),
            ("Batería", self.get_battery_status())
        ])
    
    # Método para crear pestaña de información del CPU
    def create_cpu_tab(self, parent):
        frame = self.create_scrollable_frame(parent)
        
        # Sección de información estática del CPU
        self.add_section(frame, "Información del Procesador", [
            ("Modelo", cpuinfo.get_cpu_info()['brand_raw']),
            ("Núcleos físicos", psutil.cpu_count(logical=False)),
            ("Núcleos lógicos", psutil.cpu_count(logical=True)),
            ("Frecuencia máxima", f"{psutil.cpu_freq().max:.2f} MHz"),
            ("Frecuencia actual", f"{psutil.cpu_freq().current:.2f} MHz"),
            ("Arquitectura", cpuinfo.get_cpu_info()['arch'])
        ])
        
        # Sección dinámica de estadísticas en tiempo real
        dynamic_frame = ttk.LabelFrame(frame, text="Estadísticas en Tiempo Real")
        dynamic_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5, ipadx=5, ipady=5)
        
        # Etiquetas dinámicas para actualizar la información
        self.cpu_usage_label = ttk.Label(dynamic_frame, text="Uso actual: Cargando...")
        self.cpu_usage_label.pack(anchor="w", padx=5, pady=2)
        
        self.cpu_cores_label = ttk.Label(dynamic_frame, text="Uso por núcleo: Cargando...")
        self.cpu_cores_label.pack(anchor="w", padx=5, pady=2)
        
        self.cpu_temperature_label = ttk.Label(dynamic_frame, text="Temperatura: Cargando...")
        self.cpu_temperature_label.pack(anchor="w", padx=5, pady=2)
        
        self.cpu_load_label = ttk.Label(dynamic_frame, text="Promedio de carga: Cargando...")
        self.cpu_load_label.pack(anchor="w", padx=5, pady=2)
        
        # Barra de progreso para el uso de CPU
        progress_frame = ttk.Frame(dynamic_frame)
        progress_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        ttk.Label(progress_frame, text="Uso de CPU:").pack(side=tk.LEFT, anchor="w")
        self.cpu_progress = ttk.Progressbar(
            progress_frame, 
            orient="horizontal",
            mode="determinate", 
            style="green.Horizontal.TProgressbar"
        )
        self.cpu_progress.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=5)
        
        # Iniciar la actualización en tiempo real
        self.update_cpu_info()

    # Método para obtener información de la placa base
    def get_motherboard_info(self):
        try:
            if platform.system() == "Windows":
                import wmi
                c = wmi.WMI()
                board = c.Win32_BaseBoard()[0]
                return f"{board.Manufacturer} {board.Product}" # Fabricante y modelo
            else:
                vendor = open("/sys/devices/virtual/dmi/id/board_vendor").read().strip()
                name = open("/sys/devices/virtual/dmi/id/board_name").read().strip()
                return f"{vendor} {name}"
        except Exception as e:
            return "No disponible"
        
    # Método para obtener información de los módulos de RAM
    def get_ram_type(self):
        try:
            if platform.system() == "Windows":
                import wmi
                c = wmi.WMI()
                rams = c.Win32_PhysicalMemory() # Lista de módulos de RAM
                return "\n".join([f"Módulo {i+1}: {ram.Capacity} bytes {ram.Speed}MHz" 
                                for i, ram in enumerate(rams)]) # Mostrar capacidad y velocidad de los módulos encontrados
            else:
                import subprocess
                result = subprocess.run(["dmidecode", "--type", "memory"], 
                                    capture_output=True, text=True)
                return result.stdout
        except:
            return "No disponible"

    # Método para obtener información de la GPU
    def get_gpu_info(self):
        try:
            if platform.system() == "Windows":
                import wmi
                c = wmi.WMI()
                gpu_info = []
                for gpu in c.Win32_VideoController():
                    gpu_info.append(gpu.Name.strip())
                return ", ".join(gpu_info)
            else:
                import subprocess
                result = subprocess.run(["lspci", "-nn"], capture_output=True, text=True)
                gpus = [line.split(': ')[-1] for line in result.stdout.split('\n') if 'VGA' in line]
                return ", ".join(gpus)
        except:
            return "No disponible"
    
    # Método para actualizar la información de CPU en tiempo real
    def update_cpu_info(self):
        # Actualizar uso actual de CPU
        current_usage = psutil.cpu_percent(interval=0.5)
        self.cpu_usage_label.config(text=f"Uso actual: {current_usage}%")
        
        # Actualizar uso por núcleo
        core_usages = psutil.cpu_percent(percpu=True)
        cores_text = ", ".join([f"{usage}%" for usage in core_usages])
        self.cpu_cores_label.config(text=f"Uso por núcleo: {cores_text}")
        
        # Actualizar temperatura (si está disponible)
        temp = self.get_cpu_temperature()
        self.cpu_temperature_label.config(text=f"Temperatura: {temp}")
        
        # Actualizar promedio de carga según el sistema
        if hasattr(psutil, "getloadavg"):
            load_avg = "/".join([f"{x:.2f}" for x in psutil.getloadavg()])
        else:
            load_avg = "No disponible en Windows"
        self.cpu_load_label.config(text=f"Promedio de carga: {load_avg}")
        
        # Actualizar la barra de progreso
        self.cpu_progress['value'] = current_usage
        
        # Programar la siguiente actualización en 1000 ms (1 segundo)
        self.root.after(1000, self.update_cpu_info)
    
    # Método para crear pestaña de información de memoria
    def create_memory_tab(self, parent):
        frame = self.create_scrollable_frame(parent)
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        self.add_section(frame, "Memoria Principal", [
            ("Total", self.format_size(mem.total)),
            ("Disponible", self.format_size(mem.available)),
            ("En uso", f"{self.format_size(mem.used)} ({mem.percent}%)")
        ])
        
        self.add_section(frame, "Memoria Swap", [
            ("Total", self.format_size(swap.total)),
            ("En uso", f"{self.format_size(swap.used)} ({swap.percent}%)"),
            ("Libre", self.format_size(swap.free))
        ])
        
        self.add_progress_bars(frame, [
            ("Uso de memoria", mem.percent),
            ("Uso de swap", swap.percent)
        ])
    
    # Método para crear pestaña de información de discos
    def create_disk_tab(self, parent):
        frame = self.create_scrollable_frame(parent)
        partitions = psutil.disk_partitions()
        
        for part in partitions:
            if part.fstype:
                usage = psutil.disk_usage(part.mountpoint)
                self.add_section(frame, f"Disco: {part.device}", [
                    ("Punto de montaje", part.mountpoint),
                    ("Tipo de sistema", part.fstype),
                    ("Espacio total", self.format_size(usage.total)),
                    ("En uso", f"{self.format_size(usage.used)} ({usage.percent}%)"),
                    ("Libre", self.format_size(usage.free))
                ])
                self.add_progress_bars(frame, [
                    (f"Uso de {part.device}", usage.percent)
                ])
                
        # Actividad del disco
        io = psutil.disk_io_counters()
        self.add_section(frame, "Actividad del Disco", [
            ("Lecturas", f"{io.read_count} operaciones"),
            ("Escrituras", f"{io.write_count} operaciones"),
            ("Datos leídos", self.format_size(io.read_bytes)),
            ("Datos escritos", self.format_size(io.write_bytes))
        ])
    
    # Método para crear pestaña de información de red
    def create_network_tab(self, parent):
        frame = self.create_scrollable_frame(parent)
        interfaces = psutil.net_if_addrs()
        stats = psutil.net_io_counters(pernic=True)
        
        for intf, addrs in interfaces.items():
            # Obtener dirección MAC según el sistema operativo
            if platform.system() == "Windows":
                mac = next((addr.address for addr in addrs if addr.family == psutil.AF_LINK), "N/A")
            else:
                mac = next((addr.address for addr in addrs if addr.family == socket.AF_PACKET), "N/A")
            
            self.add_section(frame, f"Interfaz: {intf}", [
                ("Dirección IP", next((addr.address for addr in addrs if addr.family == socket.AF_INET), "N/A")),
                ("MAC", mac),
                ("Bytes enviados", self.format_size(stats[intf].bytes_sent)),
                ("Bytes recibidos", self.format_size(stats[intf].bytes_recv)),
                ("Paquetes enviados", stats[intf].packets_sent),
                ("Paquetes recibidos", stats[intf].packets_recv)
            ])
    
    def create_process_tab(self, parent):
        frame = self.create_scrollable_frame(parent)
        
        # Contenedor superior para controles
        control_frame = ttk.Frame(frame)
        control_frame.pack(fill=tk.X, pady=5)
        
        # Botón de actualizar
        refresh_btn = ttk.Button(control_frame, text="Actualizar", command=self.update_process_list)
        refresh_btn.pack(side=tk.LEFT, padx=5)
        
        # Botón de terminar proceso
        self.kill_btn = ttk.Button(control_frame, text="Terminar proceso", state=tk.DISABLED, command=self.terminate_process)
        self.kill_btn.pack(side=tk.LEFT, padx=5)
        
        # Treeview para mostrar procesos
        self.process_tree = ttk.Treeview(frame, columns=('pid', 'name', 'status', 'cpu', 'memory', 'user'), show='headings')
        
        # Columnas de los procesos mostrados
        columns = {
            'pid': {'text': 'PID', 'width': 70, 'stretch': False},
            'name': {'text': 'Nombre', 'width': 150, 'stretch': True},  # Esta columna se expandirá
            'status': {'text': 'Estado', 'width': 100, 'stretch': False},
            'cpu': {'text': 'CPU%', 'width': 80, 'stretch': False},
            'memory': {'text': 'Memoria%', 'width': 90, 'stretch': False},
            'user': {'text': 'Usuario', 'width': 100, 'stretch': False}
        }
        
        for col, config in columns.items():
            self.process_tree.heading(col, text=config['text'])
            self.process_tree.column(
                col, 
                width=config['width'], 
                anchor=tk.CENTER,
                stretch=config['stretch']  # Habilita la expansión para columnas seleccionadas
            )
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.process_tree.yview)
        self.process_tree.configure(yscrollcommand=scrollbar.set)
        
        # Empaquetar
        self.process_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Configurar selección
        self.process_tree.bind('<<TreeviewSelect>>', self.on_process_select)
        
        # Menú contextual
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Terminar proceso", command=self.terminate_process)
        self.context_menu.add_command(label="Terminar por narices!!", command=self.kill_process)
        self.process_tree.bind("<Button-3>", self.show_context_menu)
        
        # Cargar datos iniciales
        self.update_process_list()

    # Método para actualizar el estado del botón de terminar proceso
    def on_process_select(self, event):
        selected = self.process_tree.selection()
        self.kill_btn['state'] = tk.NORMAL if selected else tk.DISABLED

    # Método para mostrar el menú contextual
    def show_context_menu(self, event):
        item = self.process_tree.identify_row(event.y)
        if item:
            self.process_tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def update_process_list(self):
        # Guardar selección actual
        selected = self.process_tree.selection()
        
        # Limpiar lista
        for item in self.process_tree.get_children():
            self.process_tree.delete(item)
        
        # Obtener y cargar procesos
        for proc in psutil.process_iter(['pid', 'name', 'status', 'cpu_percent', 'memory_percent', 'username']):
            try:
                self.process_tree.insert('', tk.END, values=(
                    proc.info['pid'],
                    proc.info['name'],
                    proc.info['status'],
                    f"{proc.info['cpu_percent']:.1f}",
                    f"{proc.info['memory_percent']:.1f}",
                    proc.info['username']
                ))
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        # Restaurar selección si sigue existiendo
        if selected and self.process_tree.exists(selected):
            self.process_tree.selection_set(selected)
        
        # Programar próxima actualización (5 segundos)
        self.root.after(5000, self.update_process_list)

    # Terminar proceso seleccionado
    def terminate_process(self):
        self._process_action('terminate')
    # Matar proceso seleccionado
    def kill_process(self):
        self._process_action('kill')

    def _process_action(self, action):
        selected = self.process_tree.selection()
        if not selected:
            return
        
        pid = int(self.process_tree.item(selected[0], 'values')[0])
        
        try:
            process = psutil.Process(pid)
            if action == 'terminate':
                process.terminate()
            elif action == 'kill':
                process.kill()
            
            # Actualizar lista después de 1 segundo
            self.root.after(1000, self.update_process_list)
            
        except Exception as e:
            tk.messagebox.showerror("Error", f"No se pudo {action} el proceso: {str(e)}")
    
    # Método para crear pestaña de información del programa
    def create_info_tab(self, parent):
        frame = self.create_scrollable_frame(parent)
        
        # Añadir una imagen
        from PIL import Image, ImageTk
        
        try:
            # Load the image
            image = Image.open("img/logo.png")
            
            # Resize the image
            image = image.resize((400, 400), Image.LANCZOS)  # LANCZOS para redimensionar
            self.image = ImageTk.PhotoImage(image)
            
            # Crear un label con la imagen
            label = ttk.Label(frame, image=self.image)
            label.image = self.image  # Mantener una referencia
            
            # Centrar un widget en el frame
            label.pack(pady=10, padx=10, anchor='center')
            
        except IOError:
            error_label = ttk.Label(frame, text="Error al cargar la image")
            error_label.pack(pady=10)

        # explicación básica del programa
        explanation = """
        Este programa muestra información detallada sobre el sistema, incluyendo detalles del CPU, memoria, discos y red. Es útil para monitorización y diagnóstico de hardware.
        """
        info_label = ttk.Label(frame, text=explanation, justify=tk.LEFT, wraplength=400)
        info_label.pack(pady=10)

        # Link del repositorio
        link_text = "Repositorio en GitHub"
        github_label = ttk.Label(frame, text=link_text, foreground="blue", cursor="hand2")
        github_label.pack(pady=5)
        github_label.bind("<Button-1>", lambda e: self.callback("https://github.com/sapoclay/analiza_tu_sistema"))

    def callback(self, url):
        # Abrir url en el navegador por defecto
        webbrowser.open(url, new=2)  # new=2 abre en una nueva pestaña si es posible
    
    # Método para añadir secciones de información
    def add_section(self, parent, title, items):
        frame = ttk.LabelFrame(parent, text=title)
        frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5, ipadx=5, ipady=5)
        
        for row, (text, value) in enumerate(items):
            frame.grid_rowconfigure(row, weight=1)
            frame.grid_columnconfigure(1, weight=1)  # Hacer que la segunda columna se expanda
            
            ttk.Label(frame, text=text, anchor="w").grid(
                row=row, column=0, sticky="nsew", padx=5, pady=2)
            ttk.Label(frame, text=value, anchor="w").grid(
                row=row, column=1, sticky="nsew", padx=5, pady=2)
        
        # Añadir fila de expansión al final
        frame.grid_rowconfigure(len(items), weight=1)
    
    # Método para añadir barras de progreso
    def add_progress_bars(self, parent, items):
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)  # Cambiado a BOTH
        
        for text, value in items:
            container = ttk.Frame(frame)
            container.pack(fill=tk.BOTH, expand=True, pady=2)
            
            ttk.Label(container, text=text).pack(side=tk.LEFT, anchor="w")
            progress = ttk.Progressbar(
                container, 
                length=200, 
                mode="determinate", 
                style="green.Horizontal.TProgressbar"
            )
            progress.pack(side=tk.RIGHT, fill=tk.X, expand=True)  # Ajustado para expansión
            progress['value'] = value
    
    # Método para formatear tamaños de bytes
    def format_size(self, bytes):
        return f"{bytes / (1024**3):.2f} GB"
    
    # Métodos para obtener información del sistema
    def get_cpu_temperature(self):
        try:
            temps = psutil.sensors_temperatures()
            if 'coretemp' in temps:
                return f"{temps['coretemp'][0].current}°C"
            return "N/A"
        except: return "No se ha podido obtener la temperatura"
    
    # Métodos para obtener información del sistema
    def get_pc_manufacturer(self):
        try:
            if platform.system() == "Windows":
                return platform.win32_edition()
            return open("/sys/devices/virtual/dmi/id/sys_vendor").read().strip()
        except: return "No se ha podido obtener la información del sistema"
    
    # Método para obtener el modelo de la PC
    def get_pc_model(self):
        try:
            if platform.system() == "Windows":
                return platform.win32_ver()[1]
            return open("/sys/devices/virtual/dmi/id/product_name").read().strip()
        except: return "No se ha podido obtener el modelo"
    
    # Método para obtener el estado de la batería
    def get_battery_status(self):
        try:
            battery = psutil.sensors_battery()
            return f"{battery.percent}% ({'Cargando' if battery.power_plugged else 'Batería'})"
        except: return "No hay una batería conectada!!"
    
    # Método para obtener información del sistema
    def get_system_info(self):
        pass
    


if __name__ == "__main__":
    root = tk.Tk()
    app = SystemInfoApp(root)
    root.mainloop()