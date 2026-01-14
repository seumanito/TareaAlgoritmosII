# estructuras.py

# 1. NODO PARA ARCHIVOS (Árbol Binario)
# Se ordenan por nombre: Menores a la izquierda, Mayores a la derecha
class NodoArchivo:
    def __init__(self, nombre, contenido=""):
        self.nombre = nombre
        self.contenido = contenido
        self.tamano = len(contenido) # Para el buscador por rango
        self.izq = None  # Hijo Izquierdo
        self.der = None  # Hijo Derecho

# 2. NODO PARA CARPETAS (Árbol N-ario)
# Usaremos la representación "Primer Hijo - Siguiente Hermano" para simular N-ario
class NodoCarpeta:
    def __init__(self, nombre, padre=None):
        self.nombre = nombre
        self.padre = padre
        
        # Estructura N-aria para SUB-CARPETAS (Lista enlazada de hermanos)
        self.hijo_carpeta = None      # Primer hijo carpeta
        self.siguiente_carpeta = None # Siguiente hermano carpeta
        
        # Estructura Binaria para ARCHIVOS (Raíz del árbol binario)
        self.raiz_archivos = None     # Aquí empieza el árbol de archivos de esta carpeta

# 3. NODO PARA UNIDADES (Lista Enlazada)
class NodoUnidad:
    def __init__(self, letra):
        self.letra = letra # Ej: "C:", "D:"
        self.raiz_carpeta = NodoCarpeta(letra) # Cada unidad tiene su carpeta raíz
        self.siguiente = None # Siguiente unidad (C -> D -> F)

# 4. PILA DE LOGS (Se mantiene igual, es útil)
class PilaLogs:
    def __init__(self):
        self.tope = None

    class NodoLog:
        def __init__(self, mensaje):
            self.mensaje = mensaje
            self.siguiente = None

    def push(self, mensaje):
        nuevo = self.NodoLog(mensaje)
        nuevo.siguiente = self.tope
        self.tope = nuevo
    
    def mostrar_historial(self):
        actual = self.tope
        print("--- Historial ---")
        while actual:
            print(f"> {actual.mensaje}")
            actual = actual.siguiente

    def limpiar(self):
        self.tope = None

# --- AGREGAR AL FINAL DE estructuras.py ---

class NodoB:
    def __init__(self, t, hoja=False):
        self.t = t              # Grado mínimo (define rango de claves)
        self.hoja = hoja        # True si es hoja, False si es nodo interno
        self.claves = []        # Lista de objetos (Metadata del archivo)
        self.hijos = []         # Lista de punteros a hijos

class ArbolB:
    def __init__(self, t=3):
        self.raiz = NodoB(t, True)
        self.t = t

    # Función principal de inserción
    def insertar(self, nombre, ruta, tamano):
        # Creamos el objeto de datos que guardaremos
        dato = {"nombre": nombre, "ruta": ruta, "tamano": tamano}
        
        raiz = self.raiz
        # Si la raíz está llena, el árbol crece hacia arriba
        if len(raiz.claves) == (2 * self.t) - 1:
            temp = NodoB(self.t, False)
            self.raiz = temp
            temp.hijos.insert(0, raiz)
            self._dividir_hijo(temp, 0)
            self._insertar_no_lleno(temp, dato)
        else:
            self._insertar_no_lleno(raiz, dato)

    # Inserción auxiliar en nodo no lleno
    def _insertar_no_lleno(self, x, k):
        i = len(x.claves) - 1
        
        if x.hoja:
            # Encontrar la posición correcta y desplazar
            while i >= 0 and k["nombre"] < x.claves[i]["nombre"]:
                i -= 1
            x.claves.insert(i + 1, k)
        else:
            # Encontrar el hijo correcto
            while i >= 0 and k["nombre"] < x.claves[i]["nombre"]:
                i -= 1
            i += 1
            
            # Si el hijo está lleno, dividirlo
            if len(x.hijos[i].claves) == (2 * self.t) - 1:
                self._dividir_hijo(x, i)
                if k["nombre"] > x.claves[i]["nombre"]:
                    i += 1
            self._insertar_no_lleno(x.hijos[i], k)

    def buscar_avanzado(self, filtro_nombre=None, min_s=0, max_s=float('inf'), nodo=None, resultados=None):
        """Busca archivos que cumplan con el nombre parcial y/o el rango de tamaño"""
        if nodo is None: nodo = self.raiz
        if resultados is None: resultados = []
        
        i = 0
        # Recorremos todas las claves del nodo actual
        while i < len(nodo.claves):
            # 1. Bajamos al hijo izquierdo antes de procesar la clave (Recorrido In-Orden)
            if not nodo.hoja:
                self.buscar_avanzado(filtro_nombre, min_s, max_s, nodo.hijos[i], resultados)
            
            # 2. Analizamos la clave actual
            archivo = nodo.claves[i]
            
            # Verificamos Nombre (si pidieron filtro)
            match_nombre = True
            if filtro_nombre:
                if filtro_nombre.lower() not in archivo["nombre"].lower():
                    match_nombre = False
            
            # Verificamos Tamaño
            match_tamano = min_s <= archivo["tamano"] <= max_s
            
            # Si cumple TODO, lo guardamos
            if match_nombre and match_tamano:
                resultados.append(archivo)
                
            i += 1
            
        # 3. Bajamos al último hijo (el de más a la derecha)
        if not nodo.hoja:
            self.buscar_avanzado(filtro_nombre, min_s, max_s, nodo.hijos[i], resultados)
            
        return resultados
    # División de nodo (La magia del Árbol B)
    def _dividir_hijo(self, x, i):
        t = self.t
        y = x.hijos[i]
        z = NodoB(t, y.hoja)
        
        # Mover claves y hijos de Y a Z
        x.hijos.insert(i + 1, z)
        x.claves.insert(i, y.claves[t - 1])
        
        z.claves = y.claves[t:(2 * t) - 1]
        y.claves = y.claves[0:t - 1]
        
        if not y.hoja:
            z.hijos = y.hijos[t:(2 * t)]
            y.hijos = y.hijos[0:t]

    # Búsqueda simple (para probar)
    def buscar(self, nombre, nodo=None):
        if nodo is None:
            nodo = self.raiz
            
        i = 0
        while i < len(nodo.claves) and nombre > nodo.claves[i]["nombre"]:
            i += 1
            
        if i < len(nodo.claves) and nombre == nodo.claves[i]["nombre"]:
            return nodo.claves[i] # Encontrado
        
        if nodo.hoja:
            return None # No está
            
        return self.buscar(nombre, nodo.hijos[i])

    # Mostrar contenido (In-Orden)
    def mostrar_indice(self, nodo=None):
        if nodo is None: nodo = self.raiz
        i = 0
        for i in range(len(nodo.claves)):
            if not nodo.hoja:
                self.mostrar_indice(nodo.hijos[i])
            c = nodo.claves[i]
            print(f"[INDEX] {c['nombre']} - {c['ruta']} ({c['tamano']} bytes)")
        if not nodo.hoja:
            self.mostrar_indice(nodo.hijos[i + 1])