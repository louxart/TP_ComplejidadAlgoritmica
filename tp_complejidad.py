import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict
import csv
from pathlib import Path

class RecetarioGrafo:
    def __init__(self, archivo_csv):
        self.archivo = archivo_csv
        self.grafo = nx.Graph()
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
                    headers = next(reader)
                    
                    self.recetas = []
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
                
                print(f"Archivo leído correctamente con codificación: {codificacion}")
                break
                    
            except UnicodeDecodeError:
                continue
            except Exception as e:
                print(f"Error con codificación {codificacion}: {e}")
                continue
        else:
            raise ValueError("No se pudo leer el archivo con ninguna codificación probada")
        
        self.categorias = list(set(receta['categoria'] for receta in self.recetas))
    
    def construir_grafo(self):
        for categoria in self.categorias:
            self.grafo.add_node(categoria, tipo='categoria', size=1500)
        
        for receta in self.recetas:
            nombre_receta = receta['nombre']
            categoria = receta['categoria']
            
            self.grafo.add_node(nombre_receta, tipo='receta', size=1000)
            self.grafo.add_edge(categoria, nombre_receta, relacion='pertenece_a')
            
            for ingrediente in receta['ingredientes']:
                self.grafo.add_node(ingrediente, tipo='ingrediente', size=500)
                self.grafo.add_edge(nombre_receta, ingrediente, relacion='usa')
    
    def visualizar_grafo(self, categoria=None, ingrediente=None, layout='spring'):
        plt.figure(figsize=(15, 12))
        if categoria and categoria in self.grafo:
            nodos = [n for n in self.grafo.neighbors(categoria)] + [categoria]
            subgrafo = self.grafo.subgraph(nodos)
            titulo = f"Grafo de Recetas - Categoría: {categoria}"
        elif ingrediente and ingrediente in self.grafo:
            recetas_con_ingrediente = list(self.grafo.neighbors(ingrediente))
            categorias = set()
            for receta in recetas_con_ingrediente:
                for categoria_receta in self.grafo.neighbors(receta):
                    if self.grafo.nodes[categoria_receta]['tipo'] == 'categoria':
                        categorias.add(categoria_receta)
            nodos = recetas_con_ingrediente + list(categorias) + [ingrediente]
            subgrafo = self.grafo.subgraph(nodos)
            titulo = f"Grafo de Recetas - Ingrediente: {ingrediente}"
        else:
            subgrafo = self.grafo
            titulo = "Grafo Completo del Recetario"
            
        if layout == 'spring':
            pos = nx.spring_layout(subgrafo, k=0.5, seed=42)
        elif layout == 'circular':
            pos = nx.circular_layout(subgrafo)
        else:
            pos = nx.kamada_kawai_layout(subgrafo)
        
        node_colors = []
        node_sizes = []
        for node, data in subgrafo.nodes(data=True):
            if data['tipo'] == 'categoria':
                node_colors.append('#1f78b4')  
                node_sizes.append(2000)
            elif data['tipo'] == 'receta':
                node_colors.append('#33a02c') 
                node_sizes.append(1200)
            else:
                node_colors.append('#e31a1c')  
                node_sizes.append(800)
        
        nx.draw_networkx_nodes(
            subgrafo, pos, 
            node_size=node_sizes, 
            node_color=node_colors,
            alpha=0.9
        )
        
        edge_colors = []
        for _, _, data in subgrafo.edges(data=True):
            if data['relacion'] == 'pertenece_a':
                edge_colors.append('#a6cee3')  
            else:
                edge_colors.append('#fb9a99')  
        
        nx.draw_networkx_edges(
            subgrafo, pos,
            edge_color=edge_colors,
            width=1.5,
            alpha=0.6
        )
        
        nx.draw_networkx_labels(
            subgrafo, pos,
            font_size=8,
            font_family='sans-serif'
        )
        
        plt.title(titulo)
        plt.axis('off')
        
        legend_elements = [
            plt.Line2D([0], [0], marker='o', color='w', label='Categoría', markersize=10, markerfacecolor='#1f78b4'),
            plt.Line2D([0], [0], marker='o', color='w', label='Receta', markersize=10, markerfacecolor='#33a02c'),
            plt.Line2D([0], [0], marker='o', color='w', label='Ingrediente', markersize=10, markerfacecolor='#e31a1c')
        ]
        plt.legend(handles=legend_elements, loc='upper right')
        
        plt.tight_layout()
        plt.show()
    
    def buscar_recetas(self, ingrediente=None, categoria=None):
        """Busca recetas por ingrediente, categoría o ambos"""
        resultados = []
        
        for receta in self.recetas:
            match_categoria = (categoria is None) or (receta['categoria'] == categoria)
            match_ingrediente = (ingrediente is None) or (ingrediente in receta['ingredientes'])
            
            if match_categoria and match_ingrediente:
                resultados.append(receta['nombre'])
        
        return resultados
    
    def ingredientes_comunes(self, receta1, receta2):
        """Encuentra ingredientes comunes entre dos recetas"""
        ingredientes1 = set()
        ingredientes2 = set()
        
        for receta in self.recetas:
            if receta['nombre'] == receta1:
                ingredientes1 = set(receta['ingredientes'])
            if receta['nombre'] == receta2:
                ingredientes2 = set(receta['ingredientes'])
        
        return list(ingredientes1 & ingredientes2)
    
    def recetas_por_categoria(self):
        """Devuelve un diccionario con recetas agrupadas por categoría"""
        por_categoria = defaultdict(list)
        for receta in self.recetas:
            por_categoria[receta['categoria']].append(receta['nombre'])
        return dict(por_categoria)

if __name__ == "__main__":
    recetario = RecetarioGrafo("are(Hoja1).csv")
        
    print("\n1. Visualización de la categoría 'Postre':")
    recetario.visualizar_grafo(categoria="Postre")

    # busquedas
    print("\n2. Recetas que usan 'limón':")
    print(recetario.buscar_recetas(ingrediente="limón"))
        
    print("\n3. Recetas de la categoría 'Bebida':")
    print(recetario.buscar_recetas(categoria="Bebida"))
        
    