import tkinter as tk
import requests
import threading

app = tk.Tk()
app.geometry("700x450")
app.resizable(False, False)
app.title("Semáforo Inteligente")

# Variables para LEDs
estado_verde = tk.IntVar()
estado_amarillo = tk.IntVar()
estado_rojo = tk.IntVar()

# Variables para rutina
estado_iniciar = tk.IntVar()
estado_parar = tk.IntVar()
global ciclo_activo
ciclo_activo = False

esp32_ip = "172.26.166.223"

# --- Función para controlar las luces del semáforo (Canvas) ---
def set_light(active):
    """Enciende en el canvas la luz indicada y apaga las demás"""
    canvas.itemconfig(roja, fill="red" if active == "red" else "gray")
    canvas.itemconfig(amarilla, fill="yellow" if active == "yellow" else "gray")
    canvas.itemconfig(verde, fill="green" if active == "green" else "gray")

# --- Funcion para realizar peticiones sin delay ---
def request_thread(url):
    def tarea():
        try:
            requests.get(url, timeout=1.2)
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
    threading.Thread(target=tarea).start()

# ---------------- Rutina en la Interfaz ----------------
def rutina_semaforo():
    if not ciclo_activo:
        return  

    # Leer valores de los scale en milisegundos
    t_verde = scale_tiempo_verde.get() * 1000
    t_amarillo = scale_tiempo_amarillo.get() * 1000
    t_rojo = scale_tiempo_rojo.get() * 1000

    # Paso 1: Verde encendido
    set_light("green")
    request_thread(f"http://{esp32_ip}/led/verde/on")
    request_thread(f"http://{esp32_ip}/led/amarillo/off")
    request_thread(f"http://{esp32_ip}/led/rojo/off")

    # Después de t_verde ms, iniciar parpadeo
    app.after(t_verde, lambda: parpadear_verde(3, 700, t_amarillo, t_rojo))


def parpadear_verde(veces, intervalo, t_amarillo, t_rojo):
    def toggle(count):
        if count == 0:
            # Al terminar el parpadeo, continuar con amarillo
            paso_amarillo(t_amarillo, t_rojo)
            return

        current = canvas.itemcget(verde, "fill")
        if current == "green":
            canvas.itemconfig(verde, fill="gray")
            request_thread(f"http://{esp32_ip}/led/verde/off")
        else:
            canvas.itemconfig(verde, fill="green")
            request_thread(f"http://{esp32_ip}/led/verde/on")

        # Repetir después de 'intervalo' ms
        app.after(intervalo, toggle, count - 1)

    toggle(veces * 2)  # 2 cambios = 1 parpadeo

def paso_amarillo(t_amarillo, t_rojo):
    if not ciclo_activo:
        return

    # Paso 2: Amarillo
    set_light("yellow")
    request_thread(f"http://{esp32_ip}/led/verde/off")
    request_thread(f"http://{esp32_ip}/led/amarillo/on")
    request_thread(f"http://{esp32_ip}/led/rojo/off")

    # Programar Rojo después de t_amarillo
    app.after(t_amarillo, paso_rojo, t_rojo)


def paso_rojo(t_rojo):
    if not ciclo_activo:
        return

    # Paso 3: Rojo
    set_light("red")
    request_thread(f"http://{esp32_ip}/led/verde/off")
    request_thread(f"http://{esp32_ip}/led/amarillo/off")
    request_thread(f"http://{esp32_ip}/led/rojo/on")

    # Repetir ciclo después de t_rojo
    app.after(t_rojo, rutina_semaforo)

# --- Funciones LEDs ---
def Manejar_estado_verde():
    if estado_verde.get() == 1:
        button_verde.config(bg="#737F85", fg="white", font=("Helvetica", 9, "bold"))
        request_thread(f"http://{esp32_ip}/led/verde/off")
        canvas.itemconfig(verde, fill="#737F85")
    else:
        button_verde.config(bg="#34B81A", fg="black", font=("Helvetica", 9, "bold"))
        request_thread(f"http://{esp32_ip}/led/verde/on")
        canvas.itemconfig(verde, fill="#34B81A")

def Manejar_estado_amarillo():
    if estado_amarillo.get() == 1:
        button_amarillo.config(bg="#737F85", fg="white", font=("Helvetica", 9, "bold"))
        request_thread(f"http://{esp32_ip}/led/amarillo/off")
        canvas.itemconfig(amarilla, fill="#737F85")
    else:
        button_amarillo.config(bg="#F7EA00", fg="black", font=("Helvetica", 9, "bold"))
        request_thread(f"http://{esp32_ip}/led/amarillo/on")
        canvas.itemconfig(amarilla, fill="#F7EA00")

def Manejar_estado_rojo():
    if estado_rojo.get() == 1:
        button_rojo.config(bg="#737F85", fg="white", font=("Helvetica", 9, "bold"))
        request_thread(f"http://{esp32_ip}/led/rojo/off")
        canvas.itemconfig(roja, fill="#737F85")
    else:
        button_rojo.config(bg="red", fg="black", font=("Helvetica", 9, "bold"))
        request_thread(f"http://{esp32_ip}/led/rojo/on")
        canvas.itemconfig(roja, fill="red")

# --- Funciones rutina ---
def Iniciar_rutina():
    global ciclo_activo
    estado_iniciar.set(1)
    estado_parar.set(0)
    button_iniciar.config(bg="#737F85")
    button_parar.config(bg="#2B4B75")
    ciclo_activo = True
    rutina_semaforo()  # Lanza la rutina


def Parar_rutina():
    global ciclo_activo
    ciclo_activo = False
    estado_parar.set(1)
    estado_iniciar.set(0)
    request_thread(f"http://{esp32_ip}/led/amarillo/off")
    request_thread(f"http://{esp32_ip}/led/rojo/off")
    request_thread(f"http://{esp32_ip}/led/verde/off")
    canvas.itemconfig(roja, fill="gray")
    canvas.itemconfig(verde, fill="gray")
    canvas.itemconfig(amarilla, fill="gray")
    button_parar.config(bg="#737F85")
    button_iniciar.config(bg="#2B4B75")

# --- Funciones Tiempo ---
def Tiempo_verde(valor):
    tiempo_segundos = scale_tiempo_verde.get()
    tiempo_ms = tiempo_segundos * 1000
    request_thread(f"http://{esp32_ip}/configurar?verde={tiempo_ms}")

def Tiempo_amarillo(valor):
    tiempo_segundos = scale_tiempo_amarillo.get()
    tiempo_ms = tiempo_segundos * 1000
    request_thread(f"http://{esp32_ip}/configurar?amarillo={tiempo_ms}")

def Tiempo_rojo(valor):
    tiempo_segundos = scale_tiempo_rojo.get()
    tiempo_ms = tiempo_segundos * 1000
    request_thread(f"http://{esp32_ip}/configurar?rojo={tiempo_ms}")

# ---------------- Interfaz ----------------
SidebarFrame = tk.Frame(app, bg="#5A7497", padx=20)
SidebarFrame.pack(fill=tk.Y, side=tk.LEFT)
#Titulo
tk.Label(SidebarFrame, text="Controles de los leds", bg="#5A7497", fg="white",font=("Helvetica", 11, "bold")).pack(pady=10)

MainFrame = tk.Frame(app, bg="#FCF7F7")
MainFrame.pack(fill=tk.BOTH, expand=True)

# LEDs
button_verde = tk.Checkbutton(SidebarFrame, text="Verde", bg="#34B81A", fg="black",
                              width=15, height=2, variable=estado_verde, indicatoron=0,
                              command=Manejar_estado_verde, selectcolor="", font=("Helvetica", 9, "bold"))
button_verde.pack(pady=10)

button_amarillo = tk.Checkbutton(SidebarFrame, text="Amarillo", bg="#F7EA00", fg="black",
                                 width=15, height=2, variable=estado_amarillo, indicatoron=0,
                                 command=Manejar_estado_amarillo, selectcolor="", font=("Helvetica", 9, "bold"))
button_amarillo.pack(pady=10)

button_rojo = tk.Checkbutton(SidebarFrame, text="Rojo", bg="red", fg="black",
                             width=15, height=2, variable=estado_rojo, indicatoron=0,
                             command=Manejar_estado_rojo, selectcolor="", font=("Helvetica", 9, "bold"))
button_rojo.pack(pady=10)

# Línea horizontal simulando <hr>
hr = tk.Frame(SidebarFrame, bg="black", height=1, width=150)
hr.pack(pady=10)

#Titulo
tk.Label(SidebarFrame, text="Controles del Semáforo",bg="#5A7497", fg="white", font=("Helvetica", 11, "bold")).pack(pady=10)

# Rutina con dos botones
button_iniciar = tk.Checkbutton(SidebarFrame, text="Iniciar", bg="#2B4B75", fg="white",
                                width=15, height=2, variable=estado_iniciar, indicatoron=0,
                                command=Iniciar_rutina, selectcolor="", font=("Helvetica", 9, "bold"))
button_iniciar.pack(pady=10)

button_parar = tk.Checkbutton(SidebarFrame, text="Parar", bg="#737F85", fg="white",
                              width=15, height=2, variable=estado_parar, indicatoron=0,
                              command=Parar_rutina, selectcolor="", font=("Helvetica", 9, "bold"))
button_parar.pack(pady=10)

# ---------------- Animación Semaforo ----------------

canvas = tk.Canvas(MainFrame, width=120, height=300, bg="black")
canvas.pack(pady=10)


# Dibujar semaforo
verde = canvas.create_oval(20, 20, 100, 100, fill="gray")
roja = canvas.create_oval(20, 200, 100, 280, fill="gray") 
amarilla = canvas.create_oval(20, 110, 100, 190, fill="gray")
canvas.itemconfig(verde, fill="#34B81A")
canvas.itemconfig(amarilla, fill="#F7EA00")
canvas.itemconfig(roja, fill="red")

# ---------------- Scales en MainFrame ----------------

# Frame para contener los scales en fila
scales_frame = tk.Frame(MainFrame, bg="#FCF7F7")
scales_frame.pack(pady=20)

# Tiempo verde
tk.Label(scales_frame, text="Tiempo Verde", bg="#FCF7F7", fg="black", font=("Helvetica", 9)).grid(row=0, column=0, padx=10)
scale_tiempo_verde = tk.Scale(scales_frame, from_=1, to=20, orient=tk.HORIZONTAL, bg="#FCF7F7", fg="black", font=("Helvetica", 9), command=Tiempo_verde)
scale_tiempo_verde.grid(row=1, column=0, padx=10)
scale_tiempo_verde.set(5)

# Tiempo amarillo
tk.Label(scales_frame, text="Tiempo Amarillo", bg="#FCF7F7", fg="black", font=("Helvetica", 9)).grid(row=0, column=1, padx=10)
scale_tiempo_amarillo = tk.Scale(scales_frame, from_=1, to=20, orient=tk.HORIZONTAL, bg="#FCF7F7", fg="black", font=("Helvetica", 9), command=Tiempo_amarillo)
scale_tiempo_amarillo.grid(row=1, column=1, padx=10)

scale_tiempo_amarillo.set(2)

# Tiempo rojo
tk.Label(scales_frame, text="Tiempo Rojo", bg="#FCF7F7", fg="black", font=("Helvetica", 9)).grid(row=0, column=2, padx=10)
scale_tiempo_rojo = tk.Scale(scales_frame, from_=1, to=20, orient=tk.HORIZONTAL, bg="#FCF7F7", fg="black", font=("Helvetica", 9), command=Tiempo_rojo)
scale_tiempo_rojo.grid(row=1, column=2, padx=10)
scale_tiempo_rojo.set(9)

app.mainloop()
