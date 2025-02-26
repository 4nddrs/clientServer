import firebase_admin
from firebase_admin import credentials, firestore
import psutil
import socket
import time
import sys
from datetime import datetime
from colorama import init, Fore

# Inicializar colorama
init(autoreset=True)

# Verificar que se pasó el nombre como argumento
if len(sys.argv) != 2:
    print(Fore.RED + "¡Error! Debes pasar un nombre como argumento.")
    sys.exit(1)

nombre = sys.argv[1]

# Inicializar Firebase
cred = credentials.Certificate("clientserver-88fff-firebase-adminsdk-fbsvc-cd72f77cbd.json")
 # Reemplaza con tu JSON de Firebase
firebase_admin.initialize_app(cred)
db = firestore.client()

# Función para obtener datos del sistema
def obtener_datos():
    name = socket.gethostname()
    ip = socket.gethostbyname(socket.gethostname())
    
    # Obtener la dirección MAC del adaptador Wi-Fi
    mac = None
    for interface, addrs in psutil.net_if_addrs().items():
        if "Wi-Fi" in interface or "wlan" in interface.lower():  # Filtrar por nombre de la interfaz Wi-Fi
            for addr in addrs:
                if addr.family == psutil.AF_LINK:
                    mac = addr.address
                    break
        if mac:
            break
    
    if not mac:
        print(Fore.RED + "No se pudo obtener la dirección MAC de Wi-Fi.")
        sys.exit(1)

    memory = round(psutil.virtual_memory().total / (1024 ** 3), 2)  # En GB
    state = "activo"  # Puedes modificar esta lógica según tu criterio

    # Obtener información de los discos (espacio total y utilizado)
    discos = {}
    for i, disk in enumerate(psutil.disk_partitions(), start=1):
        try:
            usage = psutil.disk_usage(disk.mountpoint)
            # Subir el espacio total a 'client' (total del disco)
            discos[str(i)] = round(usage.total / (1024 ** 3), 2)  # Espacio total en GB (para 'client')
        except PermissionError:
            continue

    return {
        "name": name,
        "ip": ip,
        "mac": mac,
        "memory": memory,
        "state": state,
        "disks": discos
    }

# Subir datos iniciales del cliente si no existe
datos_cliente = obtener_datos()
cliente_ref = db.collection("client").document(datos_cliente["mac"])

# Verificar si la MAC ya existe en la colección 'client'
if cliente_ref.get().exists:
    print(Fore.YELLOW + "La MAC ya está registrada, solo se agregarán logs.")
else:
    cliente_ref.set(datos_cliente)
    print(Fore.GREEN + "Información del cliente subida a Firebase.")

# Subir registros cada 30 segundos a 'log'
# Subir registros cada 30 segundos a 'log'
while True:
    datos = obtener_datos()
    logs = {"idClient": datos["mac"], "date": datetime.utcnow()}
    
    # Crear el diccionario de discos con el espacio utilizado
    logs["disks"] = {}
    for i, disk in enumerate(psutil.disk_partitions(), start=1):
        try:
            usage = psutil.disk_usage(disk.mountpoint)
            # Subir el espacio utilizado a 'log' (espacio ocupado por archivos)
            logs["disks"][str(i)] = round(usage.used / (1024 ** 3), 2)  # Espacio utilizado en GB (para 'log')
        except PermissionError:
            continue
    
    # Obtener la memoria utilizada
    memory_used = round(psutil.virtual_memory().used / (1024 ** 3), 2)  # Memoria utilizada en GB
    
    # Agregar la memoria utilizada a los logs
    logs["memory_used"] = memory_used

    db.collection("log").add(logs)
    print(Fore.CYAN + f"Registro en 'log' subido a Firebase. Memoria utilizada: {memory_used} GB")
    
    time.sleep(30)  # Esperar 30 segundos

