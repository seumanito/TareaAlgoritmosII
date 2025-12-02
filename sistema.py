
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