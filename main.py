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
                sistema.dir()
            
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
            
            elif accion =="index":
                sistema.index_dump()
                
        except Exception as e:
            print(f"Error ejecutando comando: {e}")

if __name__ == "__main__":
    main()