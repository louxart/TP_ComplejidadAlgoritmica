import tkinter as tk
from tkinter import ttk, messagebox
import csv
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import defaultdict, deque


def mostrar_grafo(grafo, titulo, frame_canvas):
    for widget in frame_canvas.winfo_children():
        widget.destroy()

    fig, ax = plt.subplots(figsize=(8, 6))

    try:
        pos = nx.kamada_kawai_layout(grafo)
    except:
        pos = nx.circular_layout(grafo)

    nx.draw_networkx_nodes(grafo, pos, node_color='lightblue', node_size=700, edgecolors='black', ax=ax)
    nx.draw_networkx_edges(grafo, pos, ax=ax)

    etiquetas = {n: n.capitalize() for n in grafo.nodes}
    nx.draw_networkx_labels(grafo, pos, labels=etiquetas, font_size=8, ax=ax)

    ax.set_title(titulo, fontsize=12, fontweight='bold')
    ax.axis("off")

    canvas = FigureCanvasTkAgg(fig, master=frame_canvas)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)


class ProponerRecetaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Propuesta de Recetas (Greedy y CFC)")
        self.recetas, self.grafo_ingredientes = self.cargar_recetas()
        self.recetas_sugeridas = []
        self.crear_ui()

    def cargar_recetas(self):
        recetas = []
        grafo = defaultdict(set)

        try:
            with open('recetario.csv', mode='r', encoding='latin-1') as archivo:
                lector = csv.DictReader(archivo, delimiter=';')
                for fila in lector:
                    nombre = fila['Receta'].strip()
                    ingredientes = [i.strip().lower() for i in fila['Ingredientes'].split(',')]
                    recetas.append({'nombre': nombre, 'ingredientes': ingredientes})
                    for i in ingredientes:
                        for j in ingredientes:
                            if i != j:
                                grafo[i].add(j)
        except Exception as e:
            messagebox.showerror("Error al cargar recetas", str(e))
        return recetas, grafo

    def crear_ui(self):
        frame = ttk.Frame(self.root, padding=10)
        frame.pack(fill='both', expand=True)

        ttk.Label(frame, text="Ingredientes disponibles (separados por comas):").pack(anchor='w')
        self.entrada = ttk.Entry(frame, width=80)
        self.entrada.pack(pady=5)

        botones = ttk.Frame(frame)
        botones.pack(pady=5)

        ttk.Button(botones, text="Proponer Recetas (Greedy)", command=self.metodo_greedy).pack(side='left', padx=5)
        ttk.Button(botones, text="Proponer Recetas (CFC)", command=self.metodo_cfc).pack(side='left', padx=5)
        ttk.Button(botones, text="Mostrar Grafo", command=self.mostrar_grafo).pack(side='left', padx=5)

        self.resultado = tk.Text(frame, width=100, height=20, state='disabled')
        self.resultado.pack(padx=5, pady=10)

        self.canvas_frame = ttk.Frame(self.root)
        self.canvas_frame.pack(fill='both', expand=True)

    def metodo_greedy(self):
        disponibles = set(i.strip().lower() for i in self.entrada.get().split(',') if i.strip())
        sugeridas = []

        for receta in self.recetas:
            if set(receta['ingredientes']).issubset(disponibles):
                sugeridas.append(receta)

        self.recetas_sugeridas = sugeridas
        self.mostrar_texto_resultado(sugeridas, "Recetas encontradas (Greedy):")

    def metodo_cfc(self):
        disponibles = set(i.strip().lower() for i in self.entrada.get().split(',') if i.strip())
        visitado = set()
        componente = set()

        def bfs(nodo):
            cola = deque([nodo])
            while cola:
                actual = cola.popleft()
                if actual not in visitado:
                    visitado.add(actual)
                    componente.add(actual)
                    cola.extend(self.grafo_ingredientes.get(actual, []))

        for ing in disponibles:
            if ing not in visitado:
                bfs(ing)

        sugeridas = []
        for receta in self.recetas:
            receta_ingreds = set(receta['ingredientes'])
            if disponibles.issubset(receta_ingreds) and receta_ingreds.issubset(componente):
                sugeridas.append(receta)

        self.recetas_sugeridas = sugeridas
        self.mostrar_texto_resultado(sugeridas, "Recetas encontradas (CFC con ingredientes obligatorios):")


    def mostrar_texto_resultado(self, recetas, titulo):
        self.resultado.config(state='normal')
        self.resultado.delete('1.0', tk.END)
        self.resultado.insert(tk.END, f"{titulo}\n\n")
        if not recetas:
            self.resultado.insert(tk.END, "No se encontraron recetas :( ).\n")
        else:
            for r in recetas:
                self.resultado.insert(tk.END, f"✔ {r['nombre']} → {', '.join(r['ingredientes'])}\n")
        self.resultado.config(state='disabled')

    def mostrar_grafo(self):
        if not self.recetas_sugeridas:
            messagebox.showinfo("Sin recetas", "Primero genera una propuesta de recetas.")
            return

        G = nx.Graph()
        for receta in self.recetas_sugeridas:
            nombre = receta['nombre']
            G.add_node(nombre, tipo='receta')
            for ing in receta['ingredientes']:
                G.add_node(ing, tipo='ingrediente')
                G.add_edge(nombre, ing)

        mostrar_grafo(G, "Grafo de Recetas e Ingredientes", self.canvas_frame)
