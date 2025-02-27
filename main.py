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
        self.label = ctk.CTkLabel(self.main_frame, text="Clientes en Firebase", font=("Times New Roman", 30), text_color="white")
        self.label.pack(pady=10)



        # 🔹 Información total de los discos (Total, Usado, Libre, Reportados)
        self.total_disks = 0
        self.used_disks = 0
        self.free_disks = 0
        self.reportados = 0
        self.total_clients = 0

        # 🔹 Mostrar el total, usado, libre y reportados debajo del título
        # Crear un contenedor para la fila de los tres primeros labels
        row_frame = ctk.CTkFrame(self.main_frame)
        row_frame.pack(pady=10, anchor='w', padx=(30, 0))  # Usamos 'anchor="w"' para alinearlo a la izquierda y eliminamos el padding derecho

        # Colocar los labels en la fila, usando side='left' para alinearlos horizontalmente
        self.total_label = ctk.CTkLabel(row_frame, text=f"{self.total_disks:.2f}", font=("Arial", 14), text_color="white", anchor='w')
        self.total_label.pack(side='left', padx=10)

        self.used_label = ctk.CTkLabel(row_frame, text=f"{self.used_disks:.2f}", font=("Arial", 14), text_color="white", anchor='w')
        self.used_label.pack(side='left', padx=10)

        self.free_label = ctk.CTkLabel(row_frame, text=f"{self.free_disks:.2f}", font=("Arial", 14), text_color="white", anchor='w')
        self.free_label.pack(side='left', padx=10)


        # Crear un contenedor para el label "reportado"
        report_frame = ctk.CTkFrame(self.main_frame)
        report_frame.pack(pady=5, anchor='w', padx=(30, 0))

        # Colocar el label "reportado" dentro del contenedor
        self.report_label = ctk.CTkLabel(report_frame, text=f"Reportaron {self.reportados} de {self.total_clients}", font=("Arial", 14), text_color="white", anchor='w')
        self.report_label.pack(pady=5, padx=15)




        # Agregar el logo a la parte superior derecha
        # Cargar la imagen del logo
        logo_image = Image.open("assets/Logo.png")  # Cambia la ruta por la de tu logo
        logo_image = logo_image.resize((200, 200))  # Redimensiona la imagen si es necesario
        logo = ImageTk.PhotoImage(logo_image)

        # Crear un Label para mostrar el logo
        self.logo_label = ctk.CTkLabel(self.main_frame, image=logo)
        self.logo_label.image = logo  # Necesario para mantener la referencia a la imagen
        self.logo_label.place(x=1090, y=20) 

        


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
        clientes_activos = 0  # Variable para contar los clientes activos
        total_clientes = 0  # Variable para contar el total de clientes

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
            
            # Sumar al total general y redondear a 2 decimales
            self.total_disks += total_storage
            self.used_disks += used_storage
            self.free_disks += free_storage

            # Redondear a 2 decimales
            self.total_disks = round(self.total_disks, 2)
            self.used_disks = round(self.used_disks, 2)
            self.free_disks = round(self.free_disks, 2)


            # Contamos el cliente activo
            total_clientes += 1
            if estado.lower() == "activo":
                clientes_activos += 1

            # 🔹 Si el cliente está inactivo y no tiene logs, mostrar solo "No reporta"
            if estado == "inactivo" :
                # 🔹 Crear tarjeta para cada cliente con información completa
                frame_cliente = ctk.CTkFrame(self.client_frame, height=300, width=250, corner_radius=15, fg_color="#061c31")
                frame_cliente.grid(row=fila, column=columna, padx=10, pady=10)

                # 🔹 Cargar la imagen (asegúrate de que la ruta sea correcta)
                image_path = "assets/Dic-Inactivo.png"
                image = Image.open(image_path)

                # 🔹 Redimensionar la imagen a un tamaño más pequeño, por ejemplo, 150x150 píxeles
                image_resized = image.resize((160, 160))  # Cambia el tamaño a lo que desees

                # 🔹 Convertir la imagen redimensionada a un formato compatible con tkinter
                image_tk = ImageTk.PhotoImage(image_resized)

                # 🔹 Crear una etiqueta con la imagen encima del nombre
                image_label = ctk.CTkLabel(frame_cliente, image=image_tk)
                image_label.image = image_tk  # Guardamos la referencia de la imagen
                image_label.pack(side="top", pady=6)

                # 🔹 Nombre del cliente
                label = ctk.CTkLabel(frame_cliente, text=name, font=("Arial", 18, "bold"), text_color="red")
                label.pack(side="top", pady=6)

                # 🔹 Mensaje "NO REPORTA" en rojo (antes de la info de almacenamiento)
                label_no_reporta = ctk.CTkLabel(frame_cliente, text="NO REPORTA", font=("Arial", 16, "bold"), text_color="red")
                label_no_reporta.pack(side="top", pady=(10, 90))  # Espaciado arriba y abajo

                # 🔹 Barra de progreso con cambio de color dinámico (invisible pero visible y en gris)
                progress = ctk.CTkProgressBar(frame_cliente, width=180)
                usage_ratio = used_storage / total_storage if total_storage > 0 else 0
                progress.set(usage_ratio)
                progress.configure(progress_color="gray")  # Color gris
                progress.set(0)  # O puedes ajustarlo al valor que desees, por ejemplo, `0`
                progress.pack(side="top", padx=10, pady=10)

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
            if columna > 4:
                columna = 0
                fila += 1
        
        
        # Actualizar los valores de los labels después de obtener los datos
        self.total_label.configure(text=f"Total: {self.total_disks} TB", text_color="#d5b0e8", font=("Helvetica", 12, "bold"))
        self.used_label.configure(text=f"Usado: {self.used_disks} GB", text_color="#d5b0e8", font=("Helvetica", 12, "bold"))
        self.free_label.configure(text=f"Libre: {self.free_disks} GB", text_color="#d5b0e8", font=("Helvetica", 12, "bold"))
        self.report_label.configure(text=f"Reportaron {clientes_activos} de {total_clientes}", text_color="#d5b0e8", font=("Helvetica", 12, "bold"))

        
        # Calcula el porcentaje de uso total
        used_percentage = self.used_disks / self.total_disks
        # Determina el color de la barra de progreso basado en el porcentaje de uso
        if used_percentage <= 0.5:
            progress_color = "#00FF00"  
        elif used_percentage <= 0.75:
            progress_color = "#FFFF00"  
        elif used_percentage <= 0.9:
            progress_color = "#FFA500"  
        else:
            progress_color = "#FF0000"  
        # Crear barra de progreso para mostrar el uso total de todos los discos
        self.used_progress = ctk.CTkProgressBar(self.main_frame, width=400, height=20, progress_color=progress_color)
        self.used_progress.set(used_percentage)  # Establecer el valor del progreso como el porcentaje de uso
        self.used_progress.pack(pady=5)


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