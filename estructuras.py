

class Nodo:
    def __init__(self, nombre, es_carpeta, padre=None):
        self.nombre = nombre
        self.es_carpeta = es_carpeta  # True si es carpeta, False si es archivo
        self.padre = padre            # Puntero al directorio anterior (para cd ..)
        self.contenido = ""           # Para el comando TYPE
        self.siguiente = None         # Puntero al siguiente nodo (Lista Enlazada)
        
        # Punteros para manejar los hijos como una COLA (Queue)
        self.hijos_cabeza = None      # Primer hijo
        self.hijos_cola = None        # Último hijo

class ColaHijos:
    def __init__(self):
        self.cabeza = None
        self.cola = None

    def encolar(self, nuevo_nodo):
        #Agrega un archivo/carpeta al final de la lista
        if self.cabeza is None:
            self.cabeza = nuevo_nodo
            self.cola = nuevo_nodo
        else:
            self.cola.siguiente = nuevo_nodo
            self.cola = nuevo_nodo

    def buscar(self, nombre):
        #Busca un nodo por nombre en la lista enlazada
        actual = self.cabeza
        while actual:
            if actual.nombre == nombre:
                return actual
            actual = actual.siguiente
        return None
    

class PilaLogs:
    def __init__(self):
        self.tope = None # El elemento de más arriba

    def push(self, mensaje):
        """Agrega un log al tope"""
        nuevo_log = Nodo("Log", False) # Reutilizamos Nodo o creamos uno simple
        nuevo_log.contenido = mensaje
        
        if self.tope is None:
            self.tope = nuevo_log
        else:
            nuevo_log.siguiente = self.tope
            self.tope = nuevo_log
    
    def mostrar_historial(self):
        actual = self.tope
        print("--- Historial (LIFO) ---")
        while actual:
            print(f"> {actual.contenido}")
            actual = actual.siguiente
    
    def limpiar(self):
        self.tope = None
        print("--- Historial de logs eliminado ---")