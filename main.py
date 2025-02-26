import firebase_admin
from firebase_admin import credentials, firestore
import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import PhotoImage
from PIL import Image, ImageTk  

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
        self.geometry("950x500")

        # 🔹 Crear un canvas para el degradado
        self.canvas = tk.Canvas(self, width=700, height=500)
        self.canvas.pack(fill="both", expand=True)
        self.draw_gradient()

        # 🔹 Color de fondo sólido
        self.canvas.config(bg="#061c31")

        # 🔹 Frame principal con fondo transparente
        self.main_frame = ctk.CTkFrame(self, fg_color="#061c31")
        self.main_frame.place(relwidth=1, relheight=1)

        # 🔹 Título
        self.label = ctk.CTkLabel(self.main_frame, text="Clientes en Firebase", font=("Arial", 20), text_color="white")
        self.label.pack(pady=10)

        # 🔹 Contenedor de clientes con scroll
        self.scrollable_frame = ctk.CTkFrame(self.main_frame, fg_color="#133c5c")
        self.scrollable_frame.pack(fill="both", expand=True, padx=20, pady=25)

        # 🔹 Crear un Canvas para el Scroll
        self.scroll_canvas = tk.Canvas(self.scrollable_frame, bg="#133c5c")
        self.scroll_canvas.pack(side="left", fill="both", expand=True)

        # 🔹 Barra de desplazamiento (scrollbar)
        self.scrollbar = tk.Scrollbar(self.scrollable_frame, orient="vertical", command=self.scroll_canvas.yview)
        self.scrollbar.pack(side="right", fill="y")

        self.scroll_canvas.configure(yscrollcommand=self.scrollbar.set)

        # 🔹 Crear un marco dentro del Canvas para contener los widgets de los clientes
        self.client_frame = tk.Frame(self.scroll_canvas, bg="#133c5c")
        self.scroll_canvas.create_window((0, 0), window=self.client_frame, anchor="nw")

        # 🔹 Cargar clientes
        self.obtener_datos()

    def obtener_datos(self):
        for widget in self.client_frame.winfo_children():
            widget.destroy()

        clientes_ref = db.collection("client").stream()

        fila, columna = 0, 0  # Control de posiciones

        for cliente in clientes_ref:
            data = cliente.to_dict()
            name = data.get("name", "Desconocido")
            mac = data.get("mac", "Desconocido")
            estado = data.get("state", "Activo")  # Asumimos que tienes un campo de estado
            total_storage = sum(data.get("disks", {}).values())  # Total de almacenamiento
            used_storage = self.obtener_uso_cliente(mac)  # Almacenamiento usado
            free_storage = total_storage - used_storage  # Almacenamiento libre

            # Redondear los valores a dos decimales
            total_storage = round(total_storage, 2)
            used_storage = round(used_storage, 2)
            free_storage = round(free_storage, 2)

            # 🔹 Si el cliente está inactivo y no tiene logs, mostrar solo "No reporta"
            if estado == "inactivo" : #and used_storage == 0
                # Crear una tarjeta simple con mensaje "No reporta"
                frame_cliente = ctk.CTkFrame(self.client_frame, height=150, width=250, corner_radius=15, fg_color="#061c31")
                frame_cliente.grid(row=fila, column=columna, padx=10, pady=10)

                # Texto de "No reporta" con nombre en rojo
                label_no_reporta = ctk.CTkLabel(frame_cliente, text="No reporta", font=("Arial", 16, "bold"), text_color="red")
                label_no_reporta.pack(side="top", pady=6)

                label_name = ctk.CTkLabel(frame_cliente, text=name, font=("Arial", 14, "bold"), text_color="red")
                label_name.pack(side="top", pady=6)
            else:
                # 🔹 Crear tarjeta para cada cliente con información completa
                frame_cliente = ctk.CTkFrame(self.client_frame, height=300, width=250, corner_radius=15, fg_color="#061c31")
                frame_cliente.grid(row=fila, column=columna, padx=10, pady=10)

                # 🔹 Cargar la imagen (asegúrate de que la ruta sea correcta)
                image_path = "assets/Disco.png"
                image = Image.open(image_path)

                # 🔹 Redimensionar la imagen a un tamaño más pequeño, por ejemplo, 150x150 píxeles
                image_resized = image.resize((150, 150))  # Cambia el tamaño a lo que desees

                # 🔹 Convertir la imagen redimensionada a un formato compatible con tkinter
                image_tk = ImageTk.PhotoImage(image_resized)

                # 🔹 Crear una etiqueta con la imagen encima del nombre
                image_label = ctk.CTkLabel(frame_cliente, image=image_tk)
                image_label.image = image_tk  # Guardamos la referencia de la imagen
                image_label.pack(side="top", pady=6)

                # 🔹 Nombre del cliente
                label = ctk.CTkLabel(frame_cliente, text=name, font=("Arial", 16, "bold"), text_color="white")
                label.pack(side="top", pady=6)

                # 🔹 Información del almacenamiento en filas
                label_total = ctk.CTkLabel(frame_cliente, text=f"{total_storage} GB", font=("Arial", 10), text_color="white")
                label_total.pack(side="top", pady=0)  # Sin espacio entre filas

                label_used = ctk.CTkLabel(frame_cliente, text=f"{used_storage} GB USO", font=("Arial", 10), text_color="white")
                label_used.pack(side="top", pady=0)  # Sin espacio entre filas

                label_free = ctk.CTkLabel(frame_cliente, text=f"{free_storage} GB LIBRE", font=("Arial", 10), text_color="white")
                label_free.pack(side="top", pady=(0, 0))  # Sin espacio entre filas, o el mínimo

                # 🔹 Barra de progreso con cambio de color dinámico
                progress = ctk.CTkProgressBar(frame_cliente, width=180)
                usage_ratio = used_storage / total_storage if total_storage > 0 else 0
                progress.set(usage_ratio)
                progress.configure(progress_color=self.get_progress_color(usage_ratio))
                progress.pack(side="top", padx=10, pady=10)

                # 🔹 Cargar la imagen de la flecha (asegúrate de que la ruta sea correcta)
                arrow_image = Image.open("assets/flecha.png")
                arrow_image_resized = arrow_image.resize((30, 30))  # Ajusta el tamaño de la flecha
                arrow_image_tk = ImageTk.PhotoImage(arrow_image_resized)

                # 🔹 Botón de ver detalles con imagen de flecha y color personalizado
                btn = ctk.CTkButton(frame_cliente, 
                                    text="Ver detalles", 
                                    command=lambda mac=mac: self.mostrar_detalles(mac), 
                                    image=arrow_image_tk, 
                                    compound="right",
                                    fg_color="#FF9A00",  # Color de fondo del botón
                                    hover_color="#FFB84D"  # Color al pasar el ratón
                                )
                btn.pack(side="bottom", pady=10)

            # Control de posición
            columna += 1
            if columna > 3:
                columna = 0
                fila += 1

        # Actualizar el tamaño del canvas cuando se agregan widgets
        self.client_frame.update_idletasks()
        self.scroll_canvas.config(scrollregion=self.scroll_canvas.bbox("all"))

    def obtener_uso_cliente(self, mac):
        """Obtiene el último uso de almacenamiento registrado para el cliente."""
        logs = db.collection("log").where("idClient", "==", mac).order_by("date", direction=firestore.Query.DESCENDING).limit(1).stream()
        
        for log in logs:
            return sum(log.to_dict().get("disks", {}).values())  
        return 0

    def mostrar_detalles(self, mac):
        """Muestra una nueva ventana con los detalles del cliente seleccionado."""
        cliente_doc = db.collection("client").document(mac).get()
        if not cliente_doc.exists:
            print("Cliente no encontrado")
            return

        cliente = cliente_doc.to_dict()
        logs = db.collection("log").where("idClient", "==", mac).order_by("date", direction=firestore.Query.ASCENDING).stream()
        
        used_storage, dates = [], []
        for log in logs:
            log_data = log.to_dict()
            used_storage.append(sum(log_data.get("disks", {}).values()))
            dates.append(log_data.get("date", "Desconocido"))

        detalles = ctk.CTkToplevel(self)
        detalles.title(f"Detalles de {cliente['name']}")
        detalles.geometry("990x540")  # Ajustamos el tamaño de la ventana secundaria

        # Cambiamos solo el color de fondo de la ventana secundaria
        detalles.configure(bg="#133c5c")

        # Hacer que la ventana secundaria esté encima de la ventana principal
        detalles.grab_set()  
        detalles.lift()  
        detalles.focus_force() 

        total_storage = sum(cliente.get("disks", {}).values())
        last_used_storage = used_storage[-1] if used_storage else 0

        # Crear un frame scrollable para contener las cards
        scrollable_frame = ctk.CTkScrollableFrame(detalles, width=950, height=500 , fg_color="#133c5c")
        scrollable_frame.grid(row=0, column=0, padx=10, pady=10)

        # Organizar el contenido en filas de 3 gráficos cada una
        row = 0  # Contador de filas
        column = 0  # Contador de columnas
        
        # 🔹 1: ----Card para el gráfico de torta
        card_pie_chart = ctk.CTkFrame(scrollable_frame, width=305, height=250, corner_radius=10, fg_color="#061c31")  # Card de tamaño ajustado
        card_pie_chart.grid(row=row, column=column+1, padx=5, pady=10)

        # 🔹 Gráfico de torta (Distribución de almacenamiento con espacio total y ocupado)
        fig2, ax2 = plt.subplots(figsize=(4, 3))  # Ajusta el tamaño del gráfico aquí
        labels = [f"Disco {k}" for k in cliente.get("disks", {}).keys()]
        sizes = list(cliente.get("disks", {}).values())
        occupied_size = last_used_storage
        remaining_size = total_storage - occupied_size

        ax2.pie([occupied_size, remaining_size], labels=["Ocupado", "Libre"], autopct="%1.1f%%", colors=["#ff9999", "#66b3ff"])
        ax2.set_title("Distribución de almacenamiento (Último log)")

        # Crear un canvas de matplotlib y agregarlo al frame de tkinter, sin cambiar el tamaño de la card
        canvas2 = FigureCanvasTkAgg(fig2, master=card_pie_chart)
        canvas2.get_tk_widget().place(relx=0.5, rely=0.5, anchor="center")  # Centra el gráfico en el widget de la card
        canvas2.draw()

        # 🔹 2: --Card para el gráfico de histograma
        card_histogram = ctk.CTkFrame(scrollable_frame, width=305, height=250, corner_radius=10 , fg_color="#061c31")  # Card de tamaño ajustado
        card_histogram.grid(row=row, column=column, padx=5, pady=10)

        

        # 🔹 3: --Card para el gráfico de progreso
        card_progress = ctk.CTkFrame(scrollable_frame, width=305, height=250, corner_radius=10, fg_color="#061c31")
        card_progress.grid(row=row, column=column+2, padx=5, pady=10)

        # Barra de progreso
        progress = ctk.CTkProgressBar(card_progress, width=200)
        usage_ratio = last_used_storage / total_storage if total_storage > 0 else 0
        progress.set(usage_ratio)
        progress.configure(progress_color=self.get_progress_color(usage_ratio))  # Cambiar color dinámicamente
        progress.place(relx=0.5, rely=0.4, anchor="center")  # Usamos place para no alterar el tamaño de la card

        # Mostrar el porcentaje de uso del disco
        usage_percentage = round(usage_ratio * 100, 1)  # Convertir a porcentaje
        percentage_label = ctk.CTkLabel(card_progress, text=f"{usage_percentage}% usado", fg_color=None, font=("Arial", 14))
        percentage_label.place(relx=0.5, rely=0.7, anchor="center")  # Posicionamos el label sin afectar el tamaño de la card


        # --- Incrementar la fila después de agregar 3 cards
        column = 0
        row += 1


        # 🔹 Card para el gráfico de tiempo
        card_time_graph = ctk.CTkFrame(scrollable_frame, width=305, height=250, corner_radius=10 , fg_color="#061c31")  # Card de tamaño ajustado
        card_time_graph.grid(row=row, column=column, padx=5, pady=10)

        # 🔹 Card para otra gráfica (si es necesario, puedes añadir más)
        card_another = ctk.CTkFrame(scrollable_frame, width=305, height=250, corner_radius=10 , fg_color="#061c31")  # Card de tamaño ajustado
        card_another.grid(row=row, column=column+1, padx=5, pady=10)

        # 🔹 Card para otro gráfico más (si es necesario)
        card_more = ctk.CTkFrame(scrollable_frame, width=305, height=250, corner_radius=10 , fg_color="#061c31")  # Card de tamaño ajustado
        card_more.grid(row=row, column=column+2, padx=5, pady=10)



    def draw_gradient(self):
        """Dibuja un degradado en el fondo."""
        self.canvas.create_rectangle(0, 0, 700, 500, outline="", fill="black")

    def get_progress_color(self, usage_ratio):
        """Devuelve el color de la barra de progreso según el uso del almacenamiento."""
        if usage_ratio < 0.5:
            return "#66ff66"  # Verde
        elif usage_ratio < 0.8:
            return "#ffcc00"  # Amarillo
        else:
            return "#ff6666"  # Rojo


if __name__ == "__main__":
    app = FirebaseApp()
    app.mainloop()