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

    # --- PERSISTENCIA: GUARDAR (Serialización de Árboles) ---
    def guardar_sistema(self):
        data = {
            "unidades": []
        }
        
        # 1. Recorremos las unidades (Lista Enlazada C -> D -> F)
        temp_unidad = self.unidad_c
        while temp_unidad:
            unidad_data = {
                "letra": temp_unidad.letra,
                "raiz_carpeta": self._carpeta_a_dict(temp_unidad.raiz_carpeta)
            }
            data["unidades"].append(unidad_data)
            temp_unidad = temp_unidad.siguiente
            
        with open("filesystem_backup.json", "w") as archivo:
            json.dump(data, archivo, indent=4)
        print("[Sistema] Copia de seguridad (Árboles) guardada.")

    def _carpeta_a_dict(self, nodo_carpeta):
        if not nodo_carpeta: return None
        
        diccionario = {
            "nombre": nodo_carpeta.nombre,
            "archivos": self._bst_a_lista(nodo_carpeta.raiz_archivos), # Guardamos archivos
            "subcarpetas": []
        }
        
        # Guardamos los hijos carpetas (Árbol N-ario: Recorrer hermanos)
        temp = nodo_carpeta.hijo_carpeta
        while temp:
            diccionario["subcarpetas"].append(self._carpeta_a_dict(temp))
            temp = temp.siguiente_carpeta
            
        return diccionario

    def _bst_a_lista(self, nodo_archivo):
        # Recorrido Pre-Orden para guardar archivos
        lista = []
        if nodo_archivo:
            lista.append({
                "nombre": nodo_archivo.nombre,
                "contenido": nodo_archivo.contenido,
                "tamano": nodo_archivo.tamano
            })
            lista.extend(self._bst_a_lista(nodo_archivo.izq))
            lista.extend(self._bst_a_lista(nodo_archivo.der))
        return lista
    
    # --- PERSISTENCIA: CARGAR (Reconstrucción) ---
    def cargar_sistema(self):
        if not os.path.exists("filesystem_backup.json"):
            print("[Sistema] No hay respaldo previo. Iniciando limpio.")
            return

        try:
            with open("filesystem_backup.json", "r") as archivo:
                data = json.load(archivo)

            # Reiniciamos el Índice Global para llenarlo de nuevo
            self.indice_global = ArbolB(t=3)

            # Reconstruimos cada unidad
            for unidad_data in data["unidades"]:
                letra = unidad_data["letra"]
                
                # Buscamos la unidad correspondiente en memoria
                unidad_obj = None
                temp = self.unidad_c
                while temp:
                    if temp.letra == letra:
                        unidad_obj = temp
                        break
                    temp = temp.siguiente
                
                if unidad_obj:
                    # Reconstruimos su árbol de carpetas
                    unidad_obj.raiz_carpeta = self._dict_a_carpeta(unidad_data["raiz_carpeta"], None, letra)
            
            # Restauramos punteros al inicio
            self.unidad_actual = self.unidad_c
            self.carpeta_actual = self.unidad_c.raiz_carpeta
            print("[Sistema] Árboles y B-Tree restaurados exitosamente.")

        except Exception as e:
            print(f"[Error Crítico] No se pudo cargar el respaldo: {e}")

    def _dict_a_carpeta(self, data, padre, letra_unidad):
        if not data: return None
        
        # 1. Crear el nodo carpeta
        nueva_carpeta = NodoCarpeta(data["nombre"], padre)
        
        # 2. Restaurar Archivos (y actualizar Índice Global)
        ruta_base = f"{letra_unidad}/{data['nombre']}" # Aproximación de ruta
        if padre: # Si tiene padre, tratamos de construir la ruta mejor (opcional)
             # Nota: Para rutas perfectas se requiere pasar la ruta del padre recursivamente
             pass

        for arch in data["archivos"]:
            # Insertar en Árbol Binario Local
            nuevo_archivo = NodoArchivo(arch["nombre"], arch["contenido"])
            if nueva_carpeta.raiz_archivos is None:
                nueva_carpeta.raiz_archivos = nuevo_archivo
            else:
                self._insertar_binario(nueva_carpeta.raiz_archivos, nuevo_archivo)
            
            # --- ¡RE-INDEXACIÓN AUTOMÁTICA! (Cumple requisito B-Tree) ---
            # Reconstruimos la ruta para el índice
            # Nota: Aquí simplificamos la ruta para que funcione al cargar
            ruta_full = f"{ruta_base}/{arch['nombre']}" 
            self.indice_global.insertar(arch["nombre"], ruta_full, arch["tamano"])

        # 3. Restaurar Subcarpetas (Recursividad para Árbol N-ario)
        ultimo_hijo = None
        for hijo_data in data["subcarpetas"]:
            hijo_nodo = self._dict_a_carpeta(hijo_data, nueva_carpeta, f"{ruta_base}")
            
            # Enlazar en la lista de hermanos
            if nueva_carpeta.hijo_carpeta is None:
                nueva_carpeta.hijo_carpeta = hijo_nodo
            else:
                ultimo_hijo.siguiente_carpeta = hijo_nodo
            
            ultimo_hijo = hijo_nodo # Avanzamos el puntero del último hermano
            
        return nueva_carpeta