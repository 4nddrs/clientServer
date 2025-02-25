import firebase_admin
from firebase_admin import credentials, firestore
import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# 🔹 Inicializar Firebase
cred = credentials.Certificate("key.json")  # Reemplaza con tu JSON de Firebase
firebase_admin.initialize_app(cred)
db = firestore.client()

# 🔹 Configuración de la interfaz gráfica
ctk.set_appearance_mode("dark")  # Modo oscuro
ctk.set_default_color_theme("blue")  # Tema azul

class FirebaseApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Servidor - Clientes en Firebase")
        self.geometry("700x500")

        # 🔹 Título
        self.label = ctk.CTkLabel(self, text="Clientes en Firebase", font=("Arial", 20))
        self.label.pack(pady=10)

        # 🔹 Contenedor de clientes
        self.frame = ctk.CTkFrame(self)
        self.frame.pack(fill="both", expand=True, padx=20, pady=10)

        # 🔹 Cargar clientes
        self.obtener_datos()

    def obtener_datos(self):
        """Carga los clientes desde Firebase y los muestra en la interfaz."""
        for widget in self.frame.winfo_children():
            widget.destroy()

        clientes_ref = db.collection("client").stream()

        for cliente in clientes_ref:
            data = cliente.to_dict()
            name = data.get("name", "Desconocido")
            mac = data.get("mac", "Desconocido")
            total_storage = sum(data.get("disks", {}).values())
            used_storage = self.obtener_uso_cliente(mac)

            # 🔹 Crear barra de progreso
            frame_cliente = ctk.CTkFrame(self.frame)
            frame_cliente.pack(fill="x", padx=10, pady=5)

            label = ctk.CTkLabel(frame_cliente, text=name, font=("Arial", 14))
            label.pack(side="left", padx=10)

            progress = ctk.CTkProgressBar(frame_cliente, width=300)
            progress.set(used_storage / total_storage if total_storage > 0 else 0)
            progress.pack(side="left", padx=10, pady=5)

            # Mostrar el espacio total y usado en la barra de progreso
            label_total = ctk.CTkLabel(frame_cliente, text=f"{used_storage}/{total_storage} GB", font=("Arial", 12))
            label_total.pack(side="right", padx=10)

            btn = ctk.CTkButton(frame_cliente, text="Ver detalles", 
                                command=lambda mac=mac: self.mostrar_detalles(mac))
            btn.pack(side="right", padx=10)

    def obtener_uso_cliente(self, mac):
        """Obtiene el último uso de almacenamiento registrado para el cliente."""
        logs = db.collection("log").where("idClient", "==", mac).order_by("date", direction=firestore.Query.DESCENDING).limit(1).stream()
        
        for log in logs:
            return sum(log.to_dict().get("disks", {}).values())  # Total del espacio utilizado de todos los discos
        return 0

    def mostrar_detalles(self, mac):
        """Muestra una nueva ventana con los detalles del cliente seleccionado."""
        cliente_doc = db.collection("client").document(mac).get()
        if not cliente_doc.exists:
            print("Cliente no encontrado")
            return
        
        cliente = cliente_doc.to_dict()
        logs = db.collection("log").where("idClient", "==", mac) \
            .order_by("date", direction=firestore.Query.ASCENDING).stream()
        
        used_storage = []
        dates = []
        for log in logs:
            log_data = log.to_dict()
            used_storage.append(sum(log_data.get("disks", {}).values()))  # Sumar el espacio usado de todos los discos
            dates.append(log_data.get("date", "Desconocido"))

        # 🔹 Crear nueva ventana para detalles
        detalles = ctk.CTkToplevel(self)
        detalles.title(f"Detalles de {cliente['name']}")
        detalles.geometry("800x600")

        # 🔹 Barra de progreso de almacenamiento usado (con espacio total y usado)
        total_storage = sum(cliente.get("disks", {}).values())
        last_used_storage = used_storage[-1] if used_storage else 0

        progress = ctk.CTkProgressBar(detalles, width=600)
        progress.set(last_used_storage / total_storage if total_storage > 0 else 0)
        progress.pack(pady=10)

        # Mostrar espacio total y usado en la barra de progreso
        label_total = ctk.CTkLabel(detalles, text=f"{last_used_storage}/{total_storage} GB", font=("Arial", 12))
        label_total.pack(pady=5)

        # 🔹 Gráfico de histograma (Historial de uso de almacenamiento)
       # 🔹 Gráfico de histograma (Historial de uso de almacenamiento)
        fig, ax = plt.subplots(figsize=(5, 3))

        # Crear el histograma con barras para mostrar el espacio usado
        ax.bar(dates, used_storage, color="skyblue", label="Espacio usado")

        # Añadir una línea representando el espacio usado total
        ax.plot(dates, [last_used_storage] * len(dates), color="red", label="Línea de espacio ocupado", linestyle="--", linewidth=2)

        # Definir el tamaño total del disco (1TB = 1000GB)
        disk_size = total_storage  # En GB

        # Ajustar dinámicamente el límite superior del eje Y
        ax.set_ylim(0, disk_size)  # Ajusta el eje Y de 0 hasta 1000 GB

        # Configuración de la gráfica
        ax.set_title("Historial de almacenamiento usado")
        ax.set_xlabel("Fecha")
        ax.set_ylabel("Almacenamiento (GB)")
        ax.tick_params(axis='x', rotation=45)  # Rotar las fechas para mejor visualización
        ax.legend()

        # Mostrar el gráfico
        canvas = FigureCanvasTkAgg(fig, master=detalles)
        canvas.get_tk_widget().pack(pady=10)
        canvas.draw()


        # 🔹 Gráfico de torta (Distribución de almacenamiento con espacio total y ocupado)
        fig2, ax2 = plt.subplots(figsize=(4, 3))
        labels = [f"Disco {k}" for k in cliente.get("disks", {}).keys()]
        sizes = list(cliente.get("disks", {}).values())
        occupied_size = last_used_storage
        remaining_size = total_storage - occupied_size

        ax2.pie([occupied_size, remaining_size], labels=["Ocupado", "Libre"], autopct="%1.1f%%", colors=["#ff9999", "#66b3ff"])
        ax2.set_title("Distribución de almacenamiento (Último log)")

        canvas2 = FigureCanvasTkAgg(fig2, master=detalles)
        canvas2.get_tk_widget().pack(pady=10)
        canvas2.draw()

# 🔹 Iniciar la aplicación
if __name__ == "__main__":
    app = FirebaseApp()
    app.mainloop()

