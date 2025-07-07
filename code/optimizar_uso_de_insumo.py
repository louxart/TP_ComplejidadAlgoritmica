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
    fig.tight_layout()

    try:
        pos = nx.kamada_kawai_layout(grafo)
    except:
        pos = nx.spring_layout(grafo)

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
        self.root.geometry("1000x700")
        self.root.configure(bg="#F5F5F5")
        self.root.option_add("*Font", ("Segoe UI", 10))


        self.grafo = GrafoIngredientes()
        self.grafo.cargar_csv("dataset/ingredientes_completo.csv")
        self.crear_ui()

    def crear_ui(self):
        # Estilo visual
        style = ttk.Style()
        style.configure("TFrame", background="#F5F5F5")
        style.configure("TLabel", background="#F5F5F5", font=("Segoe UI", 10))
        style.configure("TButton", font=("Segoe UI", 10, "bold"))

        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill="both", expand=True)

        # Panel izquierdo (entrada y botones)
        self.left = ttk.Frame(main_frame, padding=10, relief="ridge")
        self.left.pack(side="left", fill="y", padx=10, pady=10)

        ttk.Label(self.left, text="Ingrediente base:").pack(anchor="w", pady=(0, 3))
        self.entrada = ttk.Entry(self.left, width=30)
        self.entrada.pack(pady=(0, 10))

        ttk.Button(self.left, text="Buscar co-ocurrencias (DFS)", command=self.buscar_dfs).pack(fill="x", pady=5)

        ttk.Label(self.left, text="Ingredientes relacionados:").pack(anchor="w", pady=(10, 3))
        self.lista_dfs = tk.Listbox(self.left, height=6, width=35, bg="white", relief="solid", borderwidth=1)
        self.lista_dfs.pack(fill="x", pady=(0, 10))

        ttk.Button(self.left, text="Optimizar conexión (MST)", command=self.optimizar_mst).pack(fill="x", pady=5)

        ttk.Label(self.left, text="Insumos optimizados:").pack(anchor="w", pady=(10, 3))
        self.lista_mst = tk.Listbox(self.left, height=6, width=35, bg="white", relief="solid", borderwidth=1)
        self.lista_mst.pack(fill="x")

        # Panel derecho (grafo)
        self.right = ttk.LabelFrame(main_frame, text="Visualización del Grafo", padding=10)
        self.right.pack(side="right", fill="both", expand=True, padx=10, pady=10)

    def buscar_dfs(self):
        nodo = self.entrada.get().strip().lower()
        if not nodo:
            messagebox.showerror("Error", "Ingrese un ingrediente.")
            return
        if nodo not in self.grafo.grafo.nodes:
            messagebox.showerror("Error", f"No se encontró '{nodo}' en el grafo.")
            return

        self.resultado_dfs = self.grafo.dfs_coocurrencia(nodo)
        self.lista_dfs.delete(0, tk.END)
        for nodo_resultado, prof in self.resultado_dfs:
            self.lista_dfs.insert(tk.END, f"{nodo_resultado} (Prof. {prof})")

        nodos = [n for n, _ in self.resultado_dfs]
        subgrafo = self.grafo.grafo.subgraph(nodos)
        mostrar_grafo(subgrafo, f"Exploración desde '{nodo.capitalize()}'", self.right)

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

        mostrar_grafo(mst, "Reducción de insumos por conexiones óptimas (MST)", self.right)


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
