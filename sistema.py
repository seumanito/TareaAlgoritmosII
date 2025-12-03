
import json
import os

from estructuras import Nodo, ColaHijos, PilaLogs
from datetime import datetime

class SistemaArchivos:
    def __init__(self):
        self.raiz = Nodo("C:", True, None)
        self.raiz.lista_hijos = ColaHijos() 
        
        self.actual = self.raiz  
        self.logs = PilaLogs()  

    def registrar_log(self, comando, estado="Exito"):
        fecha = datetime.now().strftime("%H:%M:%S")
        mensaje = f"[{fecha}] {comando} -> {estado}"
        self.logs.push(mensaje)

    def mkdir(self, nombre_carpeta):
       
        nuevo = Nodo(nombre_carpeta, True, self.actual)
        nuevo.lista_hijos = ColaHijos() 
        
        
        self.actual.lista_hijos.encolar(nuevo)
        
        self.registrar_log(f"mkdir {nombre_carpeta}")
        print(f"Carpeta '{nombre_carpeta}' creada en {self.actual.nombre}")

    def cd(self, ruta):
        if ruta == "..":
            if self.actual.padre:
                self.actual = self.actual.padre
            return

        nodo_destino = self.actual.lista_hijos.buscar(ruta)
        
        if nodo_destino and nodo_destino.es_carpeta:
            self.actual = nodo_destino
            self.registrar_log(f"cd {ruta}")
        else:
            print("Error: Directorio no encontrado")
            self.registrar_log(f"cd {ruta}", "Error")
            
    def dir(self):
        print(f"\nDirectorio de {self.actual.nombre}")
        temp = self.actual.lista_hijos.cabeza
        while temp:
            tipo = "<DIR>" if temp.es_carpeta else "<FILE>"
            print(f"{tipo}\t{temp.nombre}")
            temp = temp.siguiente

    def type(self, nombre_archivo, contenido_texto):

        nuevo_archivo = Nodo(nombre_archivo, False, self.actual)
        nuevo_archivo.contenido = contenido_texto

        self.actual.lista_hijos.encolar(nuevo_archivo)
        
        print(f"[Sistema] Archivo '{nombre_archivo}' creado exitosamente.")
        self.registrar_log(f"type {nombre_archivo}")

    def guardar_sistema(self):
        data = self._nodo_a_dict(self.raiz)
        
        with open("filesystem_backup.json", "w") as archivo:
            json.dump(data, archivo, indent=4)
        print("[Sistema] Copia de seguridad guardada.")

    def _nodo_a_dict(self, nodo):
        diccionario = {
            "nombre": nodo.nombre,
            "es_carpeta": nodo.es_carpeta,
            "contenido": nodo.contenido,
            "hijos": []
        }

        if nodo.es_carpeta and hasattr(nodo, 'lista_hijos'):
            temp = nodo.lista_hijos.cabeza 
            
            while temp:
                diccionario["hijos"].append(self._nodo_a_dict(temp))
                temp = temp.siguiente
        
        return diccionario
    
    def cargar_sistema(self):
        if not os.path.exists("filesystem_backup.json"):
            print("[Sistema] No se encontró respaldo previo. Iniciando desde cero.")
            return

        with open("filesystem_backup.json", "r") as archivo:
            data = json.load(archivo)
        
        # Reconstruimos la raíz
        self.raiz = self._dict_a_nodo(data, None)
        self.actual = self.raiz # Reiniciamos el puntero al inicio
        print("[Sistema] Sistema de archivos restaurado exitosamente.")

    def _dict_a_nodo(self, data, padre):
        
        
        nuevo_nodo = Nodo(data["nombre"], data["es_carpeta"], padre)
        nuevo_nodo.contenido = data.get("contenido", "")
        
       
        if nuevo_nodo.es_carpeta:
            
            nuevo_nodo.lista_hijos = ColaHijos() 

        
        for hijo_data in data["hijos"]:
            
            hijo_nodo = self._dict_a_nodo(hijo_data, nuevo_nodo)
            
            nuevo_nodo.lista_hijos.encolar(hijo_nodo)
        
        return nuevo_nodo   