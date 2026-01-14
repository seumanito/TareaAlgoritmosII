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
    def index_search(self, nombre=None, min_s=0, max_s=float('inf')):
        print(f"\n[Índice Global] Buscando: Nombre='{nombre if nombre else '*'}' | Tamaño={min_s}-{max_s} bytes")
        
        # Llamamos a la función nueva del Árbol B
        resultados = self.indice_global.buscar_avanzado(nombre,min_s,max_s)
        
        if not resultados:
            print("   No se encontraron coincidencias en ninguna unidad.")
        else:
            for i, arch in enumerate(resultados, 1):
                print(f"   {i}. {arch['ruta']} ({arch['tamano']} KB)")
        print("Operación completada.")

    # 1. BÚSQUEDA DE CARPETAS (POST-ORDEN)
    def dir_search_folder(self, nombre_buscado):
        print(f"\n[Buscando carpeta '{nombre_buscado}' en POST-ORDEN...]")
        encontrado = self._postorden_carpetas(self.unidad_actual.raiz_carpeta, nombre_buscado)
        if not encontrado:
            print("   No se encontró la carpeta.")

    def _postorden_carpetas(self, nodo_carpeta, buscado):
        if not nodo_carpeta: return False
        
        # 1. Primero recorremos los hijos (Post-Orden: Hijos -> Raíz)
        hijo = nodo_carpeta.hijo_carpeta
        while hijo:
            if self._postorden_carpetas(hijo, buscado):
                return True
            hijo = hijo.siguiente_carpeta
            
        # 2. Luego verificamos el nodo actual (Raíz)
        if nodo_carpeta.nombre == buscado:
            print(f"   ¡Encontrada! -> {self.unidad_actual.letra}/.../{nodo_carpeta.nombre}")
            # Aquí podrías listar su contenido si quisieras
            return True
        return False

    # 2. BÚSQUEDA DE ARCHIVOS (PRE-ORDEN)
    def dir_search_file(self, nombre_archivo):
        print(f"\n[Buscando archivo '{nombre_archivo}' en PRE-ORDEN...]")
        # Iniciamos la búsqueda recursiva desde la carpeta actual
        self._preorden_archivos(self.carpeta_actual, nombre_archivo)

    def _preorden_archivos(self, nodo_carpeta, buscado):
        if not nodo_carpeta: return

        # 1. Procesamos archivos de ESTA carpeta (Pre-Orden: Raíz -> Hijos)
        # (Aquí usamos un helper para buscar en el árbol binario de la carpeta)
        self._buscar_en_binario(nodo_carpeta.raiz_archivos, buscado)

        # 2. Luego vamos a las subcarpetas
        hijo = nodo_carpeta.hijo_carpeta
        while hijo:
            self._preorden_archivos(hijo, buscado)
            hijo = hijo.siguiente_carpeta

    def _buscar_en_binario(self, nodo_binario, buscado):
        # Recorrido simple del árbol binario de archivos
        if not nodo_binario: return
        if buscado.lower() in nodo_binario.nombre.lower(): # Coincidencia parcial
            print(f"   [FILE] {nodo_binario.nombre} ({nodo_binario.tamano} bytes)")
        
        self._buscar_en_binario(nodo_binario.izq, buscado)
        self._buscar_en_binario(nodo_binario.der, buscado)

    # 3. BÚSQUEDA POR RANGO (IN-ORDEN)
    def dir_search_range(self, nombre, min_size, max_size):
        print(f"\n[Buscando '{nombre}' entre {min_size}-{max_size} bytes en IN-ORDEN...]")
        self._inorden_archivos(self.carpeta_actual, nombre, int(min_size), int(max_size))

    def _inorden_archivos(self, nodo_carpeta, nombre, min_s, max_s):
        if not nodo_carpeta: return

        # 1. Buscar en el árbol binario de archivos (In-Orden: Izq -> Raíz -> Der)
        self._recorrer_bst_inorden_rango(nodo_carpeta.raiz_archivos, nombre, min_s, max_s)

        # 2. Recursividad a subcarpetas
        hijo = nodo_carpeta.hijo_carpeta
        while hijo:
            self._inorden_archivos(hijo, nombre, min_s, max_s)
            hijo = hijo.siguiente_carpeta

    def _recorrer_bst_inorden_rango(self, nodo, nombre, min_s, max_s):
        if not nodo: return
        
        # Izquierda
        self._recorrer_bst_inorden_rango(nodo.izq, nombre, min_s, max_s)
        
        # Raíz (Procesar)
        match_nombre = nombre.lower() in nodo.nombre.lower()
        match_tamano = min_s <= nodo.tamano <= max_s
        
        if match_nombre and match_tamano:
             print(f"   [MATCH] {nodo.nombre} ({nodo.tamano} bytes)")
        
        # Derecha
        self._recorrer_bst_inorden_rango(nodo.der, nombre, min_s, max_s)