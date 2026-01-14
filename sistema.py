# sistema.py
import json
import os
from estructuras import NodoUnidad, NodoCarpeta, NodoArchivo, PilaLogs, ArbolB
from datetime import datetime

class SistemaArchivos:
    def __init__(self):
        self.unidad_c = NodoUnidad("C:")
        self.unidad_d = NodoUnidad("D:")
        self.unidad_f = NodoUnidad("F:")

        self.unidad_c.siguiente=self.unidad_d
        self.unidad_d.siguiente=self.unidad_f
        
        self.unidad_actual=self.unidad_c
        self.carpeta_actual=self.unidad_c.raiz_carpeta
        
        self.indice_global=ArbolB(t=3)
        self.logs=PilaLogs()

    def registrar_log(self, comando):
        fecha=datetime.now().strftime("%H:%M:%S")
        self.logs.push(f"[{fecha}] {comando}")

    def cd(self, ruta):
        if ruta.upper() in ["C:", "D:", "F:"]:
            temp=self.unidad_c
            while temp:
                if temp.letra==ruta.upper():
                    self.unidad_actual=temp
                    self.carpeta_actual=temp.raiz_carpeta
                    print(f"[Sistema] Cambiado a unidad {temp.letra}")
                    return
                temp=temp.siguiente
            return

        if ruta=="..":
            if self.carpeta_actual.padre:
                self.carpeta_actual=self.carpeta_actual.padre
            return

        hijo=self.carpeta_actual.hijo_carpeta
        encontrado=False
        while hijo:
            if hijo.nombre==ruta:
                self.carpeta_actual=hijo
                encontrado=True
                break
            hijo=hijo.siguiente_carpeta
        
        if not encontrado:
            print(f"[Error] No existe la carpeta '{ruta}'")

    def mkdir(self, nombre):
        nuevo=NodoCarpeta(nombre, padre=self.carpeta_actual)
        
        if not self.carpeta_actual.hijo_carpeta:
            self.carpeta_actual.hijo_carpeta=nuevo
        else:
            temp=self.carpeta_actual.hijo_carpeta
            while temp.siguiente_carpeta:
                temp=temp.siguiente_carpeta
            temp.siguiente_carpeta=nuevo
            
        print(f"Carpeta '{nombre}' creada en {self.carpeta_actual.nombre}")
        self.registrar_log(f"mkdir {nombre}")
        self.guardar_sistema()

    def type(self, nombre, contenido):
        nuevo_archivo=NodoArchivo(nombre, contenido)
        
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
        if nuevo.nombre<raiz.nombre:
            if raiz.izq is None:
                raiz.izq=nuevo
            else:
                self._insertar_binario(raiz.izq, nuevo)
        else:
            if raiz.der is None:
                raiz.der=nuevo
            else:
                self._insertar_binario(raiz.der, nuevo)

    def dir(self):
        print(f"\n--- Contenido de {self.unidad_actual.letra}\...\{self.carpeta_actual.nombre} ---")
        
        temp = self.carpeta_actual.hijo_carpeta
        while temp:
            print(f"[DIR]  {temp.nombre}")
            temp=temp.siguiente_carpeta
            
        self._mostrar_inorden(self.carpeta_actual.raiz_archivos)

    def _mostrar_inorden(self, nodo):
        if nodo:
            self._mostrar_inorden(nodo.izq)
            print(f"[FILE] {nodo.nombre} ({nodo.tamano} bytes)")
            self._mostrar_inorden(nodo.der)

    def guardar_sistema(self):
        data = {
            "unidades": []
        }
        
        temp_unidad = self.unidad_c
        while temp_unidad:
            unidad_data={
                "letra": temp_unidad.letra,
                "raiz_carpeta": self._carpeta_a_dict(temp_unidad.raiz_carpeta)
            }
            data["unidades"].append(unidad_data)
            temp_unidad=temp_unidad.siguiente
            
        with open("filesystem_backup.json", "w") as archivo:
            json.dump(data, archivo, indent=4)
        print("[Sistema] Copia de seguridad (Árboles) guardada.")

    def _carpeta_a_dict(self, nodo_carpeta):
        if not nodo_carpeta: return None
        
        diccionario = {
            "nombre": nodo_carpeta.nombre,
            "archivos": self._bst_a_lista(nodo_carpeta.raiz_archivos),
            "subcarpetas": []
        }
    
        temp=nodo_carpeta.hijo_carpeta
        while temp:
            diccionario["subcarpetas"].append(self._carpeta_a_dict(temp))
            temp=temp.siguiente_carpeta
            
        return diccionario

    def _bst_a_lista(self, nodo_archivo):
        lista=[]
        if nodo_archivo:
            lista.append({
                "nombre": nodo_archivo.nombre,
                "contenido": nodo_archivo.contenido,
                "tamano": nodo_archivo.tamano
            })
            lista.extend(self._bst_a_lista(nodo_archivo.izq))
            lista.extend(self._bst_a_lista(nodo_archivo.der))
        return lista
    
    
    def cargar_sistema(self):
        if not os.path.exists("filesystem_backup.json"):
            print("[Sistema] No hay respaldo previo. Iniciando limpio.")
            return

        try:
            with open("filesystem_backup.json", "r") as archivo:
                data=json.load(archivo)

            self.indice_global = ArbolB(t=3)

            for unidad_data in data["unidades"]:
                letra = unidad_data["letra"]
                
                unidad_obj=None
                temp=self.unidad_c
                while temp:
                    if temp.letra==letra:
                        unidad_obj=temp
                        break
                    temp=temp.siguiente
                
                if unidad_obj:
                    unidad_obj.raiz_carpeta = self._dict_a_carpeta(unidad_data["raiz_carpeta"], None, letra)
            
            self.unidad_actual = self.unidad_c
            self.carpeta_actual = self.unidad_c.raiz_carpeta
            print("[Sistema] Árboles y B-Tree restaurados exitosamente.")

        except Exception as e:
            print(f"[Error Crítico] No se pudo cargar el respaldo: {e}")

    def _dict_a_carpeta(self, data, padre, letra_unidad):
        if not data: return None
        
        nueva_carpeta = NodoCarpeta(data["nombre"], padre)
        
        ruta_base = f"{letra_unidad}/{data['nombre']}" 
        if padre: 
             pass

        for arch in data["archivos"]:
            nuevo_archivo = NodoArchivo(arch["nombre"], arch["contenido"])
            if nueva_carpeta.raiz_archivos is None:
                nueva_carpeta.raiz_archivos=nuevo_archivo
            else:
                self._insertar_binario(nueva_carpeta.raiz_archivos, nuevo_archivo)
            
            ruta_full = f"{ruta_base}/{arch['nombre']}" 
            self.indice_global.insertar(arch["nombre"], ruta_full, arch["tamano"])

        ultimo_hijo = None
        for hijo_data in data["subcarpetas"]:
            hijo_nodo = self._dict_a_carpeta(hijo_data, nueva_carpeta, f"{ruta_base}")
            
            if nueva_carpeta.hijo_carpeta is None:
                nueva_carpeta.hijo_carpeta = hijo_nodo
            else:
                ultimo_hijo.siguiente_carpeta = hijo_nodo
            
            ultimo_hijo = hijo_nodo 
            
        return nueva_carpeta
    def index_search(self, nombre=None, min_s=0, max_s=float('inf')):
        print(f"\n[Índice Global] Buscando: Nombre='{nombre if nombre else '*'}' | Tamaño={min_s}-{max_s} bytes")
        
        resultados=self.indice_global.buscar_avanzado(nombre,min_s,max_s)
        
        if not resultados:
            print("   No se encontraron coincidencias en ninguna unidad.")
        else:
            for i, arch in enumerate(resultados, 1):
                print(f"   {i}. {arch['ruta']} ({arch['tamano']} KB)")
        print("Operación completada.")

    def dir_search_folder(self, nombre_buscado):
        print(f"\n[Buscando carpeta '{nombre_buscado}' en POST-ORDEN...]")
        encontrado = self._postorden_carpetas(self.unidad_actual.raiz_carpeta, nombre_buscado)
        if not encontrado:
            print("   No se encontró la carpeta.")

    def _postorden_carpetas(self, nodo_carpeta, buscado):
        if not nodo_carpeta: return False
        
        hijo = nodo_carpeta.hijo_carpeta
        while hijo:
            if self._postorden_carpetas(hijo, buscado):
                return True
            hijo=hijo.siguiente_carpeta
            
        if nodo_carpeta.nombre == buscado:
            print(f"   ¡Encontrada! -> {self.unidad_actual.letra}/.../{nodo_carpeta.nombre}")
            return True
        return False

    def dir_search_file(self, nombre_archivo):
        print(f"\n[Buscando archivo '{nombre_archivo}' en PRE-ORDEN...]")
        self._preorden_archivos(self.carpeta_actual, nombre_archivo)

    def _preorden_archivos(self, nodo_carpeta, buscado):
        if not nodo_carpeta: return

        self._buscar_en_binario(nodo_carpeta.raiz_archivos, buscado)

        hijo = nodo_carpeta.hijo_carpeta
        while hijo:
            self._preorden_archivos(hijo, buscado)
            hijo = hijo.siguiente_carpeta

    def _buscar_en_binario(self, nodo_binario, buscado):
        if not nodo_binario: return
        if buscado.lower() in nodo_binario.nombre.lower(): 
            print(f"   [FILE] {nodo_binario.nombre} ({nodo_binario.tamano} bytes)")
        
        self._buscar_en_binario(nodo_binario.izq, buscado)
        self._buscar_en_binario(nodo_binario.der, buscado)

    
    def dir_search_range(self, nombre, min_size, max_size):
        print(f"\n[Buscando '{nombre}' entre {min_size}-{max_size} bytes en IN-ORDEN...]")
        self._inorden_archivos(self.carpeta_actual, nombre, int(min_size), int(max_size))

    def _inorden_archivos(self, nodo_carpeta, nombre, min_s, max_s):
        if not nodo_carpeta: return

        self._recorrer_bst_inorden_rango(nodo_carpeta.raiz_archivos, nombre, min_s, max_s)

        hijo=nodo_carpeta.hijo_carpeta
        while hijo:
            self._inorden_archivos(hijo, nombre, min_s, max_s)
            hijo=hijo.siguiente_carpeta

    def _recorrer_bst_inorden_rango(self, nodo, nombre, min_s, max_s):
        if not nodo: return
        
        self._recorrer_bst_inorden_rango(nodo.izq, nombre, min_s, max_s)
        
        match_nombre=nombre.lower() in nodo.nombre.lower()
        match_tamano=min_s <= nodo.tamano <= max_s
        
        if match_nombre and match_tamano:
             print(f"   [MATCH] {nodo.nombre} ({nodo.tamano} bytes)")
        
        self._recorrer_bst_inorden_rango(nodo.der, nombre, min_s, max_s)