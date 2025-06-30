import csv
import tkinter as tk
from tkinter import scrolledtext, messagebox
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import os 
import random 
from collections import defaultdict 

RUTA_ARCHIVO_RECETAS = 'recetario.csv'
CATEGORIAS_MENU = ['Entrada', 'Segundo', 'Postre', 'Bebida']
ESTILOS = {
    'bg_main': '#FFFFFF',  
    'bg_frame': '#E0F2F7',  
    'fg_text': '#333333',  
    'font_title': ('Arial', 12, 'bold'), 
    'font_label': ('Arial', 9), 
    'font_button': ('Arial', 9, 'bold'),
    'button_bg': '#4CAF50',  
    'button_fg': '#ffffff',
    'entry_bg': '#F0F8FF', 
    'text_area_bg': '#F0F8FF', 
    'node_recipe_color': '#1E90FF', 
    'node_ingredient_color': '#FFD700', 
    'edge_color': '#696969' 
}

UMBRALES_MINIMOS_POR_CATEGORIA = {
    'Entrada': 5,
    'Segundo': 5,
    'Postre': 5,
    'Bebida': 3,
    'Default': 3 
}

class RecetarioGrafo:
    def __init__(self):
        self.grafo = nx.Graph()
        self.recetas_info = {} 
        self.ingredientes_conocidos = set() 

    def cargar_desde_csv(self, ruta_archivo):
        try:
            with open(ruta_archivo, mode='r', newline='', encoding='latin-1') as file:
                reader = csv.DictReader(file, delimiter=';') 
                if not reader.fieldnames or 'Receta' not in reader.fieldnames or \
                   'Categoria' not in reader.fieldnames or 'Ingredientes' not in reader.fieldnames:
                    raise ValueError("El archivo CSV debe contener las columnas 'Receta', 'Categoria', 'Ingredientes'.")

                for row in reader:
                    receta = row['Receta'].strip()
                    categoria = row['Categoria'].strip()
                    ingredientes_str = row['Ingredientes'].strip()
                    ingredientes = [ing.strip().lower() for ing in ingredientes_str.split(',') if ing.strip()]

                    if not receta: continue 

                    self.recetas_info[receta] = {
                        'categoria': categoria,
                        'ingredientes': ingredientes
                    }

                    self.grafo.add_node(receta, tipo='receta', categoria=categoria)
                    
                    if categoria and categoria not in self.grafo:
                        self.grafo.add_node(categoria, tipo='categoria')
                    if categoria: 
                        self.grafo.add_edge(receta, categoria, weight=1, relation='es_de_categoria')

                    for ingrediente in ingredientes:
                        self.ingredientes_conocidos.add(ingrediente)
                        self.grafo.add_node(ingrediente, tipo='ingrediente')
                        self.grafo.add_edge(ingrediente, receta, weight=1, relation='requiere_ingrediente')
            return True
        except FileNotFoundError:
            messagebox.showerror("Error de Archivo", f"No se encontró el archivo '{ruta_archivo}'. Asegúrate de que esté en la misma carpeta que el script.")
            return False
        except ValueError as ve:
            messagebox.showerror("Error de Datos", f"Error en el formato del archivo CSV: {ve}")
            return False
        except Exception as e:
            messagebox.showerror("Error de Carga", f"Error al procesar el archivo CSV: {e}")
            return False

    def buscar_recetas_compatibles_backtracking(self, ingredientes_disponibles_usuario, umbrales_por_categoria):
        recetas_sugeridas_por_categoria = {cat: [] for cat in CATEGORIAS_MENU}
        ingredientes_disponibles_set = set(ing.lower() for ing in ingredientes_disponibles_usuario)

        print("\n--- INICIANDO BÚSQUEDA CON BACKTRACKING ---")
        print(f"Ingredientes disponibles del usuario: {ingredientes_disponibles_set}")
        print(f"Umbrales mínimos de ingredientes por categoría: {umbrales_por_categoria}\n")

        for receta_nombre, info_receta in self.recetas_info.items():
            ingredientes_requeridos = info_receta['ingredientes']
            categoria_receta = info_receta['categoria']

            umbral_aplicar = umbrales_por_categoria.get(categoria_receta, umbrales_por_categoria['Default'])

            coincidencias = 0
            ingredientes_encontrados_en_receta = []
            
            for ing_req in ingredientes_requeridos:
                if ing_req in ingredientes_disponibles_set:
                    coincidencias += 1
                    ingredientes_encontrados_en_receta.append(ing_req)
            
            print(f"Evaluando Receta: '{receta_nombre}' (Categoría: {categoria_receta})")
            print(f"   Ingredientes requeridos: {ingredientes_requeridos}")
            print(f"   Ingredientes encontrados: {ingredientes_encontrados_en_receta} (Total: {coincidencias} de {len(ingredientes_requeridos)})")
            print(f"   Umbral para esta categoría ({categoria_receta}): {umbral_aplicar}")

            if coincidencias >= umbral_aplicar:
                if categoria_receta in recetas_sugeridas_por_categoria:
                    recetas_sugeridas_por_categoria[categoria_receta].append(receta_nombre)
                print(f"   --> ¡RECETA SUGERIDA! '{receta_nombre}' cumple con el umbral.")
            else:
                print(f"   --> RECETA DESCARTADA. '{receta_nombre}' no cumple con el umbral. (BACKTRACK)")
            print("-" * 50)

        print("\n--- BÚSQUEDA CON BACKTRACKING FINALIZADA ---")
        return recetas_sugeridas_por_categoria

    def generar_grafo_para_interfaz(self, ingredientes_disponibles_usuario, menu_a_graficar):
        
        if not menu_a_graficar:
            return None 

        G = nx.Graph() 
        ingredientes_disponibles_set = set(ing.lower() for ing in ingredientes_disponibles_usuario)
        
        node_colors = {}
        edge_colors = {}
        edge_widths = {}
        node_labels = {} 

        for receta_nombre in menu_a_graficar:
            if receta_nombre in self.recetas_info:
                G.add_node(f"REC_{receta_nombre}", tipo='receta')
                node_labels[f"REC_{receta_nombre}"] = receta_nombre
                node_colors[f"REC_{receta_nombre}"] = ESTILOS['node_recipe_color']

        for ing_disponible in ingredientes_disponibles_set:
            G.add_node(f"ING_{ing_disponible}", tipo='ingrediente')
            node_labels[f"ING_{ing_disponible}"] = ing_disponible.capitalize()
            node_colors[f"ING_{ing_disponible}"] = ESTILOS['node_ingredient_color']

        for receta_nombre in menu_a_graficar:
            if receta_nombre in self.recetas_info:
                info_receta = self.recetas_info[receta_nombre]
                rec_node = f"REC_{receta_nombre}"
                for ing_req in info_receta['ingredientes']:
                    ing_node = f"ING_{ing_req}"
                    
                    if ing_req in ingredientes_disponibles_set and G.has_node(ing_node) and G.has_node(rec_node):
                        G.add_edge(ing_node, rec_node)
                        edge_colors[(ing_node, rec_node)] = ESTILOS['edge_color'] 
                        edge_widths[(ing_node, rec_node)] = 1.5 
        
        nodes_to_remove = [node for node in G.nodes() if G.degree(node) == 0 and G.nodes[node]['tipo'] == 'ingrediente']
        G.remove_nodes_from(nodes_to_remove)
        
        node_labels = {n: node_labels[n] for n in G.nodes() if n in node_labels}
        node_colors = {n: node_colors[n] for n in G.nodes() if n in node_colors}

        final_node_colors = [node_colors.get(node, 'gray') for node in G.nodes()]
        final_edge_colors = [edge_colors.get((u, v), edge_colors.get((v, u), 'gray')) for u, v in G.edges()]
        final_edge_widths = [edge_widths.get((u, v), edge_widths.get((v, u), 1)) for u, v in G.edges()]

        fig = Figure(figsize=(8, 6), dpi=100, facecolor=ESTILOS['bg_frame']) 
        ax = fig.add_subplot(111) 
        ax.set_facecolor(ESTILOS['bg_frame']) 

        pos = nx.spring_layout(G, k=0.9, iterations=150, seed=42) 

        nx.draw_networkx_nodes(G, pos, ax=ax,
                               node_color=final_node_colors,
                               node_size=1200, 
                               alpha=0.9,
                               edgecolors='black', 
                               linewidths=0.8) 

        nx.draw_networkx_edges(G, pos, ax=ax, edge_color=final_edge_colors, width=final_edge_widths, alpha=0.7)
        
        nx.draw_networkx_labels(G, pos, ax=ax, labels=node_labels, font_size=7, font_weight='bold', font_color='black') 

        ax.axis('off') 
        fig.tight_layout()

        return fig 

    def obtener_ingredientes_compartidos_kruskal(self, menu_sugerido):
        if not menu_sugerido:
            return {}

        ingredientes_frecuencia = defaultdict(int)
    
        ingredientes_por_receta = defaultdict(list)

        for receta_nombre in menu_sugerido:
            if receta_nombre in self.recetas_info:
                for ingrediente in self.recetas_info[receta_nombre]['ingredientes']:
                    ingredientes_frecuencia[ingrediente] += 1
                    ingredientes_por_receta[ingrediente].append(receta_nombre)

        ingredientes_ordenados = sorted(ingredientes_frecuencia.items(), key=lambda item: item[1], reverse=True)

        ingredientes_comunes = {
            ing: {
                'frecuencia': freq,
                'recetas': ingredientes_por_receta[ing]
            }
            for ing, freq in ingredientes_ordenados if freq >= 2
        }
        return ingredientes_comunes

def generar_menus_completos(recetas_por_categoria, categorias_ordenadas):
    menus_finales = []

    def backtrack(menu_parcial, indice_categoria):
        if indice_categoria == len(categorias_ordenadas):
            menus_finales.append(list(menu_parcial))
            return

        categoria_actual = categorias_ordenadas[indice_categoria]
        if categoria_actual in recetas_por_categoria and recetas_por_categoria[categoria_actual]:
            for receta in recetas_por_categoria[categoria_actual]:
                menu_parcial.append(receta)
                backtrack(menu_parcial, indice_categoria + 1)
                menu_parcial.pop() 

    backtrack([], 0)
    return menus_finales

class GeneradorMenuApp:
    def __init__(self, root):
        self.root = root
        self.configurar_ventana()

        self.grafo_recetario = RecetarioGrafo()
        if not self.grafo_recetario.cargar_desde_csv(RUTA_ARCHIVO_RECETAS):
            self.root.after(100, self.root.destroy) 
            return

        self.canvas_grafo = None 
        self.toolbar_grafo = None 
        self.label_grafo_title = None 

        self.crear_widgets()

    def configurar_ventana(self):
        self.root.title("Generador de Menús con Grafos y Backtracking")
        self.root.geometry("1400x850") 
        self.root.configure(bg=ESTILOS['bg_main'])

    def crear_widgets(self):
        main_frame = tk.Frame(self.root, bg=ESTILOS['bg_main'], padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        frame_top = tk.Frame(main_frame, bg=ESTILOS['bg_frame'], padx=15, pady=15)
        frame_top.pack(fill=tk.X, pady=(0, 10))

        label_ingredientes = tk.Label(frame_top, text="Ingredientes disponibles (separados por comas):", 
                                             font=ESTILOS['font_label'], bg=ESTILOS['bg_frame'], fg=ESTILOS['fg_text'])
        label_ingredientes.pack(padx=5, pady=5, anchor='w')
        
        self.entry_ingredientes = tk.Entry(frame_top, width=100, font=ESTILOS['font_label'], bg=ESTILOS['entry_bg'], fg=ESTILOS['fg_text']) 
        self.entry_ingredientes.pack(padx=5, pady=5, fill=tk.X, expand=True)

        label_umbrales_info = tk.Label(frame_top, text=f"Umbrales mínimos de ingredientes por receta:\n"
                                                           f"Entrada, Segundo, Postre: {UMBRALES_MINIMOS_POR_CATEGORIA['Entrada']} ingredientes\n"
                                                           f"Bebida: {UMBRALES_MINIMOS_POR_CATEGORIA['Bebida']} ingredientes",
                                             font=ESTILOS['font_label'], bg=ESTILOS['bg_frame'], fg=ESTILOS['fg_text'], justify=tk.LEFT)
        label_umbrales_info.pack(pady=5, anchor='w', padx=5)

        self.btn_generar = tk.Button(frame_top, text="Generar Propuesta de Menú y Grafo", 
                                             font=ESTILOS['font_button'], bg=ESTILOS['button_bg'], fg=ESTILOS['button_fg'], 
                                             command=self.procesar_generacion_menu, relief=tk.FLAT, padx=10, pady=5)
        self.btn_generar.pack(pady=10)

        frame_bottom = tk.Frame(main_frame, bg=ESTILOS['bg_main'])
        frame_bottom.pack(fill=tk.BOTH, expand=True, pady=(10,0))

        frame_text_results = tk.Frame(frame_bottom, bg=ESTILOS['bg_frame'])
        frame_text_results.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10)) 

        label_text_results = tk.Label(frame_text_results, text="Resultados de Recetas y Menús:", 
                                             font=ESTILOS['font_title'], bg=ESTILOS['bg_frame'], fg=ESTILOS['fg_text'])
        label_text_results.pack(pady=(5,0))

        self.txt_resultados = scrolledtext.ScrolledText(frame_text_results, height=20, state='disabled', 
                                                         font=('Courier New', 9), bg=ESTILOS['text_area_bg'], fg=ESTILOS['fg_text']) 
        self.txt_resultados.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.frame_grafo = tk.Frame(frame_bottom, bg=ESTILOS['bg_frame'])
        self.frame_grafo.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.label_grafo_title = tk.Label(self.frame_grafo, text="Grafo del Primer Menú Sugerido:", 
                                             font=ESTILOS['font_title'], bg=ESTILOS['bg_frame'], fg=ESTILOS['fg_text'])
        self.label_grafo_title.pack(pady=(5,0))


    def _actualizar_texto(self, contenido):
        self.txt_resultados.config(state='normal')
        self.txt_resultados.delete("1.0", tk.END)
        self.txt_resultados.insert(tk.END, contenido)
        self.txt_resultados.config(state='disabled')

    def mostrar_grafo_en_interfaz(self, fig, menu_graficado=None):
        if self.canvas_grafo:
            self.canvas_grafo.get_tk_widget().destroy()
            self.canvas_grafo = None
        if self.toolbar_grafo:
            self.toolbar_grafo.destroy()
            self.toolbar_grafo = None

        if menu_graficado:
            menu_str = ', '.join(menu_graficado)
            self.label_grafo_title.config(text=f"Grafo del Menú Sugerido: {menu_str}", font=('Arial', 10, 'bold')) 
        else:
            self.label_grafo_title.config(text="Grafo del Primer Menú Sugerido:", font=ESTILOS['font_title']) 

        if fig:
            self.canvas_grafo = FigureCanvasTkAgg(fig, master=self.frame_grafo)
            self.canvas_grafo.draw()
            self.canvas_grafo.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)

            self.toolbar_grafo = NavigationToolbar2Tk(self.canvas_grafo, self.frame_grafo)
            self.toolbar_grafo.update()
            self.canvas_grafo.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        else:
            temp_label = tk.Label(self.frame_grafo, text="No se pudo generar un grafo de menú completo.", 
                                  font=ESTILOS['font_label'], bg=ESTILOS['bg_frame'], fg=ESTILOS['fg_text'])
            temp_label.pack(expand=True)
            self.frame_grafo.after(3000, temp_label.destroy)


    def procesar_generacion_menu(self):
        ingredientes_input_str = self.entry_ingredientes.get().strip()
        if not ingredientes_input_str:
            messagebox.showwarning("Entrada Vacía", "Por favor, ingresa al menos un ingrediente disponible.")
            self.mostrar_grafo_en_interfaz(None) 
            return
        
        lista_ingredientes_usuario = [ing.strip() for ing in ingredientes_input_str.split(',') if ing.strip()]
        
        recetas_compatibles_por_categoria = self.grafo_recetario.buscar_recetas_compatibles_backtracking(
            lista_ingredientes_usuario, UMBRALES_MINIMOS_POR_CATEGORIA
        )

        for categoria in CATEGORIAS_MENU:
            if categoria in recetas_compatibles_por_categoria:
                random.shuffle(recetas_compatibles_por_categoria[categoria])

        str_recetas_posibles = "--- RECETAS ALCANZABLES CON TUS INGREDIENTES ---\n"
        hay_recetas_compatibles = False
        for categoria in CATEGORIAS_MENU:
            str_recetas_posibles += f"\n[{categoria.upper()}]\n"
            if recetas_compatibles_por_categoria[categoria]:
                hay_recetas_compatibles = True
                for receta in recetas_compatibles_por_categoria[categoria]:
                    str_recetas_posibles += f"   - {receta}\n"
            else:
                str_recetas_posibles += "   (No se encontraron recetas compatibles en esta categoría)\n"
        
        if not hay_recetas_compatibles:
            str_recetas_posibles += "\nNo se encontró ninguna receta compatible con los ingredientes y los umbrales dados.\n"

        str_recetas_posibles += "\n" + "="*50 + "\n"

        menus_completos = generar_menus_completos(recetas_compatibles_por_categoria, CATEGORIAS_MENU)

        str_menus_sugeridos = "\n--- PROPUESTAS DE MENÚ COMPLETO ---\n\n"
        menu_para_grafo = None 

        if not menus_completos:
            str_menus_sugeridos += "No se pudo formar ningún menú completo con las recetas compatibles.\n"
            self.mostrar_grafo_en_interfaz(None, menu_graficado=[]) 
        else:
            random.shuffle(menus_completos) 

            menu_para_grafo = menus_completos[0] 

            str_menus_sugeridos += f"Se encontraron {len(menus_completos)} combinaciones posibles. Mostrando hasta 5 (aleatorias):\n"
            for i, menu in enumerate(menus_completos[:5], 1): 
                str_menus_sugeridos += f"\n--- Menú Sugerido #{i} ---\n"
                for j, categoria in enumerate(CATEGORIAS_MENU):
                    if j < len(menu):
                        str_menus_sugeridos += f"   - {categoria+':':<16} {menu[j]}\n"
                    else:
                        str_menus_sugeridos += f"   - {categoria+':':<16} (No disponible)\n"
            
            str_menus_sugeridos += "\n" + "="*50 + "\n"
            str_menus_sugeridos += "--- ANÁLISIS DE INGREDIENTES COMPARTIDOS EN EL MENÚ SUGERIDO #1 (Simulación Kruskal) ---\n"
            ingredientes_compartidos = self.grafo_recetario.obtener_ingredientes_compartidos_kruskal(menu_para_grafo)

            if ingredientes_compartidos:
                str_menus_sugeridos += "\nLos siguientes ingredientes se comparten entre múltiples recetas en el menú sugerido, ¡optimiza tu lista de compras!\n"
                for ingrediente, info in ingredientes_compartidos.items():
                    str_menus_sugeridos += f"   - **{ingrediente.capitalize()}**: aparece en {info['frecuencia']} recetas ({', '.join(info['recetas'])})\n"
            else:
                str_menus_sugeridos += "\nNo se encontraron ingredientes compartidos entre las recetas del menú sugerido.\n"
            str_menus_sugeridos += "\n" + "="*50 + "\n"

            fig_grafo = self.grafo_recetario.generar_grafo_para_interfaz(lista_ingredientes_usuario, menu_para_grafo)
            self.mostrar_grafo_en_interfaz(fig_grafo, menu_para_grafo) 

        self._actualizar_texto(str_recetas_posibles + str_menus_sugeridos)

if __name__ == "__main__":
    root = tk.Tk()
    app = GeneradorMenuApp(root)
    root.mainloop()