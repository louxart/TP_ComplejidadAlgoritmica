import pandas as pd
import networkx as nx
import csv
from pathlib import Path
import heapq
import tkinter as tk
from tkinter import messagebox

class RecetarioGrafo:
    def __init__(self, archivo_csv):
        self.archivo = archivo_csv
        self.grafo = nx.Graph()
        self.recetas = []
        self.categorias = []
        self.cargar_datos()
        self.construir_grafo()

    def cargar_datos(self):
        if not Path(self.archivo).is_file():
            raise FileNotFoundError(f"No se encontró el archivo: {self.archivo}")
        
        codificaciones = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
        for codificacion in codificaciones:
            try:
                with open(self.archivo, mode='r', encoding=codificacion) as file:
                    reader = csv.reader(file, delimiter=';')
                    next(reader)  # Saltar encabezado
                    for row in reader:
                        if not row:
                            continue
                        receta = {
                            'nombre': row[0].strip(),
                            'categoria': row[1].strip(),
                            'ingredientes': []
                        }
                        for cell in row[2:]:
                            if cell.strip():
                                ingredientes = [ing.strip() for ing in cell.split(',') if ing.strip()]
                                receta['ingredientes'].extend(ingredientes)
                        self.recetas.append(receta)
                break
            except UnicodeDecodeError:
                continue
        self.categorias = list(set(r['categoria'] for r in self.recetas))

    def construir_grafo(self):
        for cat in self.categorias:
            self.grafo.add_node(cat, tipo='categoria')
        for receta in self.recetas:
            r_nombre = receta['nombre']
            r_categoria = receta['categoria']
            self.grafo.add_node(r_nombre, tipo='receta')
            self.grafo.add_edge(r_categoria, r_nombre, relacion='pertenece_a')
            for ing in receta['ingredientes']:
                self.grafo.add_node(ing, tipo='ingrediente')
                self.grafo.add_edge(r_nombre, ing, relacion='usa')

    def dfs_recetas_desde_ingrediente(self, ingrediente):
        if ingrediente not in self.grafo:
            return []
        visitados = set()
        recorrido = []
        def dfs(nodo):
            visitados.add(nodo)
            recorrido.append(nodo)
            for vecino in self.grafo.neighbors(nodo):
                if vecino not in visitados:
                    dfs(vecino)
        dfs(ingrediente)
        return recorrido

    def buscar_recetas(self):
        return [r['nombre'] for r in self.recetas]

    def ucs_busqueda(self, inicio, objetivo):
        if inicio not in self.grafo or objetivo not in self.grafo:
            return None
        frontera = [(0, [inicio])]
        visitados = set()
        while frontera:
            costo, camino = heapq.heappop(frontera)
            actual = camino[-1]
            if actual == objetivo:
                return camino, costo
            if actual in visitados:
                continue
            visitados.add(actual)
            for vecino in self.grafo.neighbors(actual):
                if vecino not in visitados:
                    heapq.heappush(frontera, (costo + 1, camino + [vecino]))
        return None

    def rutas_ucs_completas(self, ingrediente):
        """Devuelve todas las rutas UCS desde el ingrediente a recetas alcanzables"""
        rutas = []
        for receta in self.buscar_recetas():
            resultado = self.ucs_busqueda(ingrediente, receta)
            if resultado:
                camino, costo = resultado
                rutas.append((receta, camino, costo))
        return rutas


def iniciar_interfaz():
    def buscar():
        ing = entry_ingrediente.get().strip().lower()
        if not ing:
            messagebox.showwarning("Advertencia", "Ingrese un ingrediente.")
            return

        resultado_texto.delete("1.0", tk.END)

        if metodo.get() == "dfs":
            recorrido = recetario.dfs_recetas_desde_ingrediente(ing)
            recetas = [n for n in recorrido if recetario.grafo.nodes[n].get("tipo") == "receta"]
            resultado_texto.insert(tk.END, "🔍 Recetas encontradas (DFS):\n")
            resultado_texto.insert(tk.END, "\n".join(recetas))
            resultado_texto.insert(tk.END, "\n\n🧭 Recorrido DFS completo:\n" + " -> ".join(recorrido))
        else:
            rutas = recetario.rutas_ucs_completas(ing)
            if not rutas:
                resultado_texto.insert(tk.END, "No se encontraron rutas UCS.")
                return

            rutas_ordenadas = sorted(rutas, key=lambda x: x[2])[:5]  # ✅ las 5 recetas más cercanas
            resultado_texto.insert(tk.END, "🔍 5 recetas más cercanas por UCS:\n\n")
            for i, (receta, camino, costo) in enumerate(rutas_ordenadas, 1):
                resultado_texto.insert(tk.END, f"{i}. {receta} (costo: {costo})\n")
                resultado_texto.insert(tk.END, f"   Ruta: {' -> '.join(camino)}\n\n")

    ventana = tk.Tk()
    ventana.title("Buscador de Recetas por Ingrediente (DFS/UCS)")
    ventana.geometry("600x500")

    tk.Label(ventana, text="Ingrese un ingrediente:", font=("Arial", 12)).pack(pady=10)
    entry_ingrediente = tk.Entry(ventana, width=40, font=("Arial", 11))
    entry_ingrediente.pack()

    metodo = tk.StringVar(value="dfs")
    frame_opciones = tk.Frame(ventana)
    frame_opciones.pack(pady=10)
    tk.Radiobutton(frame_opciones, text="DFS (Explorar todo)", variable=metodo, value="dfs").pack(side=tk.LEFT, padx=10)
    tk.Radiobutton(frame_opciones, text="UCS (Top 5 rutas óptimas)", variable=metodo, value="ucs").pack(side=tk.LEFT, padx=10)

    tk.Button(ventana, text="Buscar Recetas", command=buscar, bg="#33a02c", fg="white", font=("Arial", 11)).pack(pady=10)

    resultado_texto = tk.Text(ventana, height=20, width=70, font=("Courier", 10))
    resultado_texto.pack(pady=10)

    ventana.mainloop()



if __name__ == "__main__":
    recetario = RecetarioGrafo("are(Hoja1).csv")
    iniciar_interfaz()
