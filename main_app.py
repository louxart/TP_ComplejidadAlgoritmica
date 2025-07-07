import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk  

from optimizar_uso_de_insumo import App as OptimizarInsumosInterface
from menu import GeneradorMenuApp as BacktrackingInterface
from proponer_recetas import ProponerRecetaApp as PropuestaInterface
from rutas import App as RutaRestauranteApp


class MainApplication(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Gestión de Recetas y Menús")
        self.geometry("900x600")
        self.configure(bg="#F5F5F5")

        self.create_ui()

    def create_ui(self):
    
        try:
            img = Image.open("banner.png")  
            img = img.resize((900, 150))
            self.banner_img = ImageTk.PhotoImage(img)
            banner = tk.Label(self, image=self.banner_img)
            banner.pack(pady=(10, 0))
        except Exception as e:
            print(f"[WARN] No se pudo cargar la imagen: {e}")

        
        title = tk.Label(self, text="Bienvenido al Sistema de Gestión de Recetas y Menús", font=("Arial", 16, "bold"), bg="#F5F5F5", fg="#333")
        title.pack(pady=10)

      
        button_frame = tk.Frame(self, bg="#F5F5F5")
        button_frame.pack(pady=30)

        btns = [
            ("Optimizar Uso de Insumos (DFS - MST)", '#1E90FF', self.open_dfs_mst_interface),
            ("Generar Menús (Backtracking)", '#4CAF50', self.open_backtracking_interface),
            ("Proponer Recetas (Topológico + CFC)", '#B39DDB', self.open_propuesta_interface),
            ("Ver restaurante más cercano", '#008000', self.open_rutas_interface),
        ]

        for i, (label, color, command) in enumerate(btns):
            btn = tk.Button(button_frame, text=label, font=('Arial', 11, 'bold'), bg=color,
                            fg='white', relief=tk.RAISED, padx=20, pady=12, width=35,
                            command=command)
            btn.grid(row=i, column=0, pady=10)

        
        footer = tk.Label(self, text="© 2025 Proyecto de Complejidad Algoritmica", bg="#F5F5F5", fg="#666", font=("Arial", 9))
        footer.pack(side=tk.BOTTOM, pady=10)

   
    def open_dfs_mst_interface(self):
        self._open_new_window("Optimizar Uso de Insumos", OptimizarInsumosInterface, "800x600")

    def open_backtracking_interface(self):
        self._open_new_window("Generar Menús con Backtracking", BacktrackingInterface, "1400x850")

    def open_propuesta_interface(self):
        self._open_new_window("Propuesta de Recetas", PropuestaInterface, "1000x700")

    def open_rutas_interface(self):
        self._open_new_window("Restaurante Más Cercano", RutaRestauranteApp, "900x700")

    def _open_new_window(self, title, interface_class, geometry):
        new_window = tk.Toplevel(self)
        new_window.title(title)
        try:
            interface_class(new_window)
            new_window.geometry(geometry)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar la interfaz: {e}")
            new_window.destroy()


if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()
