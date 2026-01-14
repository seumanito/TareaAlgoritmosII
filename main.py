import cohere
from sistema import SistemaArchivos

# --- CONFIGURACIÓN IA ---
co = cohere.Client("8u0JnTzSNxLXBrbFwTPIvVuNS11orWR363AN8SqZ") 

def traducir_ia(texto_usuario):
    preamble = """
    Eres un traductor de comandos para un sistema operativo simulado.
    
    COMANDOS VALIDOS:
    - mkdir <nombre>            (Crear carpeta)
    - cd <ruta>                 (Moverse: "cd D:", "cd Fotos", "cd ..")
    - type <nombre> "<texto>"   (Crear archivo)
    - dir                       (Listar contenido)
    - log                       (Ver historial)
    - clear log                 (Borrar historial)
    
    EJEMPLOS:
    "Crea carpeta Tareas" -> mkdir Tareas
    "Cambia a la unidad D" -> cd D:
    "Entra a Documentos" -> cd Documentos
    "Regresa" -> cd ..
    
    Responde ÚNICAMENTE con el comando técnico. Si no es comando, responde: ninguno
    """

    try:
        response = co.chat(
            model="command-r-08-2024", 
            message=texto_usuario,
            preamble=preamble,
            temperature=0.0 
        )
        
        comando = response.text.strip()
        if "ninguno" in comando.lower(): return None
        return comando

    except Exception as e:
        print(f"Error IA: {e}")
        return None

def main():
    sistema = SistemaArchivos()
    sistema.cargar_sistema() 

    print("--- Sistema de Archivos de Árboles (Parcial V) ---")
    print("Unidades disponibles: C:, D:, F:")

    while True:
        # 1. Prompt Dinámico: Muestra Unidad + Carpeta
        # Ej: C:/Documentos> 
        ruta_actual = f"{sistema.unidad_actual.letra}/{sistema.carpeta_actual.nombre}"
        entrada = input(f"{ruta_actual}> ")
        
        if entrada.lower() == "salir":
            sistema.guardar_sistema()
            break
        
        primer_palabra=entrada.split()[0].lower()
        comandos_conocidos=["mkdir", "cd", "type", "rmdir", "dir", "log", "clear","index"]
        if  primer_palabra in comandos_conocidos:
            comando=entrada
        else:
            comando = traducir_ia(entrada)
        
        if comando is None:
            print("Chatbot: No entendí eso como una orden válida.")
            continue
            
        print(f"🤖 Comando: {comando}") 

        # 3. Ejecución
        partes = comando.split(" ", 1)
        accion = partes[0].lower()
        argumento = partes[1] if len(partes) > 1 else ""
        
        try:
            if accion == "mkdir":
                sistema.mkdir(argumento)
            
            elif accion == "cd":
                sistema.cd(argumento)
            
            elif accion == "dir":
                # Caso 1: DIR normal
                if not argumento:
                    sistema.dir()
                
                # Caso 2: DIR SEARCH
                elif argumento.startswith("search"):
                    parts = argumento.split()
                    # Ejemplo: ['search', '-file', 'test', '-range', '10-20']
                    
                    # A. Búsqueda por Rango (-file y -range)
                    if "-range" in parts and "-file" in parts:
                        try:
                            idx_file = parts.index("-file") + 1
                            idx_range = parts.index("-range") + 1
                            
                            nombre = parts[idx_file]
                            rango = parts[idx_range].split("-") # "10-20" -> ["10", "20"]
                            
                            sistema.dir_search_range(nombre, rango[0], rango[1])
                        except:
                            print("Error: Uso correcto -> dir search -file <nombre> -range <min>-<max>")

                    # B. Búsqueda solo Archivo (-file)
                    elif "-file" in parts:
                        try:
                            idx_file = parts.index("-file") + 1
                            nombre = parts[idx_file]
                            sistema.dir_search_file(nombre)
                        except:
                            print("Error: Falta el nombre del archivo.")

                    # C. Búsqueda de Carpeta (Sin flags raros, solo el nombre)
                    else:
                        # Lo que quede después de 'search' es el nombre
                        nombre_carpeta = argumento.replace("search", "").strip()
                        if nombre_carpeta:
                            sistema.dir_search_folder(nombre_carpeta)
                        else:
                            print("Error: Especifique nombre de carpeta.")
                
            elif accion == "type":
                # Lógica para separar nombre y contenido (Igual que antes)
                datos = argumento.split(" ", 1)
                nombre = datos[0]
                contenido = datos[1].strip('"') if len(datos) > 1 else ""
                sistema.type(nombre, contenido)
                
            elif accion == "log":
                sistema.logs.mostrar_historial()
                
            elif accion == "clear": # Para "clear log"
                sistema.logs.limpiar()
            
            elif accion == "index":
                # Si no hay argumentos, mostramos todo (Dump)
                if not argumento or argumento == "search": # Por si escribe solo "index search"
                    sistema.index_dump()
                
                # Si hay búsqueda
                elif argumento.startswith("search"):
                    parts = argumento.split()
                    # Ejemplo: ['search', '-file', 'test', '-range', '5-12']
                    
                    nombre_buscado = None
                    min_s = 0
                    max_s = float('inf')
                    
                    try:
                        # 1. Detectar filtro de Nombre (-file o directo)
                        if "-file" in parts:
                            idx = parts.index("-file") + 1
                            if idx < len(parts): nombre_buscado = parts[idx]
                        elif "-range" not in parts: 
                            # Si escribe "index search notas" (sin flags)
                            nombre_buscado = argumento.replace("search", "").strip()

                        # 2. Detectar filtro de Rango (-range)
                        if "-range" in parts:
                            idx = parts.index("-range") + 1
                            if idx < len(parts):
                                rango = parts[idx].split("-")
                                min_s = int(rango[0])
                                max_s = int(rango[1])

                        # Ejecutar la búsqueda global
                        sistema.index_search(nombre_buscado, min_s, max_s)
                        
                    except ValueError:
                        print("Error: El rango debe ser numérico (ej: -range 10-20)")
                    except Exception as e:
                        print(f"Error en sintaxis: {e}")
                
        except Exception as e:
            print(f"Error ejecutando comando: {e}")

if __name__ == "__main__":
    main()