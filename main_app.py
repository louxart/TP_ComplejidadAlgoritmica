#Archivo principal
import tkinter as tk
from tkinter import messagebox
from optimizar_uso_de_insumo import App as OptimizarInsumosInterface 
from menu import GeneradorMenuApp as BacktrackingInterface
from proponer_recetas import ProponerRecetaApp as PropuestaInterface

class MainApplication(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Gestión de Recetas y Menús")
        self.geometry("600x200")
        self.configure(bg="#FFFFFF")

        self.create_main_menu()

    def create_main_menu(self):
        button_frame = tk.Frame(self, bg="#FFFFFF")
        button_frame.pack(expand=True)

        btn_dfs_mst = tk.Button(button_frame,
                                text="Optimizar Uso de Insumos (DFS - MST)",
                                font=('Arial', 10, 'bold'),
                                bg='#1E90FF',
                                fg='white',
                                relief=tk.FLAT,
                                padx=15,
                                pady=10,
                                command=self.open_dfs_mst_interface)
        btn_dfs_mst.pack(side=tk.LEFT, padx=10, pady=20)

        btn_backtracking = tk.Button(button_frame,
                                      text="Generar Menús (Backtracking)",
                                      font=('Arial', 10, 'bold'),
                                      bg='#4CAF50',
                                      fg='white',
                                      relief=tk.FLAT,
                                      padx=15,
                                      pady=10,
                                      command=self.open_backtracking_interface)
        btn_backtracking.pack(side=tk.LEFT, padx=10, pady=20)


        btn_propuesta = tk.Button(button_frame,
                                text="Proponer Recetas (Greedy + CFC)",
                                font=('Arial', 10, 'bold'),
                                bg='#FFA500',
                                fg='white',
                                relief=tk.FLAT,
                                padx=15,
                                pady=10,
                                command=self.open_propuesta_interface)
        btn_propuesta.pack(side=tk.LEFT, padx=10, pady=20)

        btn_exit = tk.Button(button_frame,
                              text="X",
                              font=('Arial', 10, 'bold'),
                              bg='green',
                              fg='white',
                              relief=tk.FLAT,
                              padx=15,
                              pady=10,
                              command=self.quit_application)
        btn_exit.pack(side=tk.LEFT, padx=10, pady=20)

    def open_dfs_mst_interface(self):
        new_window = tk.Toplevel(self)
        new_window.title("Optimizar Uso de Insumos")
        try:
            # Instancia la clase de la interfaz DFS-MST
            # Asegúrate que la clase en optimizar_uso_insumos.py sea OptimizarInsumosInterface
            OptimizarInsumosInterface(new_window) # <<-- Instanciación clave aquí
            new_window.geometry("800x600") # Establece un tamaño para la nueva ventana
        except Exception as e:
            messagebox.showerror("Error al Abrir Interfaz", f"No se pudo cargar la interfaz de Optimización de Insumos: {e}")
            new_window.destroy()

    def open_backtracking_interface(self):
        new_window = tk.Toplevel(self)
        new_window.title("Generar Menús con Backtracking")
        try:
            BacktrackingInterface(new_window)
            new_window.geometry("1400x850")
        except Exception as e:
            messagebox.showerror("Error al Abrir Interfaz", f"No se pudo cargar la interfaz de Backtracking: {e}")
            new_window.destroy()
    def open_propuesta_interface(self):
        new_window = tk.Toplevel(self)
        new_window.title("Propuesta de Recetas")
        try:
            PropuestaInterface(new_window)
            new_window.geometry("1000x700")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar la interfaz de propuesta de recetas: {e}")
            new_window.destroy()


    def quit_application(self):
        if messagebox.askyesno("Salir", "¿Estás seguro de que quieres salir de la aplicación?"):
            self.destroy()

if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()