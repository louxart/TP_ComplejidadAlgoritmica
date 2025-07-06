import tkinter as tk
from tkinter import ttk, messagebox
import csv
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os

class GrafoRutas:
    def __init__(self):
        self.grafo = nx.Graph()
        self.restaurantes = {}

    def cargar_datos(self, archivo_restaurantes, archivo_conexiones):
        with open(archivo_restaurantes, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for fila in reader:
                nombre = fila["Nombre"].strip()
                distrito = fila["Distrito"].strip()
                direccion = fila["Direccion"].strip()
                self.restaurantes[nombre] = {
                    "distrito": distrito,
                    "direccion": direccion
                }
                self.grafo.add_node(distrito)

        with open(archivo_conexiones, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for fila in reader:
                origen = fila["Origen"].strip()
                destino = fila["Destino"].strip()
                tiempo = int(fila["Tiempo_min"])
                self.grafo.add_edge(origen, destino, weight=tiempo)

    def calcular_ruta(self, origen, restaurante):
        datos = self.restaurantes.get(restaurante)
        if not datos:
            raise ValueError("Restaurante no encontrado.")

        distrito_destino = datos["distrito"]
        if origen == distrito_destino:
            return [origen], 0

        ruta = nx.dijkstra_path(self.grafo, origen, distrito_destino, weight="weight")
        tiempo = nx.dijkstra_path_length(self.grafo, origen, distrito_destino, weight="weight")
        return ruta, tiempo

    def obtener_distritos(self):
        return sorted(self.grafo.nodes)

    def obtener_restaurantes(self):
        return sorted(self.restaurantes.keys())

    def obtener_distrito_de_restaurante(self, nombre):
        return self.restaurantes.get(nombre, {}).get("distrito", "Desconocido")

    def obtener_direccion_de_restaurante(self, nombre):
        return self.restaurantes.get(nombre, {}).get("direccion", "No disponible")


def mostrar_grafo(grafo, ruta, frame_canvas):
    for widget in frame_canvas.winfo_children():
        widget.destroy()

    fig, ax = plt.subplots(figsize=(8, 6))
    pos = nx.spring_layout(grafo)
    nx.draw(grafo, pos, with_labels=True, node_color="lightblue", edge_color="gray", node_size=800, ax=ax)

    if ruta:
        edges_ruta = list(zip(ruta, ruta[1:]))
        nx.draw_networkx_edges(grafo, pos, edgelist=edges_ruta, edge_color="red", width=2.5, ax=ax)

    ax.set_title("Ruta sugerida", fontsize=12)
    canvas = FigureCanvasTkAgg(fig, master=frame_canvas)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Calculadora de Ruta a Restaurante")
        self.root.geometry("1000x600")
        self.root.configure(bg="#f0f4f7")
        self.grafo = GrafoRutas()

        base_path = os.getcwd()
        restaurantes_csv = os.path.join(base_path, "restaurantes_lima.csv")
        conexiones_csv = os.path.join(base_path, "conexiones_lima.csv")

        try:
            self.grafo.cargar_datos(restaurantes_csv, conexiones_csv)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.root.destroy()
            return

        self.crear_ui()

    def crear_ui(self):
        frame = ttk.Frame(self.root)
        frame.pack(fill="both", expand=True)

        estilo = {'font': ('Segoe UI', 10), 'padding': 5}

        left = ttk.LabelFrame(frame, text="Datos de entrada", padding=10)
        left.pack(side="left", padx=20, pady=20, fill="y")

        ttk.Label(left, text="Selecciona tu distrito:", **estilo).pack(anchor="w")
        self.origen_combo = ttk.Combobox(left, values=self.grafo.obtener_distritos(), state="readonly", width=30)
        self.origen_combo.pack(pady=2)

        ttk.Label(left, text="Selecciona un restaurante:", **estilo).pack(anchor="w", pady=(10, 0))
        self.restaurante_combo = ttk.Combobox(left, values=self.grafo.obtener_restaurantes(), state="readonly", width=30)
        self.restaurante_combo.pack(pady=2)

        ttk.Button(left, text="Calcular Ruta", command=self.calcular_ruta).pack(pady=10)

        self.resultado_label = ttk.Label(left, text="", wraplength=280, justify="left", font=('Segoe UI', 9))
        self.resultado_label.pack(pady=5)

        ttk.Label(left, text="Ruta:", **estilo).pack(anchor="w", pady=(10, 0))
        self.lista_ruta = tk.Listbox(left, width=35, height=10)
        self.lista_ruta.pack()

        self.right = ttk.LabelFrame(frame, text="Visualización del grafo", padding=10)
        self.right.pack(side="right", fill="both", expand=True, padx=10, pady=20)

    def calcular_ruta(self):
        origen = self.origen_combo.get()
        restaurante = self.restaurante_combo.get()

        if not origen or not restaurante:
            messagebox.showwarning("Advertencia", "Selecciona el distrito y el restaurante.")
            return

        try:
            ruta, tiempo = self.grafo.calcular_ruta(origen, restaurante)
            distrito_destino = self.grafo.obtener_distrito_de_restaurante(restaurante)
            direccion = self.grafo.obtener_direccion_de_restaurante(restaurante)

            self.resultado_label.config(
                text=f"Destino: {restaurante}\nDirección: {direccion}\nDistrito: {distrito_destino}\nTiempo estimado: {tiempo} min")
            self.lista_ruta.delete(0, tk.END)
            for paso in ruta:
                self.lista_ruta.insert(tk.END, paso)

            mostrar_grafo(self.grafo.grafo, ruta, self.right)

        except Exception as e:
            messagebox.showerror("Error", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
