# sistema.py
import json
import os
from estructuras import NodoUnidad, NodoCarpeta, NodoArchivo, PilaLogs, ArbolB
from datetime import datetime

class SistemaArchivos:
    def __init__(self):
        # 1. Crear las unidades C, D, F
        self.unidad_c = NodoUnidad("C:")
        self.unidad_d = NodoUnidad("D:")
        self.unidad_f = NodoUnidad("F:")
        
        # Enlazarlas (C -> D -> F)
        self.unidad_c.siguiente = self.unidad_d
        self.unidad_d.siguiente = self.unidad_f
        
        # Punteros de navegación
        self.unidad_actual = self.unidad_c
        self.carpeta_actual = self.unidad_c.raiz_carpeta
        
        self.indice_global=ArbolB(t=3)
        self.logs = PilaLogs()

    def registrar_log(self, comando):
        fecha = datetime.now().strftime("%H:%M:%S")
        self.logs.push(f"[{fecha}] {comando}")

    # --- COMANDO CD (Navegación entre unidades y carpetas) ---
    def cd(self, ruta):
        # 1. Cambio de UNIDAD (Ej: "D:")
        if ruta.upper() in ["C:", "D:", "F:"]:
            temp = self.unidad_c
            while temp:
                if temp.letra == ruta.upper():
                    self.unidad_actual = temp
                    self.carpeta_actual = temp.raiz_carpeta
                    print(f"[Sistema] Cambiado a unidad {temp.letra}")
                    return
                temp = temp.siguiente
            return

        # 2. Regresar al padre (..)
        if ruta == "..":
            if self.carpeta_actual.padre:
                self.carpeta_actual = self.carpeta_actual.padre
            return

        # 3. Entrar a una carpeta (Busqueda en Árbol N-ario)
        # En "Primer Hijo - Siguiente Hermano", buscamos linealmente en los hijos
        hijo = self.carpeta_actual.hijo_carpeta
        encontrado = False
        while hijo:
            if hijo.nombre == ruta:
                self.carpeta_actual = hijo
                encontrado = True
                break
            hijo = hijo.siguiente_carpeta
        
        if not encontrado:
            print(f"[Error] No existe la carpeta '{ruta}'")

    # --- COMANDO MKDIR (Insertar en Árbol N-ario) ---
    def mkdir(self, nombre):
        nuevo = NodoCarpeta(nombre, padre=self.carpeta_actual)
        
        # Insertar al final de la lista de hermanos (hijos del actual)
        if not self.carpeta_actual.hijo_carpeta:
            self.carpeta_actual.hijo_carpeta = nuevo
        else:
            temp = self.carpeta_actual.hijo_carpeta
            while temp.siguiente_carpeta:
                temp = temp.siguiente_carpeta
            temp.siguiente_carpeta = nuevo
            
        print(f"Carpeta '{nombre}' creada en {self.carpeta_actual.nombre}")
        self.registrar_log(f"mkdir {nombre}")
        self.guardar_sistema() # Persistencia

    # --- COMANDO TYPE (Insertar en Árbol Binario) ---
    def type(self, nombre, contenido):
        nuevo_archivo = NodoArchivo(nombre, contenido)
        
        if self.carpeta_actual.raiz_archivos is None:
            self.carpeta_actual.raiz_archivos = nuevo_archivo
        else:
            self._insertar_binario(self.carpeta_actual.raiz_archivos, nuevo_archivo)
        
        ruta_full=f"{self.unidad_actual.letra}/{self.carpeta_actual.nombre}/{nombre}"
        tamano=len(contenido)
        self.indice_global.insertar(nombre,ruta_full,tamano)

        print(f"Archivo '{nombre}' creado.")
        self.registrar_log(f"type {nombre}")
        self.guardar_sistema()

    def index_dump(self):
        print("\n---INDICE GLOBAL (ARBOL B)---")
        self.indice_global.mostrar_indice()

    def _insertar_binario(self, raiz, nuevo):
        # Lógica de inserción recursiva (Alfabética)
        if nuevo.nombre < raiz.nombre:
            if raiz.izq is None:
                raiz.izq = nuevo
            else:
                self._insertar_binario(raiz.izq, nuevo)
        else:
            if raiz.der is None:
                raiz.der = nuevo
            else:
                self._insertar_binario(raiz.der, nuevo)

    # --- COMANDO DIR (Mostrar Carpetas + Archivos In-Order) ---
    def dir(self):
        print(f"\n--- Contenido de {self.unidad_actual.letra}\...\{self.carpeta_actual.nombre} ---")
        
        # 1. Listar Carpetas (Iterando hermanos)
        temp = self.carpeta_actual.hijo_carpeta
        while temp:
            print(f"[DIR]  {temp.nombre}")
            temp = temp.siguiente_carpeta
            
        # 2. Listar Archivos (Recorrido In-Orden del Árbol Binario)
        self._mostrar_inorden(self.carpeta_actual.raiz_archivos)

    def _mostrar_inorden(self, nodo):
        if nodo:
            self._mostrar_inorden(nodo.izq)
            print(f"[FILE] {nodo.nombre} ({nodo.tamano} bytes)")
            self._mostrar_inorden(nodo.der)

    # --- PERSISTENCIA (Simplificada para el ejemplo) ---
    # NOTA: Debes adaptar tu guardar/cargar antiguo para soportar estas nuevas estructuras.
    # Por ahora dejé el placeholder.
    def guardar_sistema(self):
        pass 
    
    def cargar_sistema(self):
        pass