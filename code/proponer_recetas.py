import tkinter as tk
from tkinter import messagebox
import csv
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import defaultdict


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
        self.root.title("Propuesta de Recetas (Ordenamiento Topologico y CFC)")
        self.recetas, self.grafo_ingredientes = self.cargar_recetas()
        self.recetas_sugeridas = []
        self.crear_ui()

    def cargar_recetas(self):
        recetas = []
        grafo = defaultdict(set)

        try:
            with open('dataset/recetario.csv', mode='r', encoding='latin-1') as archivo:
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


    def metodo_topologico(self):
        disponibles = set(i.strip().lower() for i in self.entrada.get().split(',') if i.strip())
        if not disponibles:
            messagebox.showinfo("Entrada vacía", "Por favor ingresa ingredientes.")
            return
        dependencias = {}
        for receta in self.recetas:
            ings = receta['ingredientes']
            if disponibles.issubset(ings):  
                for i in range(len(ings) - 1):
                    origen = ings[i]
                    destino = ings[i + 1]
                    if origen not in dependencias:
                        dependencias[origen] = []
                    if destino not in dependencias[origen]:
                        dependencias[origen].append(destino)
                for ing in ings:
                    if ing not in dependencias:
                        dependencias[ing] = []

        labels = list(dependencias.keys())
        w2i = {label: i for i, label in enumerate(labels)}
        info = [[w2i[dest] for dest in dependencias[src]] for src in labels]

        def ordenTopologico(G):
            n = len(G)
            indegree = [0] * n
            for u in range(n):
                for v in G[u]:
                    indegree[v] += 1

            cola = [u for u in range(n) if indegree[u] == 0]
            respuesta = []
            while cola:
                u = cola.pop(0)
                respuesta.append(u)
                for v in G[u]:
                    indegree[v] -= 1
                    if indegree[v] == 0:
                        cola.append(v)

            return respuesta if len(respuesta) == n else []
        orden = ordenTopologico(info)
        self.resultado.config(state='normal')
        self.resultado.delete('1.0', tk.END)

        if not orden:
            self.resultado.insert(tk.END, "❌ No se pudo realizar ordenamiento topológico.\n")
        else:
            self.resultado.insert(tk.END, "Orden sugerido de preparación (Topológico):\n\n")
            for i in orden:
                etiqueta = labels[i]
                if etiqueta in disponibles:
                    self.resultado.insert(tk.END, f"✔ {etiqueta} (disponible)\n")
                else:
                    self.resultado.insert(tk.END, f"- {etiqueta}\n")

            self.resultado.insert(tk.END, "\nRecetas sugeridas:\n\n")
            for receta in self.recetas:
                if disponibles.issubset(set(receta['ingredientes'])):
                    self.resultado.insert(tk.END, f"✔ {receta['nombre']} → {', '.join(receta['ingredientes'])}\n")

        self.resultado.config(state='disabled')

    def metodo_cfc(self):
        disponibles = set(i.strip().lower() for i in self.entrada.get().split(',') if i.strip())
        if not disponibles:
            messagebox.showinfo("Entrada vacía", "Por favor ingresa ingredientes.")
            return

        ingredientes_lista = list(self.grafo_ingredientes.keys())
        idx_map = {ing: i for i, ing in enumerate(ingredientes_lista)}
        rev_map = {i: ing for ing, i in idx_map.items()}
        n = len(ingredientes_lista)

        G = [[] for _ in range(n)]
        for u in ingredientes_lista:
            for v in self.grafo_ingredientes[u]:
                if u in idx_map and v in idx_map:
                    G[idx_map[u]].append(idx_map[v])

        def reverseGraph(G):
            Grev = [[] for _ in range(len(G))]
            for u in range(len(G)):
                for v in G[u]:
                    Grev[v].append(u)
            return Grev

        def dfs(G, u, lst, visited):
            visited[u] = True
            for v in G[u]:
                if not visited[v]:
                    dfs(G, v, lst, visited)
            lst.append(u)

        def kosaraju(G):
            visited = [False] * len(G)
            f = []
            Grev = reverseGraph(G)
            for u in range(len(G)):
                if not visited[u]:
                    dfs(Grev, u, f, visited)
            visited = [False] * len(G)
            scc = []
            for u in reversed(f):
                if not visited[u]:
                    cc = []
                    dfs(G, u, cc, visited)
                    scc.append(cc)
            return scc

        componentes = kosaraju(G)

        disponibles_idx = {idx_map[ing] for ing in disponibles if ing in idx_map}
        sugeridas = []

        for comp in componentes:
            comp_set = set(comp)
            if disponibles_idx.issubset(comp_set):  
                ingredientes_en_cfc = {rev_map[i] for i in comp}
                for receta in self.recetas:
                    receta_ings = set(receta['ingredientes'])
                    if disponibles.issubset(receta_ings) and receta_ings.issubset(ingredientes_en_cfc):
                        sugeridas.append(receta)

        self.recetas_sugeridas = sugeridas
        self.mostrar_texto_resultado(sugeridas, "Recetas encontradas (CFC - Kosaraju):")

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
    #Se utilizó IA para esta función, la cual crea la interfaz de usuario de la aplicación
    def crear_ui(self):
        self.root.configure(bg="#FAF8F6")
        self.root.option_add("*Cursor", "hand2")  # cursor tipo puntero en toda la UI

        frame = tk.Frame(self.root, bg="#FAF8F6", padx=25, pady=25)
        frame.pack(fill='both', expand=True)

        titulo = tk.Label(frame,
                        text="✨ Bienvenido al apartado de recomendaciones de Recetas",
                        font=("Helvetica Neue", 18, "bold"),
                        bg="#FAF8F6",
                        fg="#2E2E2E")
        titulo.pack(anchor='center', pady=(0, 20))

        subtitulo = tk.Label(frame,
                            text="Escribe los ingredientes que tienes (separados por comas)",
                            font=("Segoe UI", 10),
                            bg="#FAF8F6",
                            fg="#888888")
        subtitulo.pack(anchor='w', pady=(0, 10))

        self.entrada = tk.Entry(frame,
                                font=("Segoe UI", 11),
                                bg="#FFFFFF",
                                fg="#2E2E2E",
                                insertbackground="#6A1B9A",
                                relief="flat",
                                width=90,
                                highlightthickness=2,
                                highlightbackground="#D0D0D0",
                                highlightcolor="#9575CD")
        self.entrada.pack(pady=(0, 20), ipady=8)

        botones = tk.Frame(frame, bg="#FAF8F6")
        botones.pack(pady=5)

        estilo_boton = {
            "font": ("Segoe UI", 10, "bold"),
            "bg": "#D1C4E9",
            "fg": "#2E2E2E",
            "activebackground": "#B39DDB",
            "activeforeground": "#FFFFFF",
            "relief": "flat",
            "bd": 0,
            "padx": 12,
            "pady": 10,
            "width": 32
        }

        tk.Button(botones, text=" Recetas (Orden Topológico)", command=self.metodo_topologico, **estilo_boton).pack(side='left', padx=8)
        tk.Button(botones, text=" Recetas (CFC Kosaraju)", command=self.metodo_cfc, **estilo_boton).pack(side='left', padx=8)
        tk.Button(botones, text=" Visualizar Grafo", command=self.mostrar_grafo, **estilo_boton).pack(side='left', padx=8)

        self.resultado = tk.Text(frame,
                                font=("JetBrains Mono", 10),
                                width=100,
                                height=18,
                                state='disabled',
                                bg="#FFFFFF",
                                fg="#2E2E2E",
                                relief="flat",
                                bd=1,
                                highlightthickness=1,
                                highlightbackground="#DDD",
                                insertbackground="#6A1B9A",
                                padx=10,
                                pady=10)
        self.resultado.pack(padx=5, pady=25)

        self.canvas_frame = tk.Frame(self.root, bg="#FAF8F6")
        self.canvas_frame.pack(fill='both', expand=True, pady=(0, 10))
