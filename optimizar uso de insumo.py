import tkinter as tk
from tkinter import ttk, messagebox
import csv
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def mostrar_grafo(grafo, titulo, frame_canvas):
    for widget in frame_canvas.winfo_children():
        widget.destroy()

    fig, ax = plt.subplots(figsize=(8, 6))

    try:
        pos = nx.kamada_kawai_layout(grafo)
    except:
        pos = nx.circular_layout(grafo)

    nx.draw_networkx_nodes(grafo, pos, node_color='lightgreen', node_size=700, edgecolors='black', ax=ax)
    nx.draw_networkx_edges(grafo, pos, ax=ax)

    etiquetas = {n: n.capitalize() for n in grafo.nodes}
    nx.draw_networkx_labels(grafo, pos, labels=etiquetas, font_size=8, ax=ax)

    edge_labels = {(u, v): f"{d.get('frecuencia', '')}" for u, v, d in grafo.edges(data=True)}
    nx.draw_networkx_edge_labels(grafo, pos, edge_labels=edge_labels, font_size=7, ax=ax)

    ax.set_title(titulo, fontsize=12, fontweight='bold')
    ax.axis("off")

    canvas = FigureCanvasTkAgg(fig, master=frame_canvas)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)

class GrafoIngredientes:
    def __init__(self):
        self.grafo = nx.Graph()

    def cargar_csv(self, archivo):
        with open(archivo, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for fila in reader:
                ingrediente = fila['Ingrediente'].strip().lower()
                costo = float(fila['Costo unitario estimado (S/)'])
                self.grafo.add_node(ingrediente, tipo='ingrediente', costo=costo)

                cooc = fila.get('Co-ocurrencias frecuentes', '')
                coocurrencias = [i.strip().lower() for i in cooc.split(',') if i.strip()]
                frecuencia = int(fila.get('Frecuencia', 1))

                for co in coocurrencias:
                    self.grafo.add_node(co, tipo='ingrediente')
                    self.grafo.add_edge(ingrediente, co, frecuencia=frecuencia)

    def dfs_coocurrencia(self, start, max_depth=2, max_nodos=10):
        visitado = set()
        resultado = []

        def dfs(nodo, profundidad):
            if len(resultado) >= max_nodos:
                return
            if nodo not in visitado and profundidad <= max_depth:
                visitado.add(nodo)
                resultado.append((nodo, profundidad))
                for vecino in sorted(self.grafo.neighbors(nodo)):
                    dfs(vecino, profundidad + 1)

        dfs(start, 0)
        return resultado

    def mst_costos(self, nodos):
        sub = self.grafo.subgraph(nodos).copy()
        for u, v in sub.edges():
            cu = sub.nodes[u].get("costo", 999)
            cv = sub.nodes[v].get("costo", 999)
            sub[u][v]['weight'] = (cu + cv) / 2
        return nx.minimum_spanning_tree(sub, algorithm='kruskal')

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Optimización de Insumos por Coocurrencias")
        self.grafo = GrafoIngredientes()
        self.grafo.cargar_csv("ingredientes_completo.csv")
        self.crear_ui()

    def crear_ui(self):
        frame = ttk.Frame(self.root)
        frame.pack(fill="both", expand=True)

        self.left = ttk.Frame(frame)
        self.left.pack(side="left", padx=10, pady=10)

        ttk.Label(self.left, text="Ingrediente base:").pack()
        self.entrada = ttk.Entry(self.left)
        self.entrada.pack()

        ttk.Button(self.left, text="Buscar DFS", command=self.buscar_dfs).pack(pady=5)
        self.lista_dfs = tk.Listbox(self.left, width=40, height=6)
        self.lista_dfs.pack()

        ttk.Button(self.left, text="Optimizar MST", command=self.optimizar_mst).pack(pady=5)
        self.lista_mst = tk.Listbox(self.left, width=40, height=6)
        self.lista_mst.pack()

        self.right = ttk.Frame(frame)
        self.right.pack(side="right", fill="both", expand=True)

    def buscar_dfs(self):
        nodo = self.entrada.get().strip().lower()
        if not nodo or nodo not in self.grafo.grafo:
            messagebox.showerror("Error", "Ingrediente no válido.")
            return

        self.resultado_dfs = self.grafo.dfs_coocurrencia(nodo)
        self.lista_dfs.delete(0, tk.END)
        for nodo, prof in self.resultado_dfs:
            self.lista_dfs.insert(tk.END, f"{nodo} (Prof. {prof})")

        nodos = [n for n, _ in self.resultado_dfs]
        subgrafo = self.grafo.grafo.subgraph(nodos)
        mostrar_grafo(subgrafo, f"DFS desde {nodo}", self.right)

    def optimizar_mst(self):
        if not hasattr(self, "resultado_dfs"):
            messagebox.showinfo("Primero", "Ejecuta primero la búsqueda DFS.")
            return

        nodos = [n for n, _ in self.resultado_dfs]
        mst = self.grafo.mst_costos(nodos)

        self.lista_mst.delete(0, tk.END)
        for nodo in mst.nodes():
            costo = self.grafo.grafo.nodes[nodo].get("costo", 0)
            self.lista_mst.insert(tk.END, f"{nodo} (S/ {costo:.2f})")

        mostrar_grafo(mst, "Árbol de Costos Mínimos (MST)", self.right)

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
